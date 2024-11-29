from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_URL: str
    NEO4J_URL: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    ACLED_KEY: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    S3_REGION: str

    class Config:
        env_file = ".env"

settings = Settings()