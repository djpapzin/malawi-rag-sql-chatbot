# check_db.py
import sqlite3
import pandas as pd
import os

def check_database():
    db_path = "C:/Users/MukundiMphaphuli/Desktop/Use Case 2/final_project/malawi_projects1.db"
    
    print(f"\nChecking database at: {db_path}")
    print(f"File exists: {os.path.exists(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Check table structure
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
                
            # Check row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
                sample = cursor.fetchone()
                print("\nSample row:")
                for col, val in zip(columns, sample):
                    print(f"  {col[1]}: {val}")
                    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()