from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
import os

db_path = os.path.abspath(os.path.join("app", "database", "malawi_projects1.db"))
db_uri = f"sqlite:///{db_path}"

def test_query(query):
    print(f"\nTesting query: {query}")
    try:
        db = SQLDatabase.from_uri(
            db_uri,
            include_tables=["proj_dashboard"],
            sample_rows_in_table_info=3
        )
        result = db.run(query)
        print(f"Success! Results: {result}")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Test queries
queries = [
    "SELECT COUNT(*) FROM proj_dashboard WHERE DISTRICT = 'Lilongwe'",
    "SELECT SUM(BUDGET) FROM proj_dashboard",
    "SELECT * FROM proj_dashboard WHERE PROJECTSECTOR = 'Infrastructure'",
    "SELECT * FROM proj_dashboard WHERE COMPLETIONPERCENTAGE > 50",
    "SELECT DISTRICT, AVG(BUDGET) FROM proj_dashboard GROUP BY DISTRICT"
]

print(f"Testing database connection to {db_path}...")
engine = create_engine(db_uri)

print("\nGetting table schema...")
with engine.connect() as conn:
    result = conn.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='proj_dashboard'"))
    schema = result.fetchone()
    print(schema[0])

print("\nTesting queries...")
for query in queries:
    test_query(query)
