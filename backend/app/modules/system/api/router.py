"""System endpoint route composition."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.system.schemas.analytics import AnalyticsResponse
from app.modules.system.schemas.health import HealthResponse, ReadinessResponse
from app.shared.database.session import get_db_session

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Return an inexpensive liveness signal without dependencies."""
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse, status_code=status.HTTP_200_OK)
async def readiness_check(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ReadinessResponse:
    """Verify the database is actually reachable, for orchestrator health checks."""
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not reachable.",
        ) from exc
    return ReadinessResponse(status="ok", database="ok")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics() -> AnalyticsResponse:
    """Return basic platform analytics."""
    return AnalyticsResponse()
