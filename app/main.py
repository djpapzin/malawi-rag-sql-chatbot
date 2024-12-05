from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from typing import Optional, List, Dict, Any

# Import our custom modules
from app.models import ChatQuery, ChatResponse, QueryParser
from app.dependencies import get_templates, get_query_parser, get_model, get_tokenizer
from app.response_generator import ResponseGenerator
from app.translation_service import TranslationService
from app.suggestion_generator import SuggestionGenerator
from app.database.query_builder import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Application Configuration
class Config:
    BASE_DIR = Path(__file__).parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    STATIC_DIR = BASE_DIR / "static"
    ALLOWED_ORIGINS = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    MODEL_MAX_LENGTH = 512
    TEMPERATURE = 0.7

config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Malawi Projects Chatbot",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
query_parser = get_query_parser()
response_generator = ResponseGenerator()
translation_service = TranslationService()
suggestion_generator = SuggestionGenerator()
db_manager = DatabaseManager('malawi_projects1.db')
templates = get_templates()
model = get_model()
tokenizer = get_tokenizer()

# Configure templates
if not templates:
    logger.error(f"Templates directory not found at {config.TEMPLATES_DIR}")

# Configure static files
try:
    if config.STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
        logger.info(f"Static files mounted successfully at {config.STATIC_DIR}")
    else:
        logger.warning(f"Static directory not found at {config.STATIC_DIR}")
except Exception as e:
    logger.error(f"Error mounting static files: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page endpoint"""
    if not templates:
        raise HTTPException(status_code=500, detail="Templates not configured")
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/test")
async def test_endpoint():
    """Basic test endpoint"""
    try:
        return {
            "status": "ok",
            "database": "connected" if db_manager else "not connected",
            "model": "loaded" if model else "not loaded",
            "tokenizer": "loaded" if tokenizer else "not loaded",
            "query_parser": "initialized" if query_parser else "not initialized"
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/test/db")
async def test_db():
    """Test database connection and query"""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proj_dashboard")
            count = cursor.fetchone()[0]
            return {"status": "success", "project_count": count}
    except Exception as e:
        logger.error(f"Database test error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/test/parser/{query}")
async def test_parser(query: str):
    """Test query parser functionality"""
    try:
        source_lang = 'en'  # Default to English for testing
        filters = query_parser.parse_query_intent(query, source_lang)
        return {
            "status": "success",
            "original_query": query,
            "parsed_filters": filters
        }
    except Exception as e:
        logger.error(f"Parser test error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery):
    """Main chat endpoint"""
    try:
        logger.info(f"Received query: {query.message}")
        
        # Detect language and translate
        logger.info("Starting language detection")
        source_lang, english_query = await translation_service.detect_and_translate(query.message)
        logger.info(f"Detected language: {source_lang}, Translated query: {english_query}")
        
        # Parse filters
        logger.info("Parsing query intent")
        filters = query_parser.parse_query_intent(english_query, source_lang)
        logger.info(f"Parsed filters: {filters}")
        
        # Database query
        logger.info("Fetching data from database")
        df = db_manager.get_project_data(filters)
        logger.info(f"Retrieved {len(df)} records")

        if df.empty:
            logger.info("No results found")
            return ChatResponse(
                answer=translation_service.get_translation('no_results', source_lang),
                suggested_questions=[]
            )

        # Generate response
        logger.info("Generating response")
        answer = await response_generator.generate_response(
            df=df,
            filters=filters,
            language=source_lang,
            model=model,
            tokenizer=tokenizer
        )
        logger.info("Response generated successfully")

        # Generate suggestions
        logger.info("Generating suggestions")
        suggestions = await suggestion_generator.generate_suggestions(
            filters=filters,
            df=df,
            language=source_lang
        )
        logger.info("Suggestions generated successfully")

        return ChatResponse(
            answer=answer,
            suggested_questions=suggestions
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        return ChatResponse(
            answer=f"Sorry, an error occurred: {str(e)}",
            suggested_questions=[]
        )

@app.post("/chat/more", response_model=ChatResponse)
async def get_more_results(query: ChatQuery):
    """Pagination endpoint"""
    try:
        source_lang = translation_service.detect_language(query.message)
        
        if not query.chat_history:
            return ChatResponse(
                answer=translation_service.get_translation('start_new', source_lang),
                suggested_questions=[]
            )

        # Get pagination info and data
        pagination_info = await response_generator.get_pagination_info(query.chat_history)
        df = db_manager.get_project_data(pagination_info['filters'])

        if df.empty or pagination_info['offset'] >= len(df):
            return ChatResponse(
                answer=translation_service.get_translation('no_more', source_lang),
                suggested_questions=[]
            )

        # Generate paginated response
        answer = await response_generator.generate_paginated_response(
            df=df,
            pagination_info=pagination_info,
            language=source_lang
        )

        # Generate suggestions
        suggestions = await suggestion_generator.generate_suggestions(
            filters=pagination_info['filters'],
            df=df,
            language=source_lang
        )

        return ChatResponse(
            answer=answer,
            suggested_questions=suggestions
        )

    except Exception as e:
        logger.error(f"Error in show more: {e}", exc_info=True)
        return ChatResponse(
            answer=translation_service.get_translation('error', source_lang),
            suggested_questions=[]
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )