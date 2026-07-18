from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..config import get_settings
from ..dependencies import Database, Runtime
from ..runtime import RuntimeError

router = APIRouter(tags=["system"])
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
        "runtime": settings.runtime_mode,
    }


@router.get("/ready")
def readiness(database: Database, runtime: Runtime) -> dict[str, str | int]:
    try:
        database.scalar(select(1))
        resources = runtime.list_resources()
    except (SQLAlchemyError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Control plane is not ready",
        ) from error
    return {
        "status": "ready",
        "database": "ok",
        "runtime": settings.runtime_mode,
        "managed_resources": len(resources),
    }
