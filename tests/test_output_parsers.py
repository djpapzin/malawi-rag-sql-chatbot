import pytest
from src.result_handler import ResultHandler, format_answer_section, get_column_names
import json
import csv
import os
from datetime import datetime

@pytest.fixture
def result_handler():
    """Initialize ResultHandler for testing"""
    handler = ResultHandler()
    # Ensure results directory exists
    os.makedirs(handler.base_dir, exist_ok=True)
    return handler

@pytest.fixture
def sample_data():
    """Sample project data for testing"""
    return [
        {
            "PROJECTNAME": "CHILIPA CDSS GIRLS HOSTEL",
            "PROJECTCODE": "MW-CR-001",
            "FISCALYEAR": "2023",
            "REGION": "Central",
            "DISTRICT": "Lilongwe",
            "TOTALBUDGET": 1000000,
            "PROJECTSTATUS": "In Progress",
            "PROJECTSECTOR": "Education",
            "CONTRACTORNAME": "Contractor A",
            "STARTDATE": "2023-01-01",
            "TOTALEXPENDITURETODATE": 500000,
            "FUNDINGSOURCE": "Government",
            "LASTVISIT": "2023-06-01"
        },
        {
            "PROJECTNAME": "ROAD REHABILITATION",
            "PROJECTCODE": "MW-SR-002",
            "FISCALYEAR": "2023",
            "REGION": "Southern",
            "DISTRICT": "Zomba",
            "TOTALBUDGET": 2000000,
            "PROJECTSTATUS": "Planning",
            "PROJECTSECTOR": "Transport",
            "CONTRACTORNAME": "Contractor B",
            "STARTDATE": "2023-02-01",
            "TOTALEXPENDITURETODATE": 0,
            "FUNDINGSOURCE": "World Bank",
            "LASTVISIT": "2023-06-01"
        }
    ]

