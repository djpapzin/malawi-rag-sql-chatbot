# check_db.py
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    try:
        conn = sqlite3.connect('malawi_projects1.db')
        cursor = conn.cursor()
        
        # Check projects table
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        logger.info(f"Total projects: {count}")
        
        if count > 0:
            # Get sample data
            cursor.execute("""
                SELECT id, project_name, sector, region, district, status, start_date 
                FROM projects LIMIT 3
            """)
            rows = cursor.fetchall()
            logger.info("\nSample projects:")
            for row in rows:
                logger.info(f"ID: {row[0]}")
                logger.info(f"Name: {row[1]}")
                logger.info(f"Sector: {row[2]}")
                logger.info(f"Location: {row[3]}, {row[4]}")
                logger.info(f"Status: {row[5]}")
                logger.info(f"Start Date: {row[6]}")
                logger.info("-" * 50)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_database()