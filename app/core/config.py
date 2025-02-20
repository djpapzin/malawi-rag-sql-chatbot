# app/core/config.py
import os
from enum import Enum
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LanguageCode(str, Enum):
    ENGLISH = "en"
    CHICHEWA = "ny"
    TUMBUKA = "tum"
    YAO = "yao"
    RUSSIAN = "ru"
    UZBEK = "uz"

class ProjectSector(str, Enum):
    EDUCATION = "Education"
    HEALTH = "Health"
    ROADS = "Roads and bridges"
    WATER = "Water and Sanitation"
    SECURITY = "Community security initiatives"
    AGRICULTURE = "Agriculture and environment"
    COMMERCIAL = "Commercial services"

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Malawi Infrastructure Projects Chatbot"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    PORT: str = "8000"
    HOST: str = "0.0.0.0"
    NODE_ENV: str = "development"
    
    # Database Settings
    DATABASE_URL: str = os.path.join(BASE_DIR, "malawi_projects1.db")
    DATABASE_TYPE: str = "sqlite"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # API Keys and External Services
    TOGETHER_API_KEY: str = "your_key_here"
    AZURE_TRANSLATION_KEY: str = "your_key_here"
    AZURE_TRANSLATION_REGION: str = "your_region"
    AZURE_TRANSLATION_ENDPOINT: str = "https://api.cognitive.microsofttranslator.com/"
    
    # CORS Settings
    CORS_ORIGINS: str = '["http://localhost:3000", "https://ai.kwantu.support"]'
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    LLM_MODEL: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"
    LLM_TEMPERATURE: str = "0.1"
    MAX_SEARCH_RESULTS: int = 3
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")

    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 3
    MAX_PAGE_SIZE: int = 10

    # Supported Languages Configuration
    DEFAULT_LANGUAGE: LanguageCode = LanguageCode.ENGLISH
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        LanguageCode.ENGLISH: "English",
        LanguageCode.CHICHEWA: "Chichewa",
        LanguageCode.TUMBUKA: "Tumbuka",
        LanguageCode.YAO: "Yao",
        LanguageCode.RUSSIAN: "Russian",
        LanguageCode.UZBEK: "Uzbek"
    }

    # Language-specific Keywords
    KEYWORDS: Dict[str, Dict[str, List[str]]] = {
        "en": {
            ProjectSector.EDUCATION.value: [
                "education", "school", "classroom", "teaching",
                "educational", "learning", "student", "teacher",
                "college", "university", "academic"
            ],
            ProjectSector.HEALTH.value: [
                "health", "hospital", "clinic", "medical", "healthcare",
                "health center", "health facility", "doctor", "nurse",
                "pharmacy", "patient", "medicine"
            ],
            ProjectSector.ROADS.value: [
                "road", "bridge", "transport", "highway", "street",
                "pathway", "construction", "infrastructure", "traffic"
            ],
            ProjectSector.WATER.value: [
                "water", "sanitation", "borehole", "well", "pipeline",
                "water supply", "irrigation", "drainage", "sewage"
            ],
            ProjectSector.SECURITY.value: [
                "security", "police", "community security", "safety",
                "police unit", "security post", "protection"
            ]
        },
        "ny": {  # Chichewa
            ProjectSector.EDUCATION.value: [
                "sukulu", "aphunzitsi", "kalasi", "maphunziro",
                "ophunzira", "kupunzira", "koleji", "yunivesite"
            ],
            ProjectSector.HEALTH.value: [
                "chipatala", "zachipatala", "mankhwala", "dokotala",
                "namwino", "thanzi", "chithandizo", "odwala"
            ],
            ProjectSector.ROADS.value: [
                "msewu", "mlatho", "mayendedwe", "njira",
                "kumanga", "ntchito", "galimoto"
            ],
            ProjectSector.WATER.value: [
                "madzi", "ukhondo", "mjigo", "thope",
                "mapaipi", "pompi", "cisterne"
            ],
            ProjectSector.SECURITY.value: [
                "chitetezo", "apolisi", "chambulo", "polisi",
                "alonda", "mlonda"
            ]
        },
        "ru": {  # Russian
            ProjectSector.EDUCATION.value: [
                "образование", "школа", "класс", "обучение", "учеба",
                "студент", "учитель", "колледж", "университет"
            ],
            ProjectSector.HEALTH.value: [
                "здоровье", "больница", "клиника", "медицина",
                "здравоохранение", "врач", "доктор", "аптека"
            ],
            ProjectSector.ROADS.value: [
                "дорога", "мост", "транспорт", "шоссе",
                "путь", "строительство", "инфраструктура"
            ],
            ProjectSector.WATER.value: [
                "вода", "санитария", "скважина", "колодец",
                "водопровод", "ирригация", "дренаж"
            ],
            ProjectSector.SECURITY.value: [
                "безопасность", "полиция", "охрана",
                "защита", "пост", "патруль"
            ]
        },
        "uz": {  # Uzbek
            ProjectSector.EDUCATION.value: [
                "ta'lim", "maktab", "sinf", "o'qitish",
                "talaba", "o'qituvchi", "kollej", "universitet"
            ],
            ProjectSector.HEALTH.value: [
                "sog'liq", "shifoxona", "klinika", "tibbiyot",
                "sog'liqni saqlash", "shifokor", "dorixona"
            ],
            ProjectSector.ROADS.value: [
                "yo'l", "ko'prik", "transport", "trassа",
                "qurilish", "infratuzilma"
            ],
            ProjectSector.WATER.value: [
                "suv", "sanitariya", "quduq", "vodoprovod",
                "sug'orish", "drenaj"
            ],
            ProjectSector.SECURITY.value: [
                "xavfsizlik", "politsiya", "muhofaza",
                "himoya", "post", "patrul"
            ]
        }
    }

    # Common Translations
    COMMON_PHRASES: Dict[str, Dict[str, str]] = {
        "ny": {
            "show_more": "Onani zambiri",
            "no_results": "Palibe zotsatira",
            "loading": "Tikufufuza..."
        },
        "ru": {
            "show_more": "Показать больше",
            "no_results": "Нет результатов",
            "loading": "Загрузка..."
        },
        "uz": {
            "show_more": "Ko'proq ko'rsatish",
            "no_results": "Natija yo'q",
            "loading": "Yuklanmoqda..."
        }
    }

    # Currency Formatting
    CURRENCY_FORMATS: Dict[str, Dict[str, str]] = {
        "en": {"symbol": "MK", "separator": ",", "decimal": "."},
        "ny": {"symbol": "MK", "separator": " ", "decimal": ","},
        "ru": {"symbol": "MK", "separator": " ", "decimal": ","},
        "uz": {"symbol": "MK", "separator": " ", "decimal": ","}
    }

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }

    def get_language_code(self, language_name: str) -> str:
        """Get language code from language name"""
        return next(
            (code for code, name in self.SUPPORTED_LANGUAGES.items() 
             if name.lower() == language_name.lower()),
            self.DEFAULT_LANGUAGE
        )

    def get_keywords(self, language: str, sector: Optional[str] = None) -> Dict[str, List[str]]:
        """Get keywords for a specific language and optionally sector"""
        lang_keywords = self.KEYWORDS.get(language, self.KEYWORDS['en'])
        if sector:
            return {sector: lang_keywords.get(sector, [])}
        return lang_keywords

    def get_currency_format(self, language: str) -> Dict[str, str]:
        """Get currency formatting rules for a specific language"""
        return self.CURRENCY_FORMATS.get(language, self.CURRENCY_FORMATS['en'])

settings = Settings()