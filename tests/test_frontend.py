import unittest
import requests
import json

class TestRAGSQLChatbot(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5000"  # Update this to match your API server port
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def test_multiple_projects_response(self):
        """Test the response when querying multiple projects"""
        query = "Show me all infrastructure projects in Malawi"
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={"message": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn('answer', data)
        # Check if response contains project information
        self.assertTrue(
            any(word in data['answer'].lower() for word in ['project', 'infrastructure']),
            "Response should contain project information"
        )

    def test_project_list_view(self):
        """Test the project list functionality"""
        query = "List all education projects"
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={"message": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if response contains education projects
        self.assertTrue(
            any(word in data['answer'].lower() for word in ['education', 'project']),
            "Response should contain education projects"
        )

    def test_project_details_view(self):
        """Test the detailed project view"""
        query = "Tell me about the Staff House project"
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={"message": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if response contains project details
        self.assertTrue(
            'staff house' in data['answer'].lower(),
            "Response should contain Staff House project details"
        )

    def test_language_support(self):
        """Test language support"""
        query = "Покажите инфраструктурные проекты в Малави"
        response = requests.post(
            f"{self.base_url}/chat",
            headers=self.headers,
            json={
                "message": query,
                "language": "ru"  # Specify Russian language
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if response is in Russian
        self.assertTrue(
            any(word in data['answer'].lower() for word in ['проекты', 'бюджет']),
            "Response should be in Russian"
        )

if __name__ == "__main__":
    unittest.main()
