import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_structure():
    try:
        # Connect to the database
        conn = sqlite3.connect('malawi_projects1.db')
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info("Database tables:")
        for table in tables:
            table_name = table[0]
            logger.info(f"\nTable: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            logger.info("Columns:")
            for col in columns:
                logger.info(f"  {col[1]} ({col[2]})")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            sample = cursor.fetchone()
            if sample:
                logger.info(f"Sample row: {sample}")
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

def test_query():
    try:
        conn = sqlite3.connect('malawi_projects1.db')
        cursor = conn.cursor()
        
        # Test the problematic query
        test_query = """
        SELECT p.id, p.title, p.description, p.location, p.status, p.start_date, p.end_date, p.budget
        FROM projects p
        WHERE 1=1
        ORDER BY p.start_date DESC
        LIMIT 5
        """
        
        try:
            cursor.execute(test_query)
            results = cursor.fetchall()
            logger.info(f"Query results: {results}")
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            
            # Let's try a simpler query to see the actual structure
            cursor.execute("SELECT * FROM projects LIMIT 1")
            columns = [description[0] for description in cursor.description]
            logger.info(f"Actual columns: {columns}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Checking database structure...")
    check_db_structure()
    logger.info("\nTesting query...")
    test_query() 