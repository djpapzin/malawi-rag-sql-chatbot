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
        self.db_url = os.getenv("DATABASE_URL", "sqlite:///malawi_projects.db")
        logger.info(f"Initializing DatabaseService with {self.db_url}")
        
        # Extract SQLite path from URL
        self.db_path = self.db_url.replace("sqlite:///", "")
        
        # Initialize database if it doesn't exist
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with sample data if it doesn't exist"""
        if not os.path.exists(self.db_path):
            logger.info("Creating new database with sample data")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    region TEXT NOT NULL,
                    status TEXT NOT NULL,
                    budget REAL NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    description TEXT
                )
            """)
            
            # Insert sample data
            sample_data = [
                ("Lilongwe Education Center", "Education", "Central", "Active", 2500000.00, "2023-01-01", "2024-12-31", "New education center with modern facilities"),
                ("Mzuzu Technical College", "Education", "Northern", "Planning", 3500000.00, "2024-03-01", "2025-06-30", "Technical training institute"),
                ("Zomba Primary School Renovation", "Education", "Southern", "Completed", 800000.00, "2022-06-01", "2023-05-31", "Complete renovation of existing school"),
                ("Karonga Teacher Training", "Education", "Northern", "Active", 1500000.00, "2023-07-01", "2024-08-31", "Teacher training facility"),
                ("Blantyre Science Labs", "Education", "Southern", "Active", 1200000.00, "2023-04-01", "2024-03-31", "Modern science laboratories")
            ]
            
            cursor.executemany("""
                INSERT INTO projects (name, sector, region, status, budget, start_date, end_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_data)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized with sample data")
    
    async def check_connection(self) -> bool:
        """Check database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    async def execute_query(self, query: str) -> Dict:
        """Execute a natural language query"""
        try:
            # For demo purposes, return education projects
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get education projects
            cursor.execute("""
                SELECT name, region, status, budget, start_date, end_date, description
                FROM projects
                WHERE sector = 'Education'
                ORDER BY region, status
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
            
            # Return formatted response
            return {
                "response": f"Found {len(projects)} education projects:\n\n" + "\n\n".join([
                    f"Project: {p['name']}\n"
                    f"Region: {p['region']}\n"
                    f"Status: {p['status']}\n"
                    f"Budget: MK {p['budget']:,.2f}\n"
                    f"Timeline: {p['start_date']} to {p['end_date']}\n"
                    f"Description: {p['description']}"
                    for p in projects
                ])
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                "error": f"Error executing query: {str(e)}"
            } 