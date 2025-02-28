#!/usr/bin/env python3
import os
import sqlite3
import unittest
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestDatabaseMigration(unittest.TestCase):
    """Test the database migration from malawi_projects1.db to pmisProjects.db"""
    
    def setUp(self):
        """Set up the test case"""
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pmisProjects.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create test results directory if it doesn't exist
        self.results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_results")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after the test case"""
        self.conn.close()
    
    def test_database_exists(self):
        """Test that the database file exists"""
        self.assertTrue(os.path.exists(self.db_path), f"Database file {self.db_path} does not exist")
    
    def test_proj_dashboard_table_exists(self):
        """Test that the proj_dashboard table exists"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='proj_dashboard';")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "proj_dashboard table does not exist")
    
    def test_proj_dashboard_has_records(self):
        """Test that the proj_dashboard table has records"""
        self.cursor.execute("SELECT COUNT(*) FROM proj_dashboard;")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "proj_dashboard table has no records")
        print(f"proj_dashboard table has {count} records")
    
    def test_education_projects_exist(self):
        """Test that there are education projects in the database"""
        self.cursor.execute("SELECT COUNT(*) FROM proj_dashboard WHERE PROJECTSECTOR = 'Education';")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "No education projects found in the database")
        print(f"Found {count} education projects")
    
    def test_lilongwe_projects_exist(self):
        """Test that there are projects in Lilongwe"""
        self.cursor.execute("SELECT COUNT(*) FROM proj_dashboard WHERE DISTRICT = 'Lilongwe';")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "No projects found in Lilongwe")
        print(f"Found {count} projects in Lilongwe")
    
    def test_education_projects_in_lilongwe_exist(self):
        """Test that there are education projects in Lilongwe"""
        self.cursor.execute("SELECT COUNT(*) FROM proj_dashboard WHERE PROJECTSECTOR = 'Education' AND DISTRICT = 'Lilongwe';")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, "No education projects found in Lilongwe")
        print(f"Found {count} education projects in Lilongwe")
    
    def test_project_sectors(self):
        """Test that all expected project sectors exist"""
        self.cursor.execute("SELECT DISTINCT PROJECTSECTOR FROM proj_dashboard;")
        sectors = [row[0] for row in self.cursor.fetchall()]
        
        # Check that key sectors exist
        expected_sectors = [
            "Education", 
            "Health", 
            "Roads and bridges", 
            "Water and sanitation"
        ]
        
        for sector in expected_sectors:
            self.assertIn(sector, sectors, f"Expected sector '{sector}' not found in database")
        
        print(f"Found {len(sectors)} distinct project sectors")
    
    def test_districts(self):
        """Test that all expected districts exist"""
        self.cursor.execute("SELECT DISTINCT DISTRICT FROM proj_dashboard;")
        districts = [row[0] for row in self.cursor.fetchall()]
        
        # Check that key districts exist
        expected_districts = [
            "Lilongwe", 
            "Blantyre", 
            "Zomba", 
            "Mzimba"
        ]
        
        for district in expected_districts:
            self.assertIn(district, districts, f"Expected district '{district}' not found in database")
        
        print(f"Found {len(districts)} distinct districts")
    
    def test_generate_summary_report(self):
        """Generate a summary report of the database"""
        # Get project counts by sector
        self.cursor.execute("""
            SELECT PROJECTSECTOR, COUNT(*) as count, 
                   SUM(BUDGET) as total_budget,
                   AVG(BUDGET) as avg_budget
            FROM proj_dashboard 
            GROUP BY PROJECTSECTOR
        """)
        sector_data = self.cursor.fetchall()
        
        # Get project counts by district
        self.cursor.execute("""
            SELECT DISTRICT, COUNT(*) as count
            FROM proj_dashboard 
            GROUP BY DISTRICT
            ORDER BY count DESC
            LIMIT 10
        """)
        district_data = self.cursor.fetchall()
        
        # Get project counts by status
        self.cursor.execute("""
            SELECT PROJECTSTATUS, COUNT(*) as count
            FROM proj_dashboard 
            GROUP BY PROJECTSTATUS
        """)
        status_data = self.cursor.fetchall()
        
        # Create a report
        report = {
            "timestamp": datetime.now().isoformat(),
            "database_path": self.db_path,
            "total_projects": sum(row[1] for row in sector_data),
            "sectors": [
                {
                    "name": row[0] if row[0] is not None else "Unknown",
                    "count": row[1],
                    "total_budget": row[2] if row[2] is not None else 0,
                    "avg_budget": row[3] if row[3] is not None else 0
                }
                for row in sector_data
            ],
            "top_districts": [
                {
                    "name": row[0] if row[0] is not None else "Unknown",
                    "count": row[1]
                }
                for row in district_data
            ],
            "statuses": [
                {
                    "name": row[0] if row[0] is not None else "Unknown",
                    "count": row[1]
                }
                for row in status_data
            ]
        }
        
        # Save the report to a file
        report_path = os.path.join(self.results_dir, "database_migration_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Generated summary report at {report_path}")
        
        # Also save a text version for easier reading
        text_report_path = os.path.join(self.results_dir, "database_migration_report.txt")
        with open(text_report_path, 'w') as f:
            f.write("DATABASE MIGRATION REPORT\n")
            f.write("=======================\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Database: {self.db_path}\n")
            f.write(f"Total Projects: {report['total_projects']}\n\n")
            
            f.write("PROJECTS BY SECTOR\n")
            f.write("-----------------\n")
            for sector in report['sectors']:
                name = sector['name'] if sector['name'] is not None else "Unknown"
                f.write(f"{name}: {sector['count']} projects")
                if sector['total_budget']:
                    f.write(f", Total Budget: ${sector['total_budget']:,.2f}")
                if sector['avg_budget']:
                    f.write(f", Avg Budget: ${sector['avg_budget']:,.2f}")
                f.write("\n")
            
            f.write("\nTOP 10 DISTRICTS BY PROJECT COUNT\n")
            f.write("--------------------------------\n")
            for district in report['top_districts']:
                name = district['name'] if district['name'] is not None else "Unknown"
                f.write(f"{name}: {district['count']} projects\n")
            
            f.write("\nPROJECTS BY STATUS\n")
            f.write("-----------------\n")
            for status in report['statuses']:
                name = status['name'] if status['name'] is not None else "Unknown"
                f.write(f"{name}: {status['count']} projects\n")
        
        print(f"Generated text report at {text_report_path}")

if __name__ == "__main__":
    unittest.main() 