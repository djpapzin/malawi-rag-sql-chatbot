import sqlite3

# Connect to the database
conn = sqlite3.connect('malawi_projects1.db')
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='proj_dashboard';")
print(cursor.fetchone()[0])

# Test some queries
test_queries = [
    "SELECT COUNT(*) FROM proj_dashboard WHERE DISTRICT = 'Lilongwe'",
    "SELECT SUM(BUDGET) FROM proj_dashboard",
    "SELECT * FROM proj_dashboard WHERE PROJECTSECTOR = 'Infrastructure'",
    "SELECT * FROM proj_dashboard WHERE COMPLETIONPERCENTAGE > 50",
    "SELECT DISTRICT, AVG(BUDGET) FROM proj_dashboard GROUP BY DISTRICT"
]

print("\nTesting queries:")
for query in test_queries:
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        print(f"\nQuery: {query}")
        print(f"Result: {result}")
    except Exception as e:
        print(f"\nQuery: {query}")
        print(f"Error: {str(e)}")

conn.close()
