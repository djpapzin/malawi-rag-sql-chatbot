import logging
from app.query_parser import QueryParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_parser():
    parser = QueryParser()
    
    test_queries = [
        "Show me all projects",
        "Show projects in Central Region",
        "Show education sector projects",
        "Show projects in progress",
    ]
    
    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: {query}")
        logger.info('='*50)
        
        sql_query = parser.parse_query(query)
        logger.info(f"Generated SQL: {sql_query}")

if __name__ == "__main__":
    test_parser() 