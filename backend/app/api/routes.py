from fastapi import APIRouter, Depends, HTTPException, Response, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.angel_one import AngelOneClient
from app.config.settings import Settings, get_settings
from app.database.session import get_db
from app.models.entities import IndexSymbol, Order, Position, PositionStatus, Trade, TradeMode
from app.schemas.trading import (
    BacktestRequest,
    BacktestResult,
    Candle,
    DashboardSummary,
    LoginRequest,
    OrderRead,
    PositionRead,
    StrategySettings,
    TokenResponse,
    TradeRead,
    UserCreate,
)
from app.services.auth import AuthService
from app.services.backtesting import BacktestingService
from app.services.market_data import MarketDataService
from app.services.reports import ReportService
from app.services.strategy_runner import StrategyRunner
from app.websocket.manager import manager


router = APIRouter()
runtime_settings = StrategySettings()


@router.post("/auth/register", response_model=TokenResponse)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db), settings: Settings = Depends(get_settings)) -> TokenResponse:
    service = AuthService(db, settings)
    user = await service.create_user(payload)
    return TokenResponse(access_token=service.create_access_token(user))


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db), settings: Settings = Depends(get_settings)) -> TokenResponse:
    service = AuthService(db, settings)
    user = await service.authenticate(str(payload.email), payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=service.create_access_token(user))


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(db: AsyncSession = Depends(get_db), settings: Settings = Depends(get_settings)) -> DashboardSummary:
    open_positions = await db.scalar(select(func.count(Position.id)).where(Position.status == PositionStatus.OPEN))
    total_pnl = await db.scalar(select(func.coalesce(func.sum(Trade.pnl), 0)))
    wins = await db.scalar(select(func.count(Trade.id)).where(Trade.pnl > 0))
    total_trades = await db.scalar(select(func.count(Trade.id)))
    trades_taken: dict[IndexSymbol, int] = {}
    for symbol in IndexSymbol:
        trades_taken[symbol] = int(await db.scalar(select(func.count(Trade.id)).where(Trade.symbol == symbol)) or 0)
    return DashboardSummary(
        mode=runtime_settings.mode,
        strategy_enabled=runtime_settings.enabled,
        live_pnl=float(total_pnl or 0),
        day_pnl=float(total_pnl or 0),
        win_rate=(float(wins or 0) / float(total_trades or 1)) * 100,
        active_positions=int(open_positions or 0),
        trades_taken=trades_taken,
    )


@router.get("/positions", response_model=list[PositionRead])
async def positions(db: AsyncSession = Depends(get_db)) -> list[PositionRead]:
    result = await db.execute(select(Position).order_by(Position.created_at.desc()))
    return [PositionRead.model_validate(row) for row in result.scalars()]


@router.get("/trades", response_model=list[TradeRead])
async def trades(db: AsyncSession = Depends(get_db)) -> list[TradeRead]:
    result = await db.execute(select(Trade).order_by(Trade.created_at.desc()).limit(250))
    return [TradeRead.model_validate(row) for row in result.scalars()]


@router.get("/orders", response_model=list[OrderRead])
async def orders(db: AsyncSession = Depends(get_db)) -> list[OrderRead]:
    result = await db.execute(select(Order).order_by(Order.created_at.desc()).limit(250))
    return [OrderRead.model_validate(row) for row in result.scalars()]


@router.post("/market-data/candles", response_model=Candle)
async def add_candle(payload: Candle, db: AsyncSession = Depends(get_db)) -> Candle:
    await MarketDataService(db).upsert_candle(payload)
    await manager.broadcast("candle_update", payload.model_dump(mode="json"))
    return payload


@router.get("/market-data/{symbol}/{timeframe}", response_model=list[Candle])
async def market_data(symbol: IndexSymbol, timeframe: str, db: AsyncSession = Depends(get_db)) -> list[Candle]:
    return await MarketDataService(db).recent_candles(symbol, timeframe)


@router.put("/strategy/settings", response_model=StrategySettings)
async def update_strategy_settings(payload: StrategySettings) -> StrategySettings:
    global runtime_settings
    runtime_settings = payload
    await manager.broadcast("strategy_status", payload.model_dump(mode="json"))
    return runtime_settings


@router.post("/strategy/run-on-candles")
async def run_strategy(symbol: IndexSymbol, db: AsyncSession = Depends(get_db), settings: Settings = Depends(get_settings)) -> dict[str, str]:
    service = MarketDataService(db)
    runner = StrategyRunner(db, settings, broker=AngelOneClient(settings) if runtime_settings.mode == TradeMode.LIVE else None)
    await runner.set_status(runtime_settings.enabled, runtime_settings.mode)
    await runner.on_candles(await service.recent_candles(symbol, "3m"), await service.recent_candles(symbol, "15m"))
    return {"status": "processed"}


@router.post("/backtests", response_model=BacktestResult)
async def backtest(payload: BacktestRequest) -> BacktestResult:
    return BacktestingService().run(payload)


@router.get("/reports/trades.csv")
async def export_trades(db: AsyncSession = Depends(get_db)) -> Response:
    csv_data = await ReportService(db).trades_csv()
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=trades.csv"})


@router.websocket("/ws")
async def dashboard_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
