import sqlite3

def print_schema():
    conn = sqlite3.connect('malawi_projects1.db')
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='proj_dashboard';")
    print("\nTable Schema:")
    print(cursor.fetchone()[0])
    
    # Get sample row
    cursor.execute("SELECT * FROM proj_dashboard LIMIT 1;")
    columns = [description[0] for description in cursor.description]
    print("\nColumns:", columns)
    
    conn.close()

if __name__ == "__main__":
    print_schema() 