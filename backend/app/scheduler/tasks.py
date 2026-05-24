from celery import Celery
from loguru import logger

from app.config.settings import get_settings


settings = get_settings()
celery_app = Celery("trading_scheduler", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="scheduler.market_open_healthcheck")
def market_open_healthcheck() -> str:
    logger.info("Market scheduler healthcheck")
    return "ok"


@celery_app.task(name="scheduler.daily_pnl_report")
def daily_pnl_report() -> str:
    logger.info("Daily PnL report task triggered")
    return "queued"
