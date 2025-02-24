import sqlite3
import os

def init_database():
    """Initialize the database with test data"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "database", "projects.db")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proj_dashboard (
            projectname TEXT,
            district TEXT,
            projectsector TEXT,
            projectstatus TEXT,
            budget NUMERIC,
            completionpercentage NUMERIC,
            startdate NUMERIC,
            completiondata NUMERIC
        )
    """)
    
    # Sample data lists for generating records
    districts = ['Lilongwe', 'Blantyre', 'Mzuzu', 'Zomba', 'Kasungu', 'Mangochi', 'Salima', 'Nkhata Bay', 'Karonga', 'Dedza']
    sectors = ['Infrastructure', 'Water', 'Energy', 'Education', 'Healthcare', 'Agriculture', 'Transport']
    statuses = ['Active', 'Planning', 'Completed', 'On Hold']
    project_types = ['Road', 'Bridge', 'School', 'Hospital', 'Market', 'Power Plant', 'Water Supply', 'Irrigation']
    
    # Generate 196 projects
    projects = []
    for i in range(196):
        district = districts[i % len(districts)]
        sector = sectors[i % len(sectors)]
        status = statuses[i % len(statuses)]
        project_type = project_types[i % len(project_types)]
        
        # Generate realistic project name
        project_name = f"{district} {project_type} {['Development', 'Rehabilitation', 'Construction', 'Improvement'][i % 4]} Phase {(i // 4) + 1}"
        
        # Generate realistic budget between 500,000 and 10,000,000
        budget = round(500000 + (i * 48724.489795918366), 2)
        
        # Generate completion percentage (0-100)
        completion = min(100, max(0, (i % 120)))
        
        # Generate dates (2023-2025)
        start_year = 2023 + (i % 3)
        start_month = 1 + (i % 12)
        start_date = int(f"{start_year}{start_month:02d}01")
        
        end_year = start_year + 1
        end_month = start_month
        end_date = int(f"{end_year}{end_month:02d}01")
        
        projects.append((
            project_name,
            district,
            sector,
            status,
            budget,
            completion,
            start_date,
            end_date
        ))
    
    # Insert projects
    cursor.executemany("""
        INSERT INTO proj_dashboard (projectname, district, projectsector, projectstatus, budget, completionpercentage, startdate, completiondata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, projects)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database initialized with {len(projects)} projects")

if __name__ == "__main__":
    init_database() 