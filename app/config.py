from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongodb_uri: str = Field(..., env="MONGODB_URI")
    mongodb_db: str = Field(..., env="MONGODB_DB")
    mongodb_collection: str = Field(..., env="MONGODB_COLLECTION")


settings = Settings()
