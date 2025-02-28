#!/usr/bin/env python3
import sqlite3

# Connect to the database
conn = sqlite3.connect('pmisProjects.db')
cursor = conn.cursor()

# Get a list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Found {len(tables)} tables:")

# For each table, get schema and count rows
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]
    
    print(f"\nTable: {table_name} ({row_count} rows)")
    print("-" * 80)
    for col in columns:
        col_id, col_name, col_type, notnull, default_val, pk = col
        print(f"{col_name} ({col_type})")

conn.close()
