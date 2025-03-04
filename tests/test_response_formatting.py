import unittest
import pandas as pd
from datetime import datetime
from app.response_generator import ResponseGenerator

class TestResponseFormatting(unittest.TestCase):
    def setUp(self):
        self.response_generator = ResponseGenerator()
        
        # Sample data for testing
        self.sample_project_data = {
            'PROJECTNAME': 'Lilongwe Primary School Renovation',
            'FISCALYEAR': '2023-2024',
            'DISTRICT': 'Lilongwe',
            'TOTALBUDGET': 120000000.00,
            'PROJECTSTATUS': 'In progress',
            'PROJECTSECTOR': 'Education',
            'CONTRACTORNAME': 'Malawi Construction Ltd.',
            'STARTDATE': '2023-05-15',
            'TOTALEXPENDITURETODATE': 75000000.00,
            'FUNDINGSOURCE': 'World Bank Education Grant',
            'PROJECTCODE': 'EDU-LLW-2023-005',
            'LASTVISIT': '2024-01-12'
        }
        
        # Create sample DataFrame for multiple projects
        self.multiple_projects = pd.DataFrame([
            {
                'PROJECTNAME': 'Lilongwe Primary School Renovation',
                'FISCALYEAR': '2023-2024',
                'DISTRICT': 'Lilongwe',
                'TOTALBUDGET': 120000000.00,
                'PROJECTSTATUS': 'In progress',
                'PROJECTSECTOR': 'Education'
            },
            {
                'PROJECTNAME': 'Zomba District Hospital',
                'FISCALYEAR': '2023-2024',
                'DISTRICT': 'Zomba',
                'TOTALBUDGET': 450000000.00,
                'PROJECTSTATUS': 'Planning',
                'PROJECTSECTOR': 'Health'
            }
        ])

    def test_general_query_format(self):
        """Test that general queries show exactly 6 required fields"""
        result = self.response_generator._format_project_list(self.multiple_projects)
        
        # Verify the response contains expected fields
        self.assertIn("Found 2 projects:", result)
        self.assertIn("Project 1:", result)
        self.assertIn("Project 2:", result)
        
        # Check for all required fields in correct format
        required_fields = [
            "Name: ",
            "Fiscal Year: ",
            "Location: ",
            "Budget: MWK",
            "Status: ",
            "Sector: "
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
            
        # Verify no extra fields are present
        self.assertNotIn("Contractor name:", result)
        self.assertNotIn("Contract start date:", result)
        
        # Verify proper currency formatting
        self.assertIn("MWK 120,000,000.00", result)

    def test_specific_query_format(self):
        """Test that specific queries show exactly 12 required fields"""
        project_series = pd.Series(self.sample_project_data)
        result = self.response_generator._format_specific_project(project_series)
        
        # Verify the response contains "Project Details:" header
        self.assertIn("Project Details:", result)
        
        # Check for all 12 required fields
        required_fields = [
            "Name of project: ",
            "Fiscal year: ",
            "Location: ",
            "Budget: MWK",
            "Status: ",
            "Contractor name: ",
            "Contract start date: ",
            "Expenditure to date: MWK",
            "Sector: ",
            "Source of funding: ",
            "Project code: ",
            "Date of last Council monitoring visit: "
        ]
        
        for field in required_fields:
            self.assertIn(field, result)
            
        # Verify proper date formatting
        self.assertIn("May 15, 2023", result)
        self.assertIn("January 12, 2024", result)
        
        # Verify proper currency formatting
        self.assertIn("MWK 120,000,000.00", result)
        self.assertIn("MWK 75,000,000.00", result)

    def test_pagination_message(self):
        """Test pagination message when there are more results than shown"""
        # Create a larger dataset
        large_df = pd.concat([self.multiple_projects] * 6, ignore_index=True)  # 12 projects
        
        # Test with query_info indicating more results
        query_info = {'total_count': 15}
        result = self.response_generator._format_project_list(large_df[:10], query_info)
        
        # Verify pagination message
        self.assertIn("Found 15 projects, showing first 10:", result)

    def test_null_value_handling(self):
        """Test handling of null/missing values"""
        # Create data with some null values
        project_with_nulls = self.sample_project_data.copy()
        project_with_nulls['CONTRACTORNAME'] = None
        project_with_nulls['TOTALEXPENDITURETODATE'] = None
        
        project_series = pd.Series(project_with_nulls)
        result = self.response_generator._format_specific_project(project_series)
        
        # Verify null values are displayed as "Not available"
        self.assertIn("Contractor name: Not available", result)
        self.assertIn("Expenditure to date: Not available", result)

if __name__ == '__main__':
    unittest.main() 