import sqlite3
import os

def init_database():
    """Initialize the database with test data"""
    db_path = "malawi_projects.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sector TEXT NOT NULL,
            district TEXT NOT NULL,
            status TEXT NOT NULL,
            budget REAL NOT NULL,
            start_date TEXT,
            end_date TEXT,
            description TEXT
        )
    """)
    
    # Sample project data
    projects = [
        (
            "Lilongwe District Road Rehabilitation",
            "Infrastructure",
            "Lilongwe",
            "Active",
            5000000.00,
            "2023-01-01",
            "2024-12-31",
            "Major road rehabilitation project in Lilongwe district"
        ),
        (
            "Blantyre Water Supply Expansion",
            "Water",
            "Blantyre",
            "Planning",
            7500000.00,
            "2024-03-01",
            "2025-06-30",
            "Expansion of water supply network in Blantyre"
        ),
        (
            "Mzuzu Urban Roads Project",
            "Infrastructure",
            "Mzuzu",
            "Active",
            4200000.00,
            "2023-07-01",
            "2024-08-31",
            "Urban road construction and improvement in Mzuzu"
        ),
        (
            "Zomba Rural Electrification",
            "Energy",
            "Zomba",
            "Active",
            3800000.00,
            "2023-04-01",
            "2024-03-31",
            "Rural electrification project in Zomba district"
        ),
        (
            "Kasungu Bridge Construction",
            "Infrastructure",
            "Kasungu",
            "Planning",
            2500000.00,
            "2024-01-01",
            "2024-12-31",
            "Construction of new bridge in Kasungu district"
        ),
        (
            "Lilongwe Market Development",
            "Infrastructure",
            "Lilongwe",
            "Active",
            1800000.00,
            "2023-09-01",
            "2024-06-30",
            "Development of modern market facilities in Lilongwe"
        )
    ]
    
    # Insert projects
    cursor.executemany("""
        INSERT INTO projects (name, sector, district, status, budget, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, projects)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized with {len(projects)} projects")

if __name__ == "__main__":
    init_database() 