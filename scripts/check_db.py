# check_db.py
import sqlite3
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    try:
        conn = sqlite3.connect('pmisProjects.db')
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"Database contains {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM '{table_name}';")
            count = cursor.fetchone()[0]
            print(f"- {table_name}: {count} records")

        # Check specific attributes
        if 'proj_dashboard' in [t[0] for t in tables]:
            print("\nChecking proj_dashboard table:")
            
            # Top 5 districts by project count
            cursor.execute("""
                SELECT DISTRICT, COUNT(*) as count 
                FROM proj_dashboard 
                GROUP BY DISTRICT 
                ORDER BY count DESC
                LIMIT 5
            """)
            districts = cursor.fetchall()
            print("\nTop 5 districts by project count:")
            for district in districts:
                print(f"- {district[0]}: {district[1]} projects")
            
            # Summary of budget by sector
            cursor.execute("""
                SELECT PROJECTSECTOR, 
                       COUNT(*) as count, 
                       SUM(BUDGET) as total_budget,
                       AVG(BUDGET) as avg_budget
                FROM proj_dashboard 
                GROUP BY PROJECTSECTOR
            """)
            sectors = cursor.fetchall()
            print("\nProject sectors summary:")
            for sector in sectors:
                print(f"- {sector[0]}: {sector[1]} projects, Total budget: ${sector[2]:,.2f}, Avg: ${sector[3]:,.2f}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database()