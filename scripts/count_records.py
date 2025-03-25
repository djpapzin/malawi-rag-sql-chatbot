import sqlite3

def analyze_both_dbs():
    # First database: malawi_projects1.db
    try:
        conn1 = sqlite3.connect('malawi_projects1.db')
        cursor1 = conn1.cursor()
        
        # Get record count
        cursor1.execute("SELECT COUNT(*) FROM projects")
        count = cursor1.fetchone()[0]
        
        # Get field count
        cursor1.execute("PRAGMA table_info(projects)")
        fields = cursor1.fetchall()
        
        print("\nmalawi_projects1.db analysis:")
        print(f"Number of fields in projects table: {len(fields)}")
        print(f"Number of records in projects table: {count}")
        
    except sqlite3.Error as e:
        print(f"Error with malawi_projects1.db: {e}")
    finally:
        if conn1:
            conn1.close()

if __name__ == "__main__":
    analyze_both_dbs()