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
        
        # Test each query type
        test_queries = [
            "SELECT COUNT(*) FROM proj_dashboard WHERE district = 'lilongwe';",
            "SELECT SUM(budget) FROM proj_dashboard;",
            "SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure';",
            "SELECT * FROM proj_dashboard WHERE completionpercentage > 50;",
            "SELECT district, AVG(budget) FROM proj_dashboard GROUP BY district;"
        ]
        
        for query in test_queries:
            logger.info(f"\nTesting query: {query}")
            try:
                cursor.execute(query)
                result = cursor.fetchall()
                logger.info(f"Result: {result}")
            except Exception as e:
                logger.error(f"Query failed: {str(e)}")
                
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Checking database structure...")
    check_db_structure()
    logger.info("\nTesting query...")
    test_query() 