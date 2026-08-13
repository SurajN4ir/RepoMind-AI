"""API v1 route composition root."""

from fastapi import APIRouter

from app.api.v1.routes.indexing import router as indexing_router
from app.api.v1.routes.legacy_ingestion import router as legacy_ingestion_router
from app.api.v1.routes.query import router as query_router
from app.api.v1.routes.repositories import router as repository_router
from app.api.v1.routes.search import router as search_router
from app.modules.system.api.router import router as system_router

api_v1_router = APIRouter()
api_v1_router.include_router(system_router)
api_v1_router.include_router(repository_router)
api_v1_router.include_router(legacy_ingestion_router)
api_v1_router.include_router(indexing_router)
api_v1_router.include_router(query_router)
api_v1_router.include_router(search_router)
