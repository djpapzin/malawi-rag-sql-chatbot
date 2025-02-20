import unittest
from fastapi.testclient import TestClient
from app.main import app
import json

class TestRAGSQLChatbot(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def test_multiple_projects_response(self):
        """Test the response when querying multiple projects"""
        query = "Show me all infrastructure projects in Malawi"
        response = self.client.post(
            "/chat",
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
        response = self.client.post(
            "/chat",
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
        """Test viewing details of a specific project"""
        query = "Show me details of project MW-CR-001"
        response = self.client.post(
            "/chat",
            headers=self.headers,
            json={"message": query}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if response contains project details
        self.assertTrue(
            any(word in data['answer'].lower() for word in ['mw-cr-001', 'project']),
            "Response should contain project details"
        )

    def test_language_support(self):
        """Test multilingual support"""
        # Test Russian query
        query_ru = "Покажите все проекты в Малави"
        response = self.client.post(
            "/chat",
            headers=self.headers,
            json={"message": query_ru, "language": "ru"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)

        # Test Uzbek query
        query_uz = "Malavida barcha loyihalarni ko'rsating"
        response = self.client.post(
            "/chat",
            headers=self.headers,
            json={"message": query_uz, "language": "uz"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)

if __name__ == "__main__":
    unittest.main()
