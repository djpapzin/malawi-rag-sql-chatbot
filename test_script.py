import sys
import os
import asyncio
import json
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Adjust the path to include the app modules
sys.path.append(os.path.abspath("."))

# Import necessary components
from app.query_parser import QueryParser
from app.response_formatter import ResponseFormatter
from app.database.service import DatabaseService
from app.llm_classification.new_classifier import LLMClassifier
from app.services.llm_service import LLMService

# Create request model
class ChatRequest(BaseModel):
    message: str
    language: str = "english"
    page: int = 1
    page_size: int = 10
    context: Optional[Dict[str, Any]] = None

async def test_query():
    """Test a specific query"""
    try:
        # Initialize services
        llm_service = LLMService()
        query_parser = QueryParser(llm_service=llm_service)
        response_formatter = ResponseFormatter()
        db_service = DatabaseService()
        classifier = LLMClassifier()
        
        # Create test request
        query = "Tell me about the CONSTRUCTION OF CLASSROOM BLOCK AND VIP TOILET AT MANGALE-TA CHOWE project"
        print(f"Testing query: {query}")
        
        # Classify the query
        classification = await classifier.classify_query(query, None)
        print(f"Classification: {classification.query_type}")
        
        # Convert classification to dict for the query parser
        classification_dict = {
            "query_type": classification.query_type,
            "confidence": classification.confidence,
            "parameters": classification.parameters.model_dump()
        }
        
        # Parse the query for database access
        query_info = await query_parser.parse_query(query, classification_dict)
        print(f"Generated SQL: {query_info['query']}")
        
        # Execute the query
        results = []
        if query_info["query"]:
            results = await db_service.execute_query(query_info["query"])
            print(f"Query returned {len(results)} results")
        
        # Convert QueryParameters to dict for response formatter
        parameters_dict = classification.parameters.model_dump()
        
        # Format the response
        response = response_formatter.format_response(
            query_type=classification.query_type,
            results=results,
            parameters=parameters_dict
        )
        
        # Add metadata
        response["metadata"] = {
            "query_time": query_info["metadata"]["timestamp"],
            "total_results": len(results),
            "sql_query": query_info["query"] if query_info["query"] else None,
            "confidence": classification.confidence
        }
        
        # Print response to verify all fields
        print("\nFull Response:")
        print(json.dumps(response, indent=2))
        
        # Specific check for all fields
        if classification.query_type == "specific" and len(results) > 0:
            print("\nChecking specific query fields:")
            for field_info in response_formatter.specific_project_fields:
                display_name = field_info[1]
                if display_name in response.get("data", {}):
                    print(f"✓ {display_name}: {response['data'][display_name]}")
                else:
                    print(f"✗ Missing field: {display_name}")
        
        return response
        
    except Exception as e:
        print(f"Error processing chat request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_query()) 