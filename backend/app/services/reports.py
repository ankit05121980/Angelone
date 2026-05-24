import csv
from io import StringIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Trade


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def trades_csv(self) -> str:
        result = await self.db.execute(select(Trade).order_by(Trade.created_at.desc()))
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["created_at", "mode", "symbol", "option_symbol", "quantity", "entry_price", "exit_price", "pnl", "status", "exit_reason"])
        for trade in result.scalars():
            writer.writerow(
                [
                    trade.created_at.isoformat(),
                    trade.mode.value,
                    trade.symbol.value,
                    trade.option_symbol,
                    trade.quantity,
                    trade.entry_price,
                    trade.exit_price or "",
                    trade.pnl,
                    trade.status.value,
                    trade.exit_reason or "",
                ]
            )
        return output.getvalue()
