from typing import Dict, Any
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "sqlite:///pmisProjects.db"
    TOGETHER_API_KEY: str
    MODEL_NAME: str = "togethercomputer/llama-2-70b-chat"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 512
    
    class Config:
        env_file = ".env"

# Initialize settings
db_settings = DatabaseSettings()
