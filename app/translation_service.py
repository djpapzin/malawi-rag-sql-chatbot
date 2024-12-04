from typing import Tuple, Dict
import logging
from functools import lru_cache
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.translations = self._load_translations()
        self.translator_cache = {}

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_translations() -> Dict[str, Dict[str, str]]:
        return {
            'en': {
                'no_results': 'No projects found matching your criteria.',
                'error': 'Sorry, an error occurred while processing your request.',
                'start_new': 'Please start a new search.',
                'no_more': 'No more results available.',
                'more_projects': 'Here are more projects:',
                'remaining': 'There are {} more projects.'
            }
        }

    async def detect_and_translate(self, text: str) -> Tuple[str, str]:
        """Detect language and translate to English if needed"""
        try:
            source_lang = detect(text)
            logger.info(f"Detected language: {source_lang}")

            if source_lang != 'en':
                cache_key = f"{source_lang}:{text}"
                if cache_key in self.translator_cache:
                    return source_lang, self.translator_cache[cache_key]
                
                translator = GoogleTranslator(source='auto', target='en')
                english_text = translator.translate(text)
                self.translator_cache[cache_key] = english_text
                return source_lang, english_text
            return 'en', text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return 'en', text

    def get_translation(self, key: str, language: str = 'en') -> str:
        """Get translation for a specific key"""
        translations = self.translations.get(language, self.translations['en'])
        return translations.get(key, self.translations['en'][key])