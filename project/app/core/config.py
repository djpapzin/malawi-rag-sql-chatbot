from pydantic_settings import BaseSettings
from typing import Dict, List

class Settings(BaseSettings):
    # Basic Configuration
    APP_NAME: str = "Malawi Infrastructure Projects Chatbot"
    DEBUG: bool = True
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "malawi_projects1.db"
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_SEARCH_RESULTS: int = 3
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/chatbot.log"
    
    # Domain-Specific Keywords
    SECTOR_KEYWORDS: Dict[str, List[str]] = {
        'education': ['school', 'teacher', 'classroom', 'training'],
        'health': ['hospital', 'clinic', 'healthcare', 'medical'],
        'roads': ['bridge', 'road', 'transport', 'highway'],
        'water': ['water', 'sanitation', 'borehole', 'irrigation']
    }
    
    class Config:
        env_file = ".env"

settings = Settings()
