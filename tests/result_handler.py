import json
from datetime import datetime
import os

class ResultHandler:
    def __init__(self):
        self.results = []
        
    def add_result(self, query, status_code, response_data, timestamp):
        """Add a test result"""
        self.results.append({
            "query": query,
            "status_code": status_code,
            "response_data": response_data,
            "timestamp": timestamp
        })
        
    def save_results(self, filename):
        """Save results to a markdown file"""
        if not filename.endswith('.md'):
            filename += '.md'
            
        with open(filename, 'w') as f:
            f.write("# API Test Results\n\n")
            f.write(f"Test run at: {datetime.now().isoformat()}\n\n")
            
            for result in self.results:
                f.write(f"## Query: {result['query']}\n")
                f.write(f"Status Code: {result['status_code']}\n")
                f.write(f"Timestamp: {result['timestamp']}\n")
                f.write("\nResponse Data:\n")
                f.write("```json\n")
                f.write(json.dumps(result['response_data'], indent=2))
                f.write("\n```\n\n")
                f.write("---\n\n")
