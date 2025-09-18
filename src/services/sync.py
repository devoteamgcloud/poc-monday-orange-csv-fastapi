import pprint

from src.config import settings
from src.logger import logger
from src.services.monday import MondayService


class SyncService:
    def __init__(self, monday_service: MondayService):
        self.monday_service = monday_service

    def sync_projects(self, df_projects):
        if df_projects is None or df_projects.empty:
            return

        logger.info("***Processing Projects***")
        projects_keys = df_projects["Key"].tolist()
        key_column_id = settings.project_board_mapping["Key"]

        # Fetch existing projects from Monday
        existing_projects = self.monday_service.fetch_monday_items(
            board_id=settings.projects_board_id,
            items_keys=projects_keys,
            key_column_id=key_column_id,
        )
        print("Existing Projects in Monday:")
        pprint.pprint(existing_projects)

        # Prepare inserts and mutations by comparing CSV with existing items in Monday
        projects_to_create, projects_to_update = self.monday_service.prepare_mutations(
            csv_df=df_projects,
            board_mapping=settings.project_board_mapping,
            monday_items=existing_projects,
        )
        print("***Projects to create***")
        pprint.pprint(projects_to_create)
        print("***Projects to update***")
        pprint.pprint(projects_to_update)

        # Insert and update projects in Monday
        self.monday_service.execute_mutations(
            settings.projects_board_id, projects_to_create, projects_to_update
        )
        logger.info("***Finished processing projects.***")
        return

    def sync_subtasks(self, df_subtasks):
        if df_subtasks is None or df_subtasks.empty:
            return

        logger.info("***Processing Subtasks***")
        subtasks_keys = df_subtasks["Key"].tolist()
        key_column_id = settings.project_board_mapping["Key"]

        # Fetch existing subtasks from Monday
        existing_subtasks = self.monday_service.fetch_monday_items(
            board_id=settings.subtasks_board_id,
            items_keys=subtasks_keys,
            key_column_id=key_column_id,
        )
        print("Existing subtasks in Monday:")
        pprint.pprint(existing_subtasks)

        # Prepare inserts and mutations by comparing CSV with existing items in Monday
        subtasks_to_create, subtasks_to_update = self.monday_service.prepare_mutations(
            csv_df=df_subtasks,
            board_mapping=settings.project_board_mapping,
            monday_items=existing_subtasks,
        )
        print("***Subtasks to create***")
        pprint.pprint(subtasks_to_create)
        print("***Subtasks to update***")
        pprint.pprint(subtasks_to_update)

        # Insert and update subtasks in Monday
        self.monday_service.execute_mutations(
            settings.subtasks_board_id, subtasks_to_create, subtasks_to_update
        )
        logger.info("***Finished processing subtasks.***")
        return
