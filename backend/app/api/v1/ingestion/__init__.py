from fastapi import APIRouter

from backend.app.api.v1.ingestion.ingestion import router

ingestion_router = APIRouter()

ingestion_router.include_router(router, tags=['Ingestion'])