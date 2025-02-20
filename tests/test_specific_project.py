import requests
import json
from tabulate import tabulate
import logging
import os
from datetime import datetime
import pandas as pd
import csv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure results directory exists
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def save_json_results(data, filename):
    """Save results in JSON format"""
    filepath = os.path.join(RESULTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON results to {filepath}")

def save_markdown_results(content, filename):
    """Save results in Markdown format"""
    filepath = os.path.join(RESULTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Saved Markdown results to {filepath}")

def save_csv_results(data, filename):
    """Save results in CSV format"""
    filepath = os.path.join(RESULTS_DIR, filename)
    pd.DataFrame(data).to_csv(filepath, index=False)
    logger.info(f"Saved CSV results to {filepath}")

def test_specific_project():
    """Test detailed information retrieval for a specific project"""
    
    # Initialize QueryTester
    tester = QueryTester()
    
    # Test cases with specific projects
    test_cases = [
        {
            "query": "Tell me about 'CHILIPA CDSS GIRLS HOSTEL'",
            "description": "Exact Match - Full Project Name"
        },
        {
            "query": "Show details for project MW-CR-DO",
            "description": "Exact Match - Project Code"
        },
        {
            "query": "What is the status of 'Rehabilitation of Mzimba Hospital'",
            "description": "Exact Match - Another Project"
        },
        {
            "query": "Show me project code mw-cr-do",  # Test case-insensitive matching
            "description": "Case Sensitivity - Project Code"
        },
        {
            "query": "Tell me about 'chilipa cdss girls hostel'",  # Test case-insensitive matching
            "description": "Case Sensitivity - Project Name"
        },
        {
            "query": "Show details for 'Non-existent Project'",  # Should return 0
            "description": "Edge Case - Non-existent Project",
            "expected_count": 0
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        result = tester.test_query(
            query=test_case["query"],
            description=test_case["description"],
            expected_count=test_case.get("expected_count")
        )
        results.append(result)
    
    # Generate report
    report = tester.generate_report()
    
    # Save report
    with open('results/specific_project_query_test_results.md', 'w') as f:
        f.write(report)
    
    logger.info("\nTest results saved to results/specific_project_query_test_results.md")

if __name__ == "__main__":
    test_specific_project() 