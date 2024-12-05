# test_translation.py
from app.translation_service import TranslationService
import asyncio

async def test_translation():
    # Initialize the translation service
    translation_service = TranslationService()

    # Sample text to translate
    sample_texts = [
        "Hello, how are you?",  # English
        "Hola, ¿cómo estás?",   # Spanish
        "Bonjour, comment ça va?",  # French
        "Привет, как дела?",    # Russian
        "Salom, qalaysiz?"      # Uzbek
    ]

    # Test translation for each sample text
    for text in sample_texts:
        source_lang, translated_text = await translation_service.detect_and_translate(text)
        print(f"Original: {text}")
        print(f"Detected Language: {source_lang}")
        print(f"Translated: {translated_text}\n")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_translation())