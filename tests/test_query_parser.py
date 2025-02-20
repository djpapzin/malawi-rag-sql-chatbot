import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.query_parser import QueryParser

class TestQueryParser(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_project_code_matching(self):
        """Test different project code formats"""
        test_cases = [
            # Full codes with exact matches
            ("MW-CR-DO", "AND PROJECTCODE = 'MW-CR-DO'"),
            ("mw-cr-do", "AND PROJECTCODE = 'MW-CR-DO'"),
            
            # Regional codes with LIKE patterns
            ("MW-CR", "AND PROJECTCODE LIKE 'MW-CR-%'"),
            ("mw-cr", "AND PROJECTCODE LIKE 'MW-CR-%'"),
            
            # Partial codes with MW prefix added
            ("CR-DO", "AND PROJECTCODE LIKE 'MW-CR-DO'"),
            ("cr-do", "AND PROJECTCODE LIKE 'MW-CR-DO'"),
            
            # Region only with MW prefix and wildcard
            ("CR", "AND PROJECTCODE LIKE 'MW-CR-%'"),
            ("cr", "AND PROJECTCODE LIKE 'MW-CR-%'"),
            
            # Invalid codes should return empty string
            ("XX-YY-ZZ", ""),
            ("123", ""),
        ]
        
        for code, expected in test_cases:
            with self.subTest(code=code):
                result = self.parser._build_project_code_query(code)
                self.assertEqual(result.strip(), expected.strip())

    def test_project_code_extraction(self):
        """Test extraction of project codes from queries"""
        test_cases = [
            # Full project codes
            ("show project MW-CR-DO", "MW-CR-DO"),
            ("what is project mw-cr-do?", "MW-CR-DO"),
            ("tell me about project code MW-CR-DO", "MW-CR-DO"),
            
            # Regional codes
            ("show projects in MW-CR", "MW-CR"),
            ("list MW-CR projects", "MW-CR"),
            
            # Partial codes
            ("show all CR-DO projects", "CR-DO"),
            ("find cr-do details", "CR-DO"),
            
            # Region codes
            ("list projects with code CR", "CR"),
            ("show CR region projects", "CR"),
            
            # Invalid or no codes
            ("show me all projects", ""),
            ("what about the market?", ""),
        ]
        
        for query, expected_code in test_cases:
            with self.subTest(query=query):
                code = self.parser._extract_project_code(query)
                self.assertEqual(code.upper(), expected_code.upper())

    def test_result_limiting(self):
        """Test result limiting and sorting"""
        base_query = "SELECT * FROM projects WHERE 1=1"
        
        # Test specific query limiting
        specific_result = self.parser._add_result_limits(base_query, "specific")
        self.assertIn("LIMIT 1", specific_result)
        self.assertIn("ORDER BY", specific_result)
        self.assertIn("PROJECTSTATUS", specific_result)
        
        # Test general query limiting
        general_result = self.parser._add_result_limits(base_query, "general")
        self.assertIn("LIMIT 10", general_result)
        self.assertIn("ORDER BY", general_result)
        self.assertIn("COMPLETIONPERCENTAGE", general_result)

    def test_query_parsing(self):
        """Test overall query parsing"""
        test_cases = [
            # Project code queries
            {
                "input": "show project MW-CR-DO",
                "expected_type": "specific",
                "should_have": ["AND PROJECTCODE = 'MW-CR-DO'", "LIMIT 1"]
            },
            # Regional code queries
            {
                "input": "show projects in MW-CR",
                "expected_type": "specific",
                "should_have": ["AND PROJECTCODE LIKE 'MW-CR-%'", "LIMIT 1"]
            },
            # General queries
            {
                "input": "show all projects in Central Region",
                "expected_type": "general",
                "should_have": ["LIMIT 10", "COMPLETIONPERCENTAGE"]
            },
            # Invalid queries
            {
                "input": "",
                "expected_type": "general",
                "should_have": ["LIMIT 10"]
            }
        ]
        
        for case in test_cases:
            with self.subTest(query=case["input"]):
                result = self.parser.parse_query(case["input"])
                self.assertEqual(result["type"], case["expected_type"])
                for phrase in case["should_have"]:
                    self.assertIn(phrase, result["query"])

if __name__ == "__main__":
    unittest.main()
