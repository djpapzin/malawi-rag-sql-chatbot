"""
Test suite for LLM integration in RAG SQL Chatbot
"""

import os
import pytest
from dotenv import load_dotenv
from src.llm_service import LLMService

# Load environment variables
load_dotenv()

@pytest.fixture
def llm_service():
    """Fixture to provide LLM service instance"""
    return LLMService()

def test_llm_initialization(llm_service):
    """Test LLM service initialization"""
    assert llm_service.api_key is not None
    assert llm_service.model == "mistralai/Mixtral-8x7B-Instruct-v0.1"
    assert llm_service.temperature == 0.7
    assert llm_service.max_tokens == 1500

def test_system_prompts(llm_service):
    """Test language-specific system prompts"""
    # Test English prompt
    english_prompt = llm_service.get_system_prompt("english")
    assert "infrastructure projects assistant for Malawi" in english_prompt
    
    # Test Russian prompt
    russian_prompt = llm_service.get_system_prompt("russian")
    assert "инфраструктурным проектам" in russian_prompt
    
    # Test Uzbek prompt
    uzbek_prompt = llm_service.get_system_prompt("uzbek")
    assert "infratuzilma loyihalari" in uzbek_prompt

def test_chat_context_formatting(llm_service):
    """Test chat history formatting"""
    chat_history = [
        {"type": "query", "text": "Show me projects in Malawi"},
        {"type": "response", "text": "Found 5 projects"},
        {"type": "query", "text": "What's the budget?"}
    ]
    
    formatted = llm_service.format_chat_context(chat_history)
    assert "User: Show me projects in Malawi" in formatted
    assert "Assistant: Found 5 projects" in formatted
    assert "User: What's the budget?" in formatted

@pytest.mark.asyncio
async def test_query_processing(llm_service):
    """Test query processing with LLM"""
    query = "Show me education projects in Northern Region"
    response = llm_service.process_query(
        query=query,
        chat_history=[],
        language="english"
    )
    
    # Check response structure
    assert "response" in response
    assert "llm_processing" in response
    assert "model" in response["llm_processing"]
    assert "enhanced_query" in response["llm_processing"]
    assert "suggested_questions" in response["llm_processing"]
    
    # Check response content
    assert len(response["response"]) > 0
    assert "education" in response["response"].lower() or "projects" in response["response"].lower()

def test_query_enhancement(llm_service):
    """Test query enhancement functionality"""
    test_queries = [
        "show projects",
        "what's in Northern Region",
        "education status"
    ]
    
    for query in test_queries:
        enhanced = llm_service.enhance_query(query)
        assert enhanced is not None
        assert len(enhanced) > 0
        assert enhanced != query  # Enhanced query should be different

def test_suggestion_generation(llm_service):
    """Test follow-up question generation"""
    sample_response = """
    Found 12 education projects in Northern Region.
    Total budget: MK 2,450,000,000
    Status: 8 active, 3 completed, 1 planning
    Locations: Mzimba (5), Rumphi (4), Karonga (3)
    """
    
    # Test English suggestions
    en_suggestions = llm_service.generate_suggestions(sample_response, "english")
    assert len(en_suggestions) > 0
    assert len(en_suggestions) <= 4  # Should not exceed 4 suggestions
    
    # Test Russian suggestions
    ru_suggestions = llm_service.generate_suggestions(sample_response, "russian")
    assert len(ru_suggestions) > 0
    assert len(ru_suggestions) <= 4
    
    # Test Uzbek suggestions
    uz_suggestions = llm_service.generate_suggestions(sample_response, "uzbek")
    assert len(uz_suggestions) > 0
    assert len(uz_suggestions) <= 4

def test_error_handling(llm_service):
    """Test error handling in LLM service"""
    # Test with empty query
    response = llm_service.process_query("", [], "english")
    assert "error" in response
    
    # Test with invalid language
    response = llm_service.process_query("test", [], "invalid_language")
    assert "response" in response  # Should fall back to English
    
    # Test with malformed chat history
    response = llm_service.process_query("test", [{"invalid": "format"}], "english")
    assert "response" in response  # Should handle gracefully
    assert "llm_processing" in response  # Should include processing info
    assert response["llm_processing"]["response_formatted"] is True  # Should process normally

@pytest.mark.integration
def test_full_conversation_flow(llm_service):
    """Test a complete conversation flow"""
    conversation = []
    
    # First query
    response1 = llm_service.process_query(
        "Show me education projects in Northern Region",
        conversation,
        "english"
    )
    conversation.append({"type": "query", "text": "Show me education projects in Northern Region"})
    conversation.append({"type": "response", "text": response1["response"]})
    
    assert "education" in response1["response"].lower()
    assert "Northern Region" in response1["response"]
    
    # Follow-up query using suggested question
    suggested = response1["llm_processing"]["suggested_questions"][0]
    response2 = llm_service.process_query(
        suggested,
        conversation,
        "english"
    )
    
    assert len(response2["response"]) > 0
    assert "llm_processing" in response2
    
    # Test language switching mid-conversation
    response3 = llm_service.process_query(
        "Покажите бюджет проектов",
        conversation,
        "russian"
    )
    
    assert len(response3["response"]) > 0
    assert any(word in response3["response"].lower() for word in ["бюджет", "стоимость", "финансирование"])

if __name__ == "__main__":
    pytest.main(["-v", "test_llm_integration.py"]) 