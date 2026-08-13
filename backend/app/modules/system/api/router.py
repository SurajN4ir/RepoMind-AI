"""System endpoint route composition."""

from fastapi import APIRouter, status

from app.modules.system.schemas.analytics import AnalyticsResponse
from app.modules.system.schemas.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Return an inexpensive liveness signal without dependencies."""
    return HealthResponse(status="ok")


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics() -> AnalyticsResponse:
    """Return basic platform analytics."""
    return AnalyticsResponse()
