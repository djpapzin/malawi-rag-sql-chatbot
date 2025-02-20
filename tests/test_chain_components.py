import pytest
from src.llm_chain import ProjectQueryChain
from langchain.memory import ConversationBufferMemory
import os
import json

@pytest.fixture
def chain():
    """Initialize chain for testing"""
    return ProjectQueryChain()

def test_llm_initialization(chain):
    """Test LLM initialization and basic functionality"""
    assert chain.together is not None
    assert chain.db is not None
    assert isinstance(chain.memory, ConversationBufferMemory)

def test_sql_query_generation(chain):
    """Test SQL query generation for different types of queries"""
    test_cases = [
        {
            "question": "Show me all projects in Lilongwe District",
            "expected_columns": ["PROJECTNAME", "PROJECTCODE", "FISCALYEAR", "REGION", "DISTRICT"]
        },
        {
            "question": "What is the total budget for education projects?",
            "expected_columns": ["TOTALBUDGET", "PROJECTSECTOR"]
        },
        {
            "question": "Show details about CHILIPA CDSS GIRLS HOSTEL",
            "expected_columns": ["PROJECTNAME", "CONTRACTORNAME", "STARTDATE", "TOTALEXPENDITURETODATE"]
        }
    ]
    
    for case in test_cases:
        query = chain._generate_sql_query(case["question"])
        assert query.startswith("SELECT")
        for col in case["expected_columns"]:
            assert col in query

def test_memory_management(chain):
    """Test conversation memory management"""
    # Test initial state
    assert len(chain.memory.load_memory_variables({})["chat_history"]) == 0
    
    # Test memory after one interaction
    test_question = "Show projects in Lilongwe"
    result = chain.invoke(test_question)
    
    memory_vars = chain.memory.load_memory_variables({})
    assert len(memory_vars["chat_history"]) > 0
    
    # Verify memory contains both input and output
    chat_history = memory_vars["chat_history"]
    assert any(test_question in str(msg) for msg in chat_history)
    assert any(result["answer"] in str(msg) for msg in chat_history)

def test_chain_combination(chain):
    """Test the combination of multiple chain components"""
    # Test a sequence of related queries
    queries = [
        "How many projects are there in Lilongwe District?",
        "What is their total budget?",
        "Which of these projects has the highest budget?"
    ]
    
    previous_results = []
    for query in queries:
        result = chain.invoke(query)
        assert "sql_query" in result
        assert "answer" in result
        
        # Verify each query builds on previous context
        if previous_results:
            memory_vars = chain.memory.load_memory_variables({})
            chat_history = memory_vars["chat_history"]
            
            # Check if previous queries are in memory
            for prev_query in queries[:-1]:
                assert any(prev_query in str(msg) for msg in chat_history)
        
        previous_results.append(result)

def test_error_handling(chain):
    """Test error handling in different chain components"""
    # Test invalid SQL generation
    with pytest.raises(Exception):
        chain._generate_sql_query("")  # Empty query should raise error
    
    # Test invalid database query
    result = chain.invoke("Show me projects from invalid_district")
    assert "error" in result
    
    # Test memory persistence after error
    memory_vars = chain.memory.load_memory_variables({})
    assert len(memory_vars["chat_history"]) > 0  # Memory should still be updated

def test_result_formatting(chain):
    """Test result formatting for different types of responses"""
    # Test single result formatting
    single_result = [("Project A", "Code1", 2023)]
    formatted = chain._format_result(single_result)
    assert isinstance(formatted, str)
    assert "Project A" in formatted
    
    # Test multiple results formatting
    multiple_results = [
        ("Project A", "Code1", 2023),
        ("Project B", "Code2", 2023)
    ]
    formatted = chain._format_result(multiple_results)
    assert isinstance(formatted, str)
    assert "Project A" in formatted
    assert "Project B" in formatted
    
    # Test empty result formatting
    empty_result = []
    formatted = chain._format_result(empty_result)
    assert formatted == "No results found"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 