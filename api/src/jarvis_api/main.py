from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .config import Settings
from .db import create_database_engine, create_session_factory
from .health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.from_environment()
    app.state.settings = settings
    app.state.engine = create_database_engine(settings)
    app.state.sessions = create_session_factory(app.state.engine)
    app.state.alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
    yield
    app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Jarvis Control Plane",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    return app


app = create_app()
