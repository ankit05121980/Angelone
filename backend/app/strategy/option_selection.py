from datetime import date, timedelta

from app.models.entities import IndexSymbol, OptionSide


LOT_SIZES: dict[IndexSymbol, int] = {
    IndexSymbol.NIFTY: 50,
    IndexSymbol.BANKNIFTY: 15,
}

STRIKE_STEPS: dict[IndexSymbol, int] = {
    IndexSymbol.NIFTY: 50,
    IndexSymbol.BANKNIFTY: 100,
}


def atm_strike(symbol: IndexSymbol, spot_price: float) -> int:
    step = STRIKE_STEPS[symbol]
    return int(round(spot_price / step) * step)


def nearest_weekly_expiry(from_date: date | None = None) -> date:
    current = from_date or date.today()
    # Indian index options usually expire on Thursday; move to the nearest upcoming Thursday.
    days_until_thursday = (3 - current.weekday()) % 7
    if days_until_thursday == 0:
        return current
    return current + timedelta(days=days_until_thursday)


def option_symbol(symbol: IndexSymbol, strike: int, side: OptionSide, expiry: date | None = None) -> str:
    expiry_date = nearest_weekly_expiry(expiry)
    return f"{symbol.value}{expiry_date:%d%b%y}{strike}{side.value}".upper()


def calculate_quantity(symbol: IndexSymbol, option_price: float, capital: float, allocation_pct: float = 0.25) -> int:
    lot_size = LOT_SIZES[symbol]
    budget = capital * allocation_pct
    lots = max(int(budget // (option_price * lot_size)), 1)
    return lots * lot_size
