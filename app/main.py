from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import uuid
from typing import Dict, Any, List
import logging

# Import our custom modules
from .models import ChatQuery, ChatResponse, QueryMetadata, QuerySource, QueryParser
from .response_generator import ResponseGenerator
from .sql_tracker import SQLTracker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Malawi Projects Chatbot",
    description="A chatbot for querying Malawi infrastructure projects",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
response_generator = ResponseGenerator()
sql_tracker = SQLTracker()
query_parser = QueryParser()

@app.post("/query")
async def process_query(chat_query: ChatQuery) -> ChatResponse:
    """
    Process a chat query and return response with source information
    """
    try:
        # Parse the query and generate SQL
        query_start = datetime.now()
        sql_query, filters = query_parser.parse_query_intent(chat_query.message)
        
        # Execute query and track sources
        df, sources = sql_tracker.execute_query(sql_query)
        query_end = datetime.now()
        
        # Create query metadata
        execution_time = (query_end - query_start).total_seconds()
        metadata = QueryMetadata(
            query_id=str(uuid.uuid4()),
            execution_time=execution_time,
            row_count=len(df),
            sources=sources,
            timestamp=query_end
        )
        
        # Generate response with sources
        response_data = response_generator.generate_response(
            df=df,
            query_metadata=metadata,
            filters=filters
        )
        
        # Generate suggested questions based on results
        suggested_questions = query_parser.generate_suggestions(df, filters)

        return ChatResponse(
            answer=response_data["answer"],
            suggested_questions=suggested_questions,
            metadata=metadata,
            sources=response_data["sources"],
            error=None
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return ChatResponse(
            answer="I encountered an error processing your query.",
            suggested_questions=[],
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}