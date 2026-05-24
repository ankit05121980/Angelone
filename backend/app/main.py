from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.routes import router
from app.config.settings import get_settings
from app.database.session import create_all
from app.utils.logging import configure_logging


settings = get_settings()
configure_logging(settings.log_level)

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app = FastAPI(title=settings.app_name, version="1.0.0", openapi_url=f"{settings.api_prefix}/openapi.json")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup() -> None:
    await create_all()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