def test_json_formatting(result_handler, sample_data):
    """Test JSON output formatting"""
    # Test with sample data
    sql_query = "SELECT * FROM proj_dashboard"
    answer = "Sample answer"
    files = result_handler.save_results(sql_query, sample_data, answer, "Show all projects")
    
    # Verify JSON file was created and has correct structure
    assert os.path.exists(files["json_file"])
    with open(files["json_file"], 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert "question" in data
        assert "sql_query" in data
        assert "results" in data
        assert "answer" in data
        assert "metadata" in data
        assert isinstance(data["metadata"]["generated_at"], str)
        
        # Verify data content
        assert len(data["results"]) == 2
        assert data["results"][0]["PROJECTNAME"] == "CHILIPA CDSS GIRLS HOSTEL"
        assert data["results"][1]["PROJECTNAME"] == "ROAD REHABILITATION"

def test_csv_formatting(result_handler, sample_data):
    """Test CSV output formatting"""
    # Test with sample data
    sql_query = "SELECT * FROM proj_dashboard"
    answer = "Sample answer"
    files = result_handler.save_results(sql_query, sample_data, answer)
    
    # Verify CSV file was created with correct structure
    assert os.path.exists(files["csv_file"])
    with open(files["csv_file"], 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        # Verify row count
        assert len(rows) == 2
        
        # Verify data content
        assert rows[0]["PROJECTNAME"] == "CHILIPA CDSS GIRLS HOSTEL"
        assert rows[0]["PROJECTCODE"] == "MW-CR-001"
        assert rows[0]["TOTALBUDGET"] == "MWK 1,000,000"  # Check formatting
        
        assert rows[1]["PROJECTNAME"] == "ROAD REHABILITATION"
        assert rows[1]["PROJECTCODE"] == "MW-SR-002"

def test_markdown_formatting(result_handler, sample_data):
    """Test Markdown output formatting"""
    sql_query = "SELECT * FROM proj_dashboard"
    answer = "Sample answer"
    files = result_handler.save_results(sql_query, sample_data, answer)
    
    # Verify Markdown file was created with correct structure
    assert os.path.exists(files["markdown_file"])
    with open(files["markdown_file"], 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for required sections
        assert "# Query Results" in content
        assert "## SQL Query" in content
        assert "## Results" in content
        assert "## Answer" in content
        
        # Check for table formatting
        assert "|" in content  # Table separator
        assert "PROJECTNAME" in content
        assert "PROJECTCODE" in content
        assert "CHILIPA CDSS GIRLS HOSTEL" in content
        assert "ROAD REHABILITATION" in content
        
        # Check for proper markdown table structure
        table_lines = [line for line in content.split('\n') if '|' in line]
        assert len(table_lines) >= 4  # Header, separator, and at least 2 data rows

def test_answer_formatting(result_handler, sample_data):
    """Test natural language answer formatting"""
    # Test specific project query
    columns = ["PROJECTNAME", "PROJECTCODE", "FISCALYEAR", "REGION", "DISTRICT",
               "TOTALBUDGET", "PROJECTSTATUS", "PROJECTSECTOR"]
    
    # Convert sample data to list of tuples for format_answer_section
    sample_tuples = [
        (
            data["PROJECTNAME"], data["PROJECTCODE"], data["FISCALYEAR"],
            data["REGION"], data["DISTRICT"], data["TOTALBUDGET"],
            data["PROJECTSTATUS"], data["PROJECTSECTOR"]
        )
        for data in sample_data
    ]
    
    # Test single project formatting
    single_project = [sample_tuples[0]]
    formatted_answer = format_answer_section(single_project, columns)
    
    # Verify answer structure for single project
    assert "* **Project Name**: CHILIPA CDSS GIRLS HOSTEL" in formatted_answer
    assert "* **Total Budget**: MWK 1,000,000" in formatted_answer
    assert "* **Project Status**: In Progress" in formatted_answer
    
    # Test multiple projects summary
    formatted_answer = format_answer_section(sample_tuples, columns)
    assert "* **Total Projects**: 2" in formatted_answer
    assert "* **Total Budget**: MWK 3,000,000" in formatted_answer
    assert "* **District Breakdown**:" in formatted_answer
    assert "  - Lilongwe: 1 project" in formatted_answer
    assert "  - Zomba: 1 project" in formatted_answer

def test_error_handling(result_handler):
    """Test error handling in output formatting"""
    # Test with invalid data
    invalid_data = None
    sql_query = "SELECT * FROM proj_dashboard"
    answer = "Error occurred"
    
    files = result_handler.save_results(sql_query, invalid_data, answer)
    assert "error" not in files  # Should handle gracefully
    
    # Test with empty results
    empty_data = []
    files = result_handler.save_results(sql_query, empty_data, answer)
    
    # Verify files are created even with empty data
    assert os.path.exists(files["markdown_file"])
    assert os.path.exists(files["csv_file"])
    assert os.path.exists(files["json_file"])
    
    # Check empty data handling in files
    with open(files["markdown_file"], 'r', encoding='utf-8') as f:
        content = f.read()
        assert "No results found" in content

def test_column_name_extraction():
    """Test SQL query column name extraction"""
    test_cases = [
        {
            "query": "SELECT PROJECTNAME, TOTALBUDGET FROM proj_dashboard",
            "expected": {"PROJECTNAME", "TOTALBUDGET"}
        },
        {
            "query": "SELECT * FROM proj_dashboard",
            "expected": {"*"}  # All columns selected
        },
        {
            "query": "SELECT COUNT(*) as total FROM proj_dashboard",
            "expected": {"total"}  # Use alias for aggregate queries
        },
        {
            "query": "SELECT p.PROJECTNAME, p.TOTALBUDGET FROM proj_dashboard p",
            "expected": {"PROJECTNAME", "TOTALBUDGET"}  # Strip table aliases
        },
        {
            "query": "SELECT DISTINCT REGION, COUNT(*) as count FROM proj_dashboard GROUP BY REGION",
            "expected": {"REGION", "count"}  # Handle GROUP BY queries
        }
    ]
    
    for case in test_cases:
        columns = get_column_names(case["query"])
        assert set(columns) == case["expected"], \
            f"Expected {case['expected']} for query '{case['query']}', got {columns}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])