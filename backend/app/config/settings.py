from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Angel One Index Algo"
    environment: Literal["local", "staging", "production"] = "local"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    database_url: str = "postgresql+asyncpg://trader:trader@postgres:5432/trading"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: SecretStr = Field(default=SecretStr("change-me-in-production"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    angel_api_key: SecretStr | None = None
    angel_client_code: str | None = None
    angel_password: SecretStr | None = None
    angel_totp_secret: SecretStr | None = None
    angel_base_url: str = "https://apiconnect.angelbroking.com"
    angel_feed_url: str = "wss://smartapisocket.angelone.in/smart-stream"

    default_mode: Literal["paper", "live"] = "paper"
    nifty_capital: float = 50_000
    banknifty_capital: float = 50_000
    max_loss_per_trade: float = 1_000
    target_profit_per_trade: float = 2_000
    max_daily_loss: float = 3_000
    max_trades_per_index: int = 3
    max_concurrent_trades: int = 2
    entry_start_time: str = "09:30"
    entry_stop_time: str = "12:30"
    force_exit_time: str = "15:15"

    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    alert_from_email: str | None = None
    alert_to_email: str | None = None

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
