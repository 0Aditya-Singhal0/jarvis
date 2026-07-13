from pathlib import Path

from fastapi import APIRouter, Request, Response
from sqlalchemy.exc import SQLAlchemyError

from .config import ConfigurationError
from .db import database_is_ready
from .schema import schema_is_current

router = APIRouter()


@router.get("/healthz", include_in_schema=False)
def health(request: Request) -> Response:
    try:
        ready = database_is_ready(request.app.state.engine)
        current = schema_is_current(
            request.app.state.engine,
            Path(request.app.state.alembic_ini),
        )
    except (ConfigurationError, OSError, SQLAlchemyError, ValueError):
        ready = current = False
    status = 200 if ready and current else 503
    body = '{"status":"ok"}' if status == 200 else '{"status":"unavailable"}'
    return Response(body, status_code=status, media_type="application/json", headers={"Cache-Control": "no-store"})
