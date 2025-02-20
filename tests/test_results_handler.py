import os
import pytest
from datetime import datetime
from typing import Dict, Any, List

class TestResultsHandler:
    """Handler for saving test results in markdown format"""
    
    def __init__(self, output_dir: str = "test_results"):
        """Initialize the test results handler"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def _format_test_case(self, test_case: Dict[str, Any]) -> str:
        """Format a single test case result"""
        result = f"### {test_case['name']}\n\n"
        
        # Add description if available
        if test_case.get('description'):
            result += f"**Description**: {test_case['description']}\n\n"
            
        # Add test data
        if test_case.get('test_data'):
            result += "**Test Data**:\n```python\n"
            result += str(test_case['test_data'])
            result += "\n```\n\n"
            
        # Add expected results
        if test_case.get('expected'):
            result += "**Expected Results**:\n```\n"
            result += str(test_case['expected'])
            result += "\n```\n\n"
            
        # Add actual results
        if test_case.get('actual'):
            result += "**Actual Results**:\n```\n"
            result += str(test_case['actual'])
            result += "\n```\n\n"
            
        # Add status
        status_emoji = "✅" if test_case.get('passed', False) else "❌"
        result += f"**Status**: {status_emoji} {'PASSED' if test_case.get('passed', False) else 'FAILED'}\n\n"
        
        # Add error message if failed
        if test_case.get('error'):
            result += "**Error**:\n```\n"
            result += str(test_case['error'])
            result += "\n```\n\n"
            
        return result
    
    def save_test_results(self, test_name: str, test_cases: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
        """Save test results to a markdown file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Test Results: {test_name}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write summary
            f.write("## Summary\n\n")
            f.write(f"- Total Tests: {summary['total']}\n")
            f.write(f"- Passed: {summary['passed']}\n")
            f.write(f"- Failed: {summary['failed']}\n")
            f.write(f"- Execution Time: {summary['execution_time']:.2f} seconds\n\n")
            
            # Write test cases
            f.write("## Test Cases\n\n")
            for test_case in test_cases:
                f.write(self._format_test_case(test_case))
                
        return filepath

@pytest.fixture
def results_handler():
    """Fixture to provide a test results handler"""
    return TestResultsHandler() 