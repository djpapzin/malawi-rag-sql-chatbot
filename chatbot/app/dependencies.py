from fastapi import Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
from functools import lru_cache
from models import QueryParser

logger = logging.getLogger(__name__)

@lru_cache()
def get_templates():
    template_dir = Path(__file__).parent / "templates"
    if template_dir.exists():
        return Jinja2Templates(directory=str(template_dir))
    logger.error(f"Templates directory not found at {template_dir}")
    return None

@lru_cache()
def get_query_parser():
    return QueryParser()

@lru_cache()
def get_model():
    try:
        from transformers import AutoModelForCausalLM
        return AutoModelForCausalLM.from_pretrained("microsoft/phi-2", device_map="auto")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

@lru_cache()
def get_tokenizer():
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained("microsoft/phi-2")
    except Exception as e:
        logger.error(f"Error loading tokenizer: {e}")
        return None