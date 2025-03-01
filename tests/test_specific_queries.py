import pytest
import json
import requests
from typing import Dict, Any

BASE_URL = "http://154.0.164.254:5000/api/rag-sql-chatbot"

def make_chat_request(message: str) -> Dict[str, Any]:
    """Helper function to make chat requests"""
    response = requests.post(
        f"{BASE_URL}/chat",
        headers={"Content-Type": "application/json"},
        json={"message": message}
    )
    return response.json()

def test_health_check():
    """Verify health endpoint is working"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "RAG SQL Chatbot is running"

class TestDirectProjectQueries:
    """Test queries that directly reference project names"""
    
    def test_exact_project_name(self):
        """Test query with exact project name"""
        # First get a list of projects
        response = make_chat_request("List all projects in Lilongwe")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert result["type"] == "text"
        assert "MWK" in result["message"]

    def test_project_status_query(self):
        """Test query about project status"""
        response = make_chat_request("What projects are currently ongoing in Lilongwe?")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert "ongoing" in result["message"].lower()

class TestProjectAttributeQueries:
    """Test queries that search by project attributes"""
    
    def test_budget_query(self):
        """Test query filtering by budget"""
        response = make_chat_request("Show me projects in Lilongwe with budget over 200 million MWK")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert "222,903,780" in result["message"] or "200,000,000" in result["message"]
        
    def test_completion_query(self):
        """Test query filtering by location"""
        response = make_chat_request("List all health center projects in Lilongwe")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert "health" in result["message"].lower()

class TestContextualQueries:
    """Test follow-up queries that require context"""
    
    def test_followup_query(self):
        """Test follow-up query about projects"""
        # First query about projects
        response = make_chat_request("What projects are currently ongoing in Lilongwe?")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert result["type"] == "text"
        
        # Follow-up query
        response = make_chat_request("What is the total budget for these projects?")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert result["type"] == "text"
        assert "MWK" in result["message"]

class TestSpecificDetailQueries:
    """Test queries about specific project details"""
    
    def test_budget_range_query(self):
        """Test query about project budgets in a range"""
        response = make_chat_request("Show me projects in Lilongwe with budget between 150 million and 200 million")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert any(budget in result["message"] for budget in ["195,000,000", "170,000,000", "168,912,000", "165,000,000", "155,000,000"])
        
    def test_sector_query(self):
        """Test query about projects in a specific sector"""
        response = make_chat_request("List all bridge construction projects in Lilongwe")
        assert response["metadata"]["total_results"] >= 1
        result = response["results"][0]
        assert "bridge" in result["message"].lower()

class TestErrorHandling:
    """Test error handling for specific queries"""
    
    def test_nonexistent_project(self):
        """Test query for non-existent project"""
        response = make_chat_request("Show details for Non Existent Project XYZ")
        assert response["metadata"]["total_results"] == 0
        result = response["results"][0]
        assert "no" in result["message"].lower() or "not found" in result["message"].lower()
        
    def test_ambiguous_query(self):
        """Test handling of ambiguous project references"""
        response = make_chat_request("Show me health center projects in Lilongwe")
        assert response["metadata"]["total_results"] > 1
        result = response["results"][0]
        assert any(x in result["message"].lower() for x in ["health centre", "health center"])

if __name__ == "__main__":
    # Run health check first
    print("Running health check...")
    test_health_check()
    print("Health check passed!")
    
    # Create test instances
    test_direct = TestDirectProjectQueries()
    test_attrs = TestProjectAttributeQueries()
    test_context = TestContextualQueries()
    test_details = TestSpecificDetailQueries()
    test_errors = TestErrorHandling()
    
    # Run all tests
    print("\nTesting direct project queries...")
    test_direct.test_exact_project_name()
    test_direct.test_project_status_query()
    
    print("\nTesting project attribute queries...")
    test_attrs.test_budget_query()
    test_attrs.test_completion_query()
    
    print("\nTesting contextual queries...")
    test_context.test_followup_query()
    
    print("\nTesting specific detail queries...")
    test_details.test_budget_range_query()
    test_details.test_sector_query()
    
    print("\nTesting error handling...")
    test_errors.test_nonexistent_project()
    test_errors.test_ambiguous_query()
    
    print("\nAll tests completed successfully!")
