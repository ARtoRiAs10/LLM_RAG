from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Open Source RAG API"
    DATABASE_URL: str
    
    # Updated variables for Qdrant Cloud
    QDRANT_URL: str
    QDRANT_API_KEY: str

    OLLAMA_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()