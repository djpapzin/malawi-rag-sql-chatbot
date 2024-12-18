"""
Setup script for creating and populating the test database
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

def create_database():
    """Create the database and tables"""
    conn = sqlite3.connect('malawi_projects1.db')
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        sector TEXT NOT NULL,
        region TEXT NOT NULL,
        district TEXT NOT NULL,
        budget REAL NOT NULL,
        completion_percentage REAL DEFAULT 0,
        status TEXT NOT NULL,
        start_date DATE,
        description TEXT
    )
    """)
    
    # Sample data
    projects = []
    sectors = ['Education', 'Health', 'Water and Sanitation', 'Transport', 'Community security initiatives']
    regions = ['Northern Region', 'Central Region', 'Southern Region']
    districts = {
        'Northern Region': ['Chitipa', 'Karonga', 'Likoma', 'Mzimba', 'Nkhata Bay', 'Rumphi'],
        'Central Region': ['Dedza', 'Dowa', 'Kasungu', 'Lilongwe', 'Mchinji', 'Nkhotakota', 'Ntcheu', 'Ntchisi', 'Salima'],
        'Southern Region': ['Balaka', 'Blantyre', 'Chikwawa', 'Chiradzulu', 'Machinga', 'Mangochi', 'Mulanje', 'Mwanza', 'Nsanje', 'Thyolo', 'Zomba']
    }
    
    # Generate 100 sample projects
    start_date = datetime(2020, 1, 1)
    for i in range(100):
        sector = random.choice(sectors)
        region = random.choice(regions)
        district = random.choice(districts[region])
        budget = random.uniform(100000, 5000000)
        completion = random.uniform(0, 100)
        
        if completion == 0:
            status = 'Not Started'
        elif completion == 100:
            status = 'Completed'
        else:
            status = 'In Progress'
        
        project_date = start_date + timedelta(days=random.randint(0, 730))
        
        projects.append({
            'project_name': f"{sector} Project in {district} {i+1}",
            'sector': sector,
            'region': region,
            'district': district,
            'budget': budget,
            'completion_percentage': completion,
            'status': status,
            'start_date': project_date.strftime('%Y-%m-%d'),
            'description': f"Sample {sector.lower()} project in {district}, {region}"
        })
    
    # Insert data
    cursor.executemany("""
    INSERT INTO projects (
        project_name, sector, region, district, budget,
        completion_percentage, status, start_date, description
    ) VALUES (
        :project_name, :sector, :region, :district, :budget,
        :completion_percentage, :status, :start_date, :description
    )
    """, projects)
    
    conn.commit()
    conn.close()
    
    print(f"Created database with {len(projects)} sample projects")

if __name__ == "__main__":
    create_database() 