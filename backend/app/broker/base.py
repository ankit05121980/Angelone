from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator

from app.models.entities import IndexSymbol, OptionSide


@dataclass(frozen=True)
class BrokerOrder:
    broker_order_id: str
    status: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class Tick:
    symbol: str
    token: str
    last_price: float
    volume: float
    exchange_timestamp: str


class BrokerClient(ABC):
    @abstractmethod
    async def login(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def historical_candles(self, symbol: IndexSymbol, interval: str, from_ts: str, to_ts: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def place_market_order(self, option_symbol: str, side: str, quantity: int) -> BrokerOrder:
        raise NotImplementedError

    @abstractmethod
    async def place_stoploss_order(self, option_symbol: str, quantity: int, trigger_price: float) -> BrokerOrder:
        raise NotImplementedError

    @abstractmethod
    async def order_status(self, broker_order_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def positions(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def stream_ticks(self, tokens: list[str]) -> AsyncIterator[Tick]:
        raise NotImplementedError


def instrument_key(symbol: IndexSymbol, strike: int, side: OptionSide, expiry: str) -> str:
    return f"{symbol.value}:{expiry}:{strike}:{side.value}"
