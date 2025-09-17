from pydantic_settings import BaseSettings, SettingsConfigDict
from src.models import mapping
class Settings(BaseSettings):
    env: str = "dev"

    log_name: str = "BACKEND_LOG"
    log_format: str = "%(levelname)s - %(funcName)s - %(filename)s - %(message)s"

    monday_api_token: str
    monday_api_endpoint: str
    projects_board_id: int
    subtasks_board_id: int

    project_board_mapping: dict = mapping.PROJECT_BOARD_CONFIG
    subtask_board_mapping: dict = mapping.SUBTASK_BOARD_CONFIG



    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()