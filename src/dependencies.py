from fastapi import Depends

from src.services.monday import MondayService
from src.services.sync import SyncService


def get_monday_service() -> MondayService:
    return MondayService()


def get_sync_service(
    monday_service: MondayService = Depends(get_monday_service),
) -> SyncService:
    return SyncService(monday_service)
