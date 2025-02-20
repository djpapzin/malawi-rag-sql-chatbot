import sqlite3
import pandas as pd
import os

def setup_database():
    # Create database connection
    conn = sqlite3.connect('malawi_projects1.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS districts (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sectors (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        district_id INTEGER,
        sector_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        budget REAL,
        status TEXT,
        FOREIGN KEY (district_id) REFERENCES districts (id),
        FOREIGN KEY (sector_id) REFERENCES sectors (id)
    )
    ''')

    # Sample data
    districts = [
        (1, 'Lilongwe'),
        (2, 'Blantyre'),
        (3, 'Mzuzu'),
        (4, 'Zomba')
    ]

    sectors = [
        (1, 'Infrastructure'),
        (2, 'Education'),
        (3, 'Healthcare'),
        (4, 'Agriculture')
    ]

    projects = [
        (1, 'Road Rehabilitation Project', 'Upgrading major roads in the district', 1, 1, '2024-01-01', '2025-12-31', 1500000.00, 'In Progress'),
        (2, 'School Construction', 'Building new primary schools', 2, 2, '2024-03-01', '2024-12-31', 800000.00, 'Planning'),
        (3, 'Hospital Expansion', 'Expanding district hospital capacity', 3, 3, '2024-02-01', '2025-06-30', 2000000.00, 'In Progress'),
        (4, 'Irrigation System', 'Installing modern irrigation systems', 4, 4, '2024-04-01', '2025-03-31', 1200000.00, 'Planning')
    ]

    # Insert sample data
    cursor.executemany('INSERT OR REPLACE INTO districts VALUES (?, ?)', districts)
    cursor.executemany('INSERT OR REPLACE INTO sectors VALUES (?, ?)', sectors)
    cursor.executemany('INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', projects)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
