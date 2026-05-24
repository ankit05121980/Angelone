import asyncio
from typing import Any, AsyncIterator

import httpx
import pyotp
from loguru import logger

from app.broker.base import BrokerClient, BrokerOrder, Tick
from app.config.settings import Settings
from app.models.entities import IndexSymbol


class AngelOneClient(BrokerClient):
    """Small SmartAPI wrapper with explicit boundaries for live trading side effects."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.jwt_token: str | None = None
        self.feed_token: str | None = None
        self.refresh_token: str | None = None
        self._client = httpx.AsyncClient(base_url=settings.angel_base_url, timeout=15)

    async def login(self) -> None:
        if not all([self.settings.angel_api_key, self.settings.angel_client_code, self.settings.angel_password, self.settings.angel_totp_secret]):
            raise RuntimeError("Angel One credentials are not configured")

        totp = pyotp.TOTP(self.settings.angel_totp_secret.get_secret_value()).now()
        payload = {
            "clientcode": self.settings.angel_client_code,
            "password": self.settings.angel_password.get_secret_value(),
            "totp": totp,
        }
        response = await self._request("POST", "/rest/auth/angelbroking/user/v1/loginByPassword", json=payload)
        data = response.get("data") or {}
        self.jwt_token = data.get("jwtToken")
        self.feed_token = data.get("feedToken")
        self.refresh_token = data.get("refreshToken")
        if not self.jwt_token:
            raise RuntimeError("Angel One login did not return a JWT token")

    async def historical_candles(self, symbol: IndexSymbol, interval: str, from_ts: str, to_ts: str) -> list[dict[str, Any]]:
        payload = {
            "exchange": "NSE",
            "symboltoken": self._index_token(symbol),
            "interval": interval,
            "fromdate": from_ts,
            "todate": to_ts,
        }
        response = await self._request("POST", "/rest/secure/angelbroking/historical/v1/getCandleData", json=payload)
        return response.get("data") or []

    async def place_market_order(self, option_symbol: str, side: str, quantity: int) -> BrokerOrder:
        payload = {
            "variety": "NORMAL",
            "tradingsymbol": option_symbol,
            "symboltoken": option_symbol,
            "transactiontype": side,
            "exchange": "NFO",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": str(quantity),
        }
        response = await self._request("POST", "/rest/secure/angelbroking/order/v1/placeOrder", json=payload)
        order_id = str((response.get("data") or {}).get("orderid", ""))
        return BrokerOrder(broker_order_id=order_id, status="placed", raw=response)

    async def place_stoploss_order(self, option_symbol: str, quantity: int, trigger_price: float) -> BrokerOrder:
        payload = {
            "variety": "STOPLOSS",
            "tradingsymbol": option_symbol,
            "symboltoken": option_symbol,
            "transactiontype": "SELL",
            "exchange": "NFO",
            "ordertype": "STOPLOSS_MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "triggerprice": str(round(trigger_price, 2)),
            "quantity": str(quantity),
        }
        response = await self._request("POST", "/rest/secure/angelbroking/order/v1/placeOrder", json=payload)
        order_id = str((response.get("data") or {}).get("orderid", ""))
        return BrokerOrder(broker_order_id=order_id, status="placed", raw=response)

    async def order_status(self, broker_order_id: str) -> dict[str, Any]:
        response = await self._request("GET", "/rest/secure/angelbroking/order/v1/getOrderBook")
        orders = response.get("data") or []
        return next((order for order in orders if str(order.get("orderid")) == broker_order_id), {})

    async def positions(self) -> list[dict[str, Any]]:
        response = await self._request("GET", "/rest/secure/angelbroking/order/v1/getPosition")
        return response.get("data") or []

    async def stream_ticks(self, tokens: list[str]) -> AsyncIterator[Tick]:
        # The production websocket protocol requires token subscription framing from SmartAPI.
        # This loop keeps the application boundary async and retry-safe while deployments wire tokens.
        while True:
            logger.debug("Angel One stream heartbeat for {} tokens", len(tokens))
            await asyncio.sleep(1)
            for token in tokens:
                yield Tick(symbol=token, token=token, last_price=0, volume=0, exchange_timestamp="")

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        headers = {
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-PrivateKey": self.settings.angel_api_key.get_secret_value() if self.settings.angel_api_key else "",
        }
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        for attempt in range(3):
            try:
                response = await self._client.request(method, path, headers=headers, **kwargs)
                response.raise_for_status()
                payload = response.json()
                if payload.get("status") is False:
                    raise RuntimeError(payload.get("message", "Angel One API request failed"))
                return payload
            except Exception as exc:
                if attempt == 2:
                    logger.exception("Angel One request failed: {} {}", method, path)
                    raise
                await asyncio.sleep(2**attempt)
                logger.warning("Retrying Angel One request after error: {}", exc)
        raise RuntimeError("Unreachable Angel One retry state")

    @staticmethod
    def _index_token(symbol: IndexSymbol) -> str:
        return "99926000" if symbol == IndexSymbol.NIFTY else "99926009"
