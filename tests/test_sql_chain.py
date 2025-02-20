"""Test suite for SQL Chain implementation"""

import pytest
import pytest_asyncio
from src.sql_chain import SQLChain
import asyncio
import os
from datetime import datetime
from tests.test_results_handler import TestResultsHandler

@pytest_asyncio.fixture
async def chain():
    """Initialize SQL Chain for testing"""
    chain = SQLChain()
    yield chain

@pytest.fixture
def results_handler():
    """Initialize test results handler"""
    return TestResultsHandler()

@pytest.mark.asyncio
async def test_sql_generation(chain, results_handler):
    """Test SQL query generation"""
    test_cases = []
    start_time = datetime.now()
    
    test_data = [
        {
            "question": "Show me all projects in Lilongwe District",
            "expected_columns": ["PROJECTNAME", "DISTRICT", "BUDGET"],
            "expected_conditions": ["DISTRICT", "Lilongwe", "LIMIT 100"]
        },
        {
            "question": "What is the total budget for education projects?",
            "expected_columns": ["PROJECTSECTOR", "BUDGET"],
            "expected_conditions": ["PROJECTSECTOR", "education", "GROUP BY"]
        },
        {
            "question": "Show details about CHILIPA CDSS GIRLS HOSTEL",
            "expected_columns": ["PROJECTNAME", "STARTDATE"],
            "expected_conditions": ["PROJECTNAME", "CHILIPA"]
        }
    ]
    
    for i, case in enumerate(test_data, 1):
        test_case = {
            "name": f"SQL Generation Test Case {i}",
            "description": f"Testing SQL generation for: {case['question']}",
            "test_data": case,
            "passed": True
        }
        
        try:
            query = await chain.generate_sql(case["question"])
            test_case["actual"] = query
            
            # Validate SQL structure
            assert query.lower().startswith("select"), "Query should start with SELECT"
            assert "from proj_dashboard" in query.lower(), "Query should reference proj_dashboard table"
            assert query.strip().endswith(";"), "Query should end with semicolon"
            
            # Validate columns
            query_lower = query.lower()
            for col in case["expected_columns"]:
                assert col.lower() in query_lower, f"Missing column: {col}"
                
            # Validate conditions
            for condition in case["expected_conditions"]:
                assert condition.lower() in query_lower, f"Missing condition: {condition}"
                
        except Exception as e:
            test_case["passed"] = False
            test_case["error"] = str(e)
            
        test_cases.append(test_case)
    
    # Calculate summary
    execution_time = (datetime.now() - start_time).total_seconds()
    summary = {
        "total": len(test_cases),
        "passed": sum(1 for case in test_cases if case["passed"]),
        "failed": sum(1 for case in test_cases if not case["passed"]),
        "execution_time": execution_time
    }
    
    # Save results
    results_file = results_handler.save_test_results(
        "sql_generation",
        test_cases,
        summary
    )
    
    # Fail the test if any case failed
    assert summary["failed"] == 0, f"Some test cases failed. See {results_file} for details."

@pytest.mark.asyncio
async def test_results_processing(chain, results_handler):
    """Test processing of query results"""
    test_cases = []
    start_time = datetime.now()
    
    test_data = [
        {
            "question": "How many projects are there?",
            "query": "SELECT COUNT(*) as count FROM proj_dashboard;",
            "results": [(42,)],
            "expected_keywords": ["42", "projects"]
        },
        {
            "question": "What is the total budget?",
            "query": "SELECT SUM(budget) as total FROM proj_dashboard;",
            "results": [(1000000,)],
            "expected_keywords": ["1000000", "budget", "total"]
        }
    ]
    
    for i, case in enumerate(test_data, 1):
        test_case = {
            "name": f"Results Processing Test Case {i}",
            "description": f"Testing results processing for: {case['question']}",
            "test_data": case,
            "passed": True
        }
        
        try:
            answer = await chain.process_results(
                case["question"],
                case["query"],
                case["results"]
            )
            test_case["actual"] = answer
            
            # Validate answer contains expected keywords
            answer_lower = answer.lower()
            for keyword in case["expected_keywords"]:
                assert keyword.lower() in answer_lower, f"Missing keyword: {keyword}"
                
        except Exception as e:
            test_case["passed"] = False
            test_case["error"] = str(e)
            
        test_cases.append(test_case)
    
    # Calculate summary
    execution_time = (datetime.now() - start_time).total_seconds()
    summary = {
        "total": len(test_cases),
        "passed": sum(1 for case in test_cases if case["passed"]),
        "failed": sum(1 for case in test_cases if not case["passed"]),
        "execution_time": execution_time
    }
    
    # Save results
    results_file = results_handler.save_test_results(
        "results_processing",
        test_cases,
        summary
    )
    
    # Fail the test if any case failed
    assert summary["failed"] == 0, f"Some test cases failed. See {results_file} for details."

