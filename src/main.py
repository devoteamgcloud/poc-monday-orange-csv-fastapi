import pprint

from fastapi import Depends, FastAPI
from typing_extensions import Annotated

from src.config import settings
from src.logger import logger
from src.models import mapping
from src.services.monday import MondayService
from src.utils import csv

app = FastAPI(redoc_url=None, docs_url=None if settings.env == "prod" else "/docs")


@app.get("/sync-csv")
def read_root(monday_service: Annotated[MondayService, Depends()]):
    df_projects, df_subtasks = csv.load_and_filter("sample.csv")
    logger.info(f"CSV Projects: {len(df_projects)}, Subtasks: {len(df_subtasks)}")

    # Process parents
    if df_projects is not None and not df_projects.empty:
        logger.info("***Processing Projects***")
        projects_keys = df_projects["Key"].tolist()
        key_column_id = settings.project_board_mapping["Key"]

        existing_projects = monday_service.fetch_monday_items(
            board_id=settings.projects_board_id,
            items_keys=projects_keys,
            key_column_id=key_column_id,
        )
        print("Existing Projects in Monday:")
        pprint.pprint(existing_projects)

    # Prepare inserts and mutations
    projects_to_create, projects_to_update = monday_service.prepare_mutations(
        csv_df=df_projects, board_mapping=settings.project_board_mapping, monday_items=existing_projects
    )
    print("***Projects to create***")
    pprint.pprint(projects_to_create)
    print("***Projects to update***")
    pprint.pprint(projects_to_update)

    return {"Hello": "Root of Docusign Integration API"}
