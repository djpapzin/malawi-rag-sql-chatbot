from fastapi import HTTPException
from typing import Dict, Any
from .logger import logger

class ChatbotError(Exception):
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def handle_error(error: Exception) -> Dict[str, Any]:
    """Handle different types of errors and return appropriate responses"""
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    
    if isinstance(error, ChatbotError):
        return {
            "error_message": error.message,
            "suggested_questions": [
                "What are the current infrastructure projects?",
                "Show me projects in Central Region",
                "What education projects are ongoing?"
            ]
        }
    
    if isinstance(error, HTTPException):
        return {
            "error_message": "An API error occurred. Please try again.",
            "suggested_questions": [
                "What are the major infrastructure projects?",
                "Show me recent projects",
                "What projects are planned?"
            ]
        }
    
    # Generic error
    return {
        "error_message": "I encountered an unexpected error. Please try rephrasing your question.",
        "suggested_questions": [
            "What infrastructure projects are there?",
            "Show me project statistics",
            "What are the ongoing projects?"
        ]
    }