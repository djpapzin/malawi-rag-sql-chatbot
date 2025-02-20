import requests
import json
import sqlite3
import pandas as pd
from tabulate import tabulate

def get_database_projects():
    """Get education projects directly from database"""
    conn = sqlite3.connect('malawi_projects1.db')
    query = """
        SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
        FROM proj_dashboard 
        WHERE ISLATEST = 1 
        AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
        ORDER BY PROJECTNAME ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_api_projects():
    """Get education projects through API"""
    query = {
        "message": "Show me all education projects",
        "language": "english",
        "session_id": "test_session"
    }
    
    response = requests.post(
        "http://localhost:8001/query",
        json=query
    )
    return response.json()

def parse_api_response(response_text):
    """Parse the API response text into structured data"""
    projects = []
    current_project = {}
    
    for line in response_text.split('\n'):
        if not line.strip():
            if current_project:
                projects.append(current_project)
                current_project = {}
            continue
            
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if key == 'Project':
                if current_project:
                    projects.append(current_project)
                current_project = {}
            current_project[key] = value
            
    if current_project:
        projects.append(current_project)
        
    return projects

def compare_results():
    """Compare database results with API response"""
    # Get data
    db_df = get_database_projects()
    api_response = get_api_projects()
    api_projects = parse_api_response(api_response['response'])
    
    # Create comparison table
    comparison_data = []
    for idx, db_row in db_df.head(5).iterrows():  # Compare first 5 projects
        db_name = db_row['PROJECTNAME']
        api_project = next((p for p in api_projects if p.get('Project') == db_name), None)
        
        comparison_data.append([
            db_name,
            'Yes' if api_project else 'No',
            db_row['REGION'],
            api_project.get('Location', '').split(',')[0].strip() if api_project else 'N/A',
            db_row['PROJECTSTATUS'] or 'None',
            api_project.get('Status', 'N/A') if api_project else 'N/A'
        ])
    
    # Print results
    print("\nEducation Projects Comparison")
    print("-" * 50)
    print(f"Total Projects in Database: {len(db_df)}")
    print(f"Total Projects in API Response: {len(api_projects)}")
    print(f"Counts Match: {'✓' if len(db_df) == len(api_projects) else '✗'}")
    
    print("\nDetailed Comparison (First 5 Projects):")
    print(tabulate(
        comparison_data,
        headers=['Project Name', 'In API', 'DB Region', 'API Region', 'DB Status', 'API Status'],
        tablefmt='grid'
    ))
    
    # Save full comparison
    comparison = {
        "database_count": len(db_df),
        "api_count": len(api_projects),
        "matches": len(db_df) == len(api_projects),
        "sample_comparison": comparison_data
    }
    
    with open("education_projects_comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)

if __name__ == "__main__":
    compare_results() 