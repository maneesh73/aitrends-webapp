from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    database_url: str = "sqlite:///./aitrends.db"
    guardian_api_key: str = ""
    github_token: str = ""
    huggingface_api_key: str = ""
    youtube_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    sync_secret_key: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
