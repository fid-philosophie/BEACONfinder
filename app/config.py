from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    mongodb_uri: str = Field(..., env="MONGODB_URI")
    mongodb_db: str = Field(..., env="MONGODB_DB")
    mongodb_collection: str = Field(..., env="MONGODB_COLLECTION")

    app_host: str = Field("0.0.0.0", env="APP_HOST")
    container_port: int = Field(8000, ge=1, le=65535, env="CONTAINER_PORT")
    app_root_path: str = Field("", env="APP_ROOT_PATH")


settings = Settings()
