"""
Translation Service for RAG SQL Chatbot
"""

import os
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationService:
    """Handler for translation operations using Azure Translator"""
    
    def __init__(self):
        """Initialize Translation Service"""
        self.api_key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com/")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
        
        if not self.api_key:
            logger.warning("AZURE_TRANSLATOR_KEY not set. Translation service will be disabled.")
        else:
            logger.info("Translation service initialized")
    
    async def translate(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translated text
        """
        try:
            if not self.api_key:
                logger.warning("Translation skipped: API key not configured")
                return text
                
            # Convert language code to Azure format
            language_map = {
                "english": "en",
                "russian": "ru",
                "uzbek": "uz"
            }
            target_code = language_map.get(target_language.lower(), "en")
            
            # Prepare request
            url = f"{self.endpoint}/translate"
            params = {
                "api-version": "3.0",
                "to": target_code
            }
            headers = {
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Ocp-Apim-Subscription-Region": self.region,
                "Content-Type": "application/json"
            }
            body = [{"text": text}]
            
            # Make request
            response = requests.post(url, params=params, headers=headers, json=body)
            response.raise_for_status()
            
            # Extract translation
            translation = response.json()[0]["translations"][0]["text"]
            logger.info(f"Successfully translated text to {target_language}")
            
            return translation
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text  # Return original text on error 