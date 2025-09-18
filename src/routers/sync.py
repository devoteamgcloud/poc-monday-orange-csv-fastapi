from pathlib import Path

from fastapi import APIRouter, Depends

from src.config import settings
from src.dependencies import get_sync_service
from src.logger import logger
from src.services.sync import SyncService
from src.utils import csv

router = APIRouter()

ROOT_DIR = Path(__file__).parent.parent.parent


@router.get("/sync-csv")
def sync_csv(sync_service: SyncService = Depends(get_sync_service)):
    # Load and filter CSV data
    df_projects, df_subtasks = csv.load_and_filter(str(ROOT_DIR / "sample.csv"))
    logger.info(f"CSV Projects: {len(df_projects)}, Subtasks: {len(df_subtasks)}")

    # Process projects
    sync_service.sync_projects(df_projects)

    # Process subtasks
    sync_service.sync_subtasks(df_subtasks)

    return {"Success": "Sync of CSV to Monday complete."}
