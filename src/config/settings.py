from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee las variables de entorno del archivo .env
    """

    # Data Storage
    DATA_DIR: str = "./data"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Personal Finance API"
    DEBUG: bool = False

    # CORS
    ALLOWED_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
