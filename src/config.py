from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    env: str = "dev"
    monday_api_token: str
    monday_api_endpoint: str
    projects_board_id: int
    subtasks_board_id: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()