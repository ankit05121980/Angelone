from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import IndexSymbol, MarketData
from app.schemas.trading import Candle


class MarketDataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_candle(self, candle: Candle) -> MarketData:
        result = await self.db.execute(
            select(MarketData).where(
                MarketData.symbol == candle.symbol,
                MarketData.timeframe == candle.timeframe,
                MarketData.candle_time == candle.candle_time,
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            model = MarketData(**candle.model_dump())
            self.db.add(model)
        else:
            model.open = candle.open
            model.high = candle.high
            model.low = candle.low
            model.close = candle.close
            model.volume = candle.volume
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def recent_candles(self, symbol: IndexSymbol, timeframe: str, limit: int = 100) -> list[Candle]:
        result = await self.db.execute(
            select(MarketData)
            .where(MarketData.symbol == symbol, MarketData.timeframe == timeframe)
            .order_by(MarketData.candle_time.desc())
            .limit(limit)
        )
        rows = list(reversed(result.scalars().all()))
        return [
            Candle(
                symbol=row.symbol,
                timeframe=row.timeframe,
                candle_time=row.candle_time,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
            )
            for row in rows
        ]

    @staticmethod
    def tick_to_candle(symbol: IndexSymbol, price: float, volume: float, timeframe: str = "3m") -> Candle:
        return Candle(
            symbol=symbol,
            timeframe=timeframe,
            candle_time=datetime.utcnow().replace(second=0, microsecond=0),
            open=price,
            high=price,
            low=price,
            close=price,
            volume=volume,
        )
