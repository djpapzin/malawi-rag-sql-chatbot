from fastapi import Depends
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
from functools import lru_cache
from app.models import QueryParser

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
        import warnings
        from transformers import AutoModelForCausalLM
        
        # Suppress deprecation warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            device_map="auto",
            trust_remote_code=True
        )
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

@lru_cache()
def get_tokenizer():
    try:
        import warnings
        from transformers import AutoTokenizer
        
        # Suppress deprecation warnings
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/phi-2",
            trust_remote_code=True,
            padding_side="left"
        )
        return tokenizer
    except Exception as e:
        logger.error(f"Error loading tokenizer: {e}")
        return None