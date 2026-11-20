from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8001
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB_NAME: str = "pdftrack"
    MONGODB_COLLECTION_NAME: str = "documents"
    MAX_PDF_SIZE_MB: int = 50
    DEFAULT_PAGE_LIMIT: int = 20
    MAX_PAGE_LIMIT: int = 100
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
