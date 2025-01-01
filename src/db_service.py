"""
Database Service for RAG SQL Chatbot
"""

import os
import logging
import sqlite3
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """Handler for database operations"""
    
    def __init__(self):
        """Initialize Database Service"""
        self.db_path = "malawi_projects.db"
        logger.info(f"Initializing DatabaseService with {self.db_path}")
    
    async def check_connection(self) -> bool:
        """Check database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"Database connection successful. Found {count} projects.")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    async def execute_query(self, query: str) -> Dict:
        """Execute a natural language query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all projects
            cursor.execute("""
                SELECT name, sector, district, status, budget, start_date, end_date, description
                FROM projects
                ORDER BY district, sector
            """)
            
            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            # Format results
            projects = []
            for row in results:
                project = dict(zip(columns, row))
                projects.append(project)
            
            conn.close()
            
            # Format response with only Project and Location information
            response = "Here are the relevant projects:\n\n"
            for p in projects:
                response += f"1. Project: {p['name']}\n"
                response += f"   Description: {p['description']}\n"
                response += f"2. Location: {p['district']} District\n\n"
            
            return {
                "response": response,
                "projects": projects
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                "error": f"Error executing query: {str(e)}",
                "response": "I apologize, but I encountered an error processing your query. Please try again."
            } 