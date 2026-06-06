import os

from fastapi import APIRouter
from fastapi import BackgroundTasks
from app.services.ingestion_service import IngestionService
from pathlib import Path

router = APIRouter(prefix="/api", tags=["ingestion"])

@router.post("/ingest-data")
async def upload_document(
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        IngestionService.ingest
    )

    return {
        "status": "processing"
    }