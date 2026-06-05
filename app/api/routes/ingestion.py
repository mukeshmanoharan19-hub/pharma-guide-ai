import os

from fastapi import APIRouter
from fastapi import BackgroundTasks
from app.services.ingestion_service import IngestionService
from pathlib import Path

router = APIRouter(prefix="/api", tags=["ingestion"])

file_path = Path(__file__).parent.parent.parent.parent / "data" / "seeds" / "products.json"

@router.post("/ingest-data")
async def upload_document(
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        IngestionService.ingest,
        file_path
    )

    return {
        "status": "processing"
    }