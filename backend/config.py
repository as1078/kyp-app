from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    QDRANT_API_KEY: str
    QDRANT_URL: str

    class Config:
        env_file = ".env"

settings = Settings()