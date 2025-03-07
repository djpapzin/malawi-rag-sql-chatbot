import unittest
import pandas as pd
from app.response_formatter import ResponseFormatter

class TestResponseFormatter(unittest.TestCase):
    def setUp(self):
        self.response_formatter = ResponseFormatter()
        
        # Sample data for testing
        self.sample_project_data = {
            'PROJECTNAME': 'Lilongwe Primary School Renovation',
            'PROJECTCODE': 'EDU-LLW-2023-005',
            'PROJECTSECTOR': 'Education',
            'PROJECTSTATUS': 'In progress',
            'DISTRICT': 'Lilongwe',
            'TOTALBUDGET': 120000000.00,
            'COMPLETIONPERCENTAGE': 65,
            'TRADITIONALAUTHORITY': 'Lilongwe Central',
            'STARTDATE': '2023-05-15',
            'COMPLETIONESTIDATE': '2024-05-15',
            'FUNDINGSOURCE': 'World Bank Education Grant',
            'TOTALEXPENDITURETODATE': 75000000.00,
            'CONTRACTORNAME': 'Malawi Construction Ltd.',
            'SIGNINGDATE': '2023-04-01',
            'LASTVISIT': '2024-01-12',
            'PROJECTDESC': 'Renovation of classrooms and administrative buildings'
        }

    def test_format_response_for_specific_query(self):
        """Test that format_response correctly uses format_specific_project for specific queries"""
        # Format the response with query_type="specific"
        result = self.response_formatter.format_response(
            query_type="specific", 
            results=[self.sample_project_data], 
            parameters={}
        )
        
        # Check that the response has the correct format from format_specific_project
        self.assertEqual(result["type"], "specific")
        self.assertIn("data", result)
        
        # Verify the detailed sections are present
        self.assertIn("Core Information", result["data"])
        self.assertIn("Location", result["data"])
        self.assertIn("Financial Details", result["data"])
        
        # Verify specific fields are correctly extracted
        core_info = result["data"].get("Core Information", {})
        self.assertIn("Project Name", core_info)
        self.assertEqual(core_info["Project Name"], "Lilongwe Primary School Renovation")
        self.assertIn("Sector", core_info)
        self.assertEqual(core_info["Sector"], "Education")
        
        # Check financial details
        financial = result["data"].get("Financial Details", {})
        self.assertIn("Total Budget", financial)
        self.assertEqual(financial["Total Budget"], "MWK 120,000,000.00")

if __name__ == '__main__':
    unittest.main() 