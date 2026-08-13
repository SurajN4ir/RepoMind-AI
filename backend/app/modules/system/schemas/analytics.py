"""Analytics endpoint response schemas."""

from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    indexedRepositories: int = 0
    totalChunks: int = 0
    queriesAnswered: int = 0
    avgQueryLatencyMs: float | None = None
    uptime: str | None = None
    languagesSupported: int = 4