@pytest.mark.asyncio
async def test_complete_chain(chain, results_handler):
    """Test the complete SQL chain execution"""
    test_cases = []
    start_time = datetime.now()
    
    test_data = [
        {
            "question": "Show me all projects in Lilongwe District",
            "expected_fields": ["query", "results", "answer", "execution_time"]
        }
    ]
    
    for i, case in enumerate(test_data, 1):
        test_case = {
            "name": f"Complete Chain Test Case {i}",
            "description": f"Testing complete chain execution for: {case['question']}",
            "test_data": case,
            "passed": True
        }
        
        try:
            result = await chain.run(case["question"])
            test_case["actual"] = result
            
            # Validate response structure
            for field in case["expected_fields"]:
                assert field in result, f"Missing field: {field}"
            
            # Validate query
            assert result["query"].lower().startswith("select"), "Query should start with SELECT"
            assert "proj_dashboard" in result["query"].lower(), "Query should reference proj_dashboard table"
            
            # Validate execution time
            assert isinstance(result["execution_time"], float), "Execution time should be float"
            assert 0 < result["execution_time"] < 10, "Execution time should be reasonable"
            
            # Validate answer
            assert isinstance(result["answer"], str), "Answer should be string"
            assert len(result["answer"]) > 0, "Answer should not be empty"
            
        except Exception as e:
            test_case["passed"] = False
            test_case["error"] = str(e)
            
        test_cases.append(test_case)
    
    # Calculate summary
    execution_time = (datetime.now() - start_time).total_seconds()
    summary = {
        "total": len(test_cases),
        "passed": sum(1 for case in test_cases if case["passed"]),
        "failed": sum(1 for case in test_cases if not case["passed"]),
        "execution_time": execution_time
    }
    
    # Save results
    results_file = results_handler.save_test_results(
        "complete_chain",
        test_cases,
        summary
    )
    
    # Fail the test if any case failed
    assert summary["failed"] == 0, f"Some test cases failed. See {results_file} for details."

@pytest.mark.asyncio
async def test_error_handling(chain, results_handler):
    """Test error handling in the chain"""
    test_cases = []
    start_time = datetime.now()
    
    test_data = [
        {
            "name": "Empty Question",
            "question": "",
            "expected_error": "Empty question provided"
        },
        {
            "name": "SQL Injection Attempt",
            "question": "DROP TABLE proj_dashboard",
            "expected_error": "injection"
        },
        {
            "name": "Malformed Question",
            "question": "12345",
            "expected_error": "malformed"
        }
    ]
    
    for case in test_data:
        test_case = {
            "name": f"Error Handling: {case['name']}",
            "description": f"Testing error handling for: {case['question']}",
            "test_data": case,
            "passed": True
        }
        
        try:
            result = await chain.run(case["question"])
            test_case["actual"] = result
            
            # Validate error response
            assert "error" in result, "Should contain error field"
            assert result["query"] is None, "Query should be None"
            assert result["results"] is None, "Results should be None"
            assert case["expected_error"].lower() in result["error"].lower(), f"Error should contain: {case['expected_error']}"
            
        except Exception as e:
            test_case["passed"] = False
            test_case["error"] = str(e)
            
        test_cases.append(test_case)
    
    # Calculate summary
    execution_time = (datetime.now() - start_time).total_seconds()
    summary = {
        "total": len(test_cases),
        "passed": sum(1 for case in test_cases if case["passed"]),
        "failed": sum(1 for case in test_cases if not case["passed"]),
        "execution_time": execution_time
    }
    
    # Save results
    results_file = results_handler.save_test_results(
        "error_handling",
        test_cases,
        summary
    )
    
    # Fail the test if any case failed
    assert summary["failed"] == 0, f"Some test cases failed. See {results_file} for details."

@pytest.mark.asyncio
async def test_column_selection(chain, results_handler):
    """Test column selection logic"""
    test_cases = []
    start_time = datetime.now()
    
    test_data = [
        {
            "name": "Standard Columns",
            "question": "Show all projects",
            "expected_columns": chain.standard_columns,
            "unexpected_columns": chain.specific_columns
        },
        {
            "name": "Specific Project Columns",
            "question": "Show details about MW-123",
            "expected_columns": chain.standard_columns + chain.specific_columns,
            "unexpected_columns": []
        },
        {
            "name": "Project Code Columns",
            "question": "Tell me about project 5f0c",
            "expected_columns": chain.standard_columns + chain.specific_columns,
            "unexpected_columns": []
        }
    ]
    
    for case in test_data:
        test_case = {
            "name": f"Column Selection: {case['name']}",
            "description": f"Testing column selection for: {case['question']}",
            "test_data": case,
            "passed": True
        }
        
        try:
            columns = chain._get_columns_for_query(case["question"])
            test_case["actual"] = columns
            
            # Validate expected columns are present
            for col in case["expected_columns"]:
                assert col in columns, f"Missing expected column: {col}"
                
            # Validate unexpected columns are not present
            for col in case["unexpected_columns"]:
                assert col not in columns, f"Found unexpected column: {col}"
                
        except Exception as e:
            test_case["passed"] = False
            test_case["error"] = str(e)
            
        test_cases.append(test_case)
    
    # Calculate summary
    execution_time = (datetime.now() - start_time).total_seconds()
    summary = {
        "total": len(test_cases),
        "passed": sum(1 for case in test_cases if case["passed"]),
        "failed": sum(1 for case in test_cases if not case["passed"]),
        "execution_time": execution_time
    }
    
    # Save results
    results_file = results_handler.save_test_results(
        "column_selection",
        test_cases,
        summary
    )
    
    # Fail the test if any case failed
    assert summary["failed"] == 0, f"Some test cases failed. See {results_file} for details."

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 