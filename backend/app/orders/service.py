from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.base import BrokerClient
from app.models.entities import Order, OrderStatus, Position, PositionStatus, Signal, Trade, TradeMode
from app.schemas.trading import OrderRequest, OrderRead
from app.services.alerts import AlertService
from app.websocket.manager import manager


class OrderService:
    def __init__(self, db: AsyncSession, broker: BrokerClient | None, alerts: AlertService):
        self.db = db
        self.broker = broker
        self.alerts = alerts

    async def execute_entry(self, request: OrderRequest) -> OrderRead:
        signal_model = Signal(
            symbol=request.signal.symbol,
            side=request.signal.side,
            strategy_name="intraday_momentum_breakout",
            candle_time=request.signal.candle_time,
            entry_price=request.signal.entry_price,
            strike=request.signal.strike,
            expiry=request.signal.expiry,
            reason=request.signal.reason,
            metadata_json={"indicators": request.signal.indicators.model_dump()},
        )
        self.db.add(signal_model)
        await self.db.flush()

        order = Order(
            signal_id=signal_model.id,
            mode=request.mode,
            symbol=request.signal.symbol,
            option_symbol=request.option_symbol,
            quantity=request.quantity,
            price=request.price,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()

        if request.mode == TradeMode.LIVE:
            if not self.broker:
                raise RuntimeError("Live broker is not configured")
            broker_order = await self.broker.place_market_order(request.option_symbol, "BUY", request.quantity)
            order.broker_order_id = broker_order.broker_order_id
            order.raw_response = broker_order.raw
            order.status = OrderStatus.PLACED
        else:
            order.broker_order_id = f"PAPER-{order.id}"
            order.status = OrderStatus.FILLED
            order.raw_response = {"simulated": True}

        trade = Trade(
            order_id=order.id,
            mode=request.mode,
            symbol=request.signal.symbol,
            option_symbol=request.option_symbol,
            quantity=request.quantity,
            entry_price=request.price,
            status=PositionStatus.OPEN,
        )
        self.db.add(trade)
        await self.db.flush()

        position = Position(
            trade_id=trade.id,
            symbol=request.signal.symbol,
            option_symbol=request.option_symbol,
            quantity=request.quantity,
            average_price=request.price,
            last_price=request.price,
            unrealized_pnl=0,
            status=PositionStatus.OPEN,
        )
        self.db.add(position)
        await self.db.commit()
        await self.db.refresh(order)

        payload = OrderRead.model_validate(order).model_dump(mode="json")
        await manager.broadcast("order_update", payload)
        await self.alerts.trade_alert(f"{request.mode.value.upper()} BUY {request.option_symbol} x {request.quantity} @ {request.price}")
        return OrderRead.model_validate(order)

    async def mark_to_market(self, option_symbol: str, last_price: float) -> None:
        result = await self.db.execute(select(Position).where(Position.option_symbol == option_symbol, Position.status == PositionStatus.OPEN))
        positions = result.scalars().all()
        for position in positions:
            position.last_price = last_price
            position.unrealized_pnl = (last_price - position.average_price) * position.quantity
            await manager.broadcast(
                "pnl_update",
                {
                    "position_id": position.id,
                    "option_symbol": position.option_symbol,
                    "last_price": last_price,
                    "unrealized_pnl": position.unrealized_pnl,
                },
            )
        await self.db.commit()

    async def exit_position(self, position: Position, exit_price: float, reason: str) -> None:
        trade = await self.db.get(Trade, position.trade_id)
        if not trade:
            return
        pnl = (exit_price - position.average_price) * position.quantity
        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.status = PositionStatus.CLOSED
        trade.exit_reason = reason
        position.last_price = exit_price
        position.unrealized_pnl = pnl
        position.status = PositionStatus.CLOSED
        await self.db.commit()
        await manager.broadcast("position_closed", {"position_id": position.id, "pnl": pnl, "reason": reason})
