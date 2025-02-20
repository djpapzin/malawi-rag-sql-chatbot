import sqlite3
import requests
import json
from tabulate import tabulate
import pandas as pd
import csv

def get_database_projects():
    """Retrieve education projects from the database with detailed information."""
    conn = sqlite3.connect('malawi_projects1.db')
    cursor = conn.cursor()
    
    query = """
    SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
    FROM proj_dashboard 
    WHERE ISLATEST = 1 
    AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
    ORDER BY PROJECTNAME ASC
    """
    
    print("\nDatabase SQL Query:")
    print("-" * 50)
    print(query.strip())
    print("-" * 50)
    
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    
    conn.close()
    
    # Convert to list of dictionaries for easier comparison
    projects = []
    for row in results:
        project = {}
        for col, val in zip(columns, row):
            # Handle null values consistently
            project[col] = "Not available" if val is None or str(val).strip() == '' else val
        projects.append(project)
    
    return projects

def get_api_projects():
    """Retrieve education projects from the API."""
    url = "http://localhost:8001/query"
    query = {
        "message": "Show me education sector projects"
    }
    
    try:
        response = requests.post(url, json=query)
        result = response.json()
        
        # Extract and display the SQL query from the source
        if 'source' in result and 'sql' in result['source']:
            print("\nAPI SQL Query:")
            print("-" * 50)
            print(result['source']['sql'].strip())
            print("-" * 50)
            
        return result
    except Exception as e:
        print(f"Error querying API: {str(e)}")
        return None

def parse_api_response(response):
    """Parse API response into structured data."""
    if not response:
        return []
    
    # Extract project information from the response text
    projects = []
    if 'response' in response:
        # Split the response into individual project sections
        project_sections = response['response'].split('\n\n')
        
        for section in project_sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            project = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map the keys to match database column names
                    if key == 'Project':
                        project['PROJECTNAME'] = value
                    elif key == 'Sector':
                        project['PROJECTSECTOR'] = value
                    elif key == 'Location':
                        # Split location into region and district
                        if ',' in value:
                            region, district = value.split(',', 1)
                            project['REGION'] = region.strip()
                            project['DISTRICT'] = district.strip()
                        else:
                            project['REGION'] = value
                            project['DISTRICT'] = ''
                    elif key == 'Status':
                        project['PROJECTSTATUS'] = value
                    elif key == 'Budget':
                        project['TOTALBUDGET'] = value
            
            if project:  # Only add if we found some data
                projects.append(project)
    
    return projects

def save_comparison_csv(db_projects, api_projects):
    """Save comparison data to CSV file"""
    # Prepare comparison data
    comparison_data = []
    for idx, db_project in enumerate(db_projects[:5]):  # First 5 projects
        api_project = api_projects[idx] if idx < len(api_projects) else {}
        row = {
            'Project Name': db_project.get('PROJECTNAME', ''),
            'DB Region': db_project.get('REGION', ''),
            'API Region': api_project.get('REGION', ''),
            'DB District': db_project.get('DISTRICT', ''),
            'API District': api_project.get('DISTRICT', ''),
            'DB Status': db_project.get('PROJECTSTATUS', ''),
            'API Status': api_project.get('PROJECTSTATUS', ''),
            'DB Budget': db_project.get('TOTALBUDGET', ''),
            'API Budget': api_project.get('TOTALBUDGET', '')
        }
        comparison_data.append(row)
    
    # Save to CSV
    with open('results/education_projects_comparison.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=comparison_data[0].keys())
        writer.writeheader()
        writer.writerows(comparison_data)

def generate_markdown_table(db_projects, api_projects):
    """Generate markdown table comparison"""
    markdown = "# Education Projects Comparison\n\n"
    
    # Add summary
    markdown += "## Summary\n"
    markdown += f"* Database Projects: {len(db_projects)}\n"
    markdown += f"* API Projects: {len(api_projects)}\n"
    markdown += f"* Match: {'Yes' if len(db_projects) == len(api_projects) else 'No'}\n\n"
    
    # Add SQL queries
    markdown += "## SQL Queries\n\n"
    markdown += "### Database Query\n```sql\n"
    markdown += """SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
FROM proj_dashboard 
WHERE ISLATEST = 1 
AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
ORDER BY PROJECTNAME ASC\n```\n\n"""
    
    # Add comparison table
    markdown += "## First 5 Projects Comparison\n\n"
    markdown += "| Project Name | Source | Region | District | Status | Budget |\n"
    markdown += "|--------------|---------|---------|-----------|---------|----------|\n"
    
    # Add rows for first 5 projects
    for idx, db_project in enumerate(db_projects[:5]):
        api_project = api_projects[idx] if idx < len(api_projects) else {}
        
        # Database row
        markdown += f"| {db_project.get('PROJECTNAME', '')} | Database | "
        markdown += f"{db_project.get('REGION', '')} | {db_project.get('DISTRICT', '')} | "
        markdown += f"{db_project.get('PROJECTSTATUS', '')} | {db_project.get('TOTALBUDGET', '')} |\n"
        
        # API row
        if api_project:
            markdown += f"| {api_project.get('PROJECTNAME', '')} | API | "
            markdown += f"{api_project.get('REGION', '')} | {api_project.get('DISTRICT', '')} | "
            markdown += f"{api_project.get('PROJECTSTATUS', '')} | {api_project.get('TOTALBUDGET', '')} |\n"
    
    # Save markdown
    with open('results/education_projects_comparison.md', 'w') as f:
        f.write(markdown)
    
    return markdown

def compare_results():
    """Compare and display detailed project information from both sources."""
    print("\nRetrieving and comparing education projects...")
    
    # Get data from both sources
    db_projects = get_database_projects()
    api_response = get_api_projects()
    api_projects = parse_api_response(api_response)
    
    # Prepare comparison data
    comparison = {
        'database_count': len(db_projects),
        'api_count': len(api_projects),
        'counts_match': len(db_projects) == len(api_projects),
        'first_5_projects': {
            'database': db_projects[:5],
            'api': api_projects[:5]
        }
    }
    
    # Print comparison results
    print(f"\nComparison Results:")
    print(f"Database Projects Count: {comparison['database_count']}")
    print(f"API Projects Count: {comparison['api_count']}")
    print(f"Counts Match: {'Yes' if comparison['counts_match'] else 'No'}")
    
    print("\nFirst 5 Projects from Database:")
    if db_projects:
        print(tabulate(db_projects[:5], headers='keys', tablefmt='grid'))
    else:
        print("No projects found in database")
    
    print("\nFirst 5 Projects from API:")
    if api_projects:
        print(tabulate(api_projects[:5], headers='keys', tablefmt='grid'))
    else:
        print("No projects found in API response")
    
    # Save comparison to different formats
    with open('results/education_projects_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    # Save CSV comparison
    save_comparison_csv(db_projects, api_projects)
    
    # Generate and save markdown comparison
    markdown_table = generate_markdown_table(db_projects, api_projects)
    
    print("\nComparison files generated in results directory:")
    print("1. education_projects_comparison.json (JSON format)")
    print("2. education_projects_comparison.csv (CSV format)")
    print("3. education_projects_comparison.md (Markdown format)")

def generate_comprehensive_report(all_results):
    """Generate a comprehensive markdown report combining all query results."""
    markdown = "# Comprehensive Query Test Results\n\n"
    
    # Add summary section
    markdown += "## Overview\n"
    markdown += "This report contains the results of various queries testing the infrastructure projects database and API.\n\n"
    
    # Separate specific and general queries
    specific_queries = []
    general_queries = []
    
    for result in all_results:
        if result.get('query_type') == 'specific' or 'show details for' in result['query'].lower() or "'project" in result['query'].lower():
            specific_queries.append(result)
        else:
            general_queries.append(result)
    
    # Add table of contents
    markdown += "## Table of Contents\n"
    markdown += "1. [Specific Project Queries](#specific-project-queries)\n"
    markdown += "2. [General Project Queries](#general-project-queries)\n\n"
    
    # Specific Project Queries Section
    markdown += "## Specific Project Queries\n\n"
    for query_data in specific_queries:
        query = query_data['query'].replace("'", "").strip()
        markdown += f"### Query: {query}\n\n"
        
        if 'sql' in query_data:
            markdown += "### SQL Query\n```sql\n"
            markdown += f"{query_data['sql']}\n```\n\n"
        
        markdown += "### Results Summary\n"
        markdown += f"* Database Results: {query_data.get('db_count', 0)}\n"
        markdown += f"* API Results: {query_data.get('api_count', 0)}\n"
        markdown += f"* Match: {'Yes' if query_data.get('counts_match', False) else 'No'}\n\n"
        
        markdown += "### Project Details\n\n"
        if 'results' in query_data and query_data['results']:
            first_result = query_data['results'][0]
            markdown += "| Field | Value |\n"
            markdown += "|-------|-------|\n"
            for field, value in first_result.items():
                if field == 'PROJECTNAME' or value:  # Always show project name and non-empty fields
                    markdown += f"| {field} | {value if value else 'Not available'} |\n"
        else:
            markdown += "No project details available\n\n"
            
    # General Project Queries Section
    markdown += "## General Project Queries\n\n"
    for query_data in general_queries:
        query = query_data['query'].replace("'", "").strip()
        markdown += f"### Query: {query}\n\n"
        
        if 'sql' in query_data:
            markdown += "### SQL Query\n```sql\n"
            markdown += f"{query_data['sql']}\n```\n\n"
        
        markdown += "### Results Summary\n"
        markdown += f"* Database Results: {query_data.get('db_count', 0)}\n"
        markdown += f"* API Results: {query_data.get('api_count', 0)}\n"
        markdown += f"* Match: {'Yes' if query_data.get('counts_match', False) else 'No'}\n\n"
        
        markdown += "### Results Comparison\n\n"
        if 'results' in query_data and query_data['results']:
            markdown += "| Project Name | Source | Region | District | Status | Budget |\n"
            markdown += "|--------------|---------|---------|-----------|---------|----------|\n"
            
            for result in query_data['results'][:5]:  # Show first 5 results
                # Database row
                markdown += f"| {result.get('PROJECTNAME', 'Not available')} | Database | "
                markdown += f"{result.get('REGION', 'Not available')} | {result.get('DISTRICT', 'Not available')} | "
                markdown += f"{result.get('PROJECTSTATUS', 'Not available')} | {result.get('TOTALBUDGET', 'Not available')} |\n"
                
                # API row (if available)
                if 'api_result' in result:
                    api_result = result['api_result']
                    markdown += f"| {api_result.get('PROJECTNAME', 'Not available')} | API | "
                    markdown += f"{api_result.get('REGION', 'Not available')} | {api_result.get('DISTRICT', 'Not available')} | "
                    markdown += f"{api_result.get('PROJECTSTATUS', 'Not available')} | {api_result.get('TOTALBUDGET', 'Not available')} |\n"
        else:
            markdown += "No results available\n\n"
    
    return markdown

def test_specific_queries():
    """Test a set of specific education project queries"""
    test_queries = [
        # Location-based queries
        "Tell me about education projects in Mchinji",
        "Show education projects in Zomba district",
        "List all projects in Southern Region",
        
        # Status-based queries
        "Show me completed education projects",
        "What are the ongoing education projects",
        "List delayed education projects",
        
        # Budget-based queries
        "Show me education projects with budget information",
        "Which education projects have the highest budget",
        "List education projects with expenditure details",
        
        # Sector-specific queries
        "Tell me about school construction projects",
        "Show me classroom block projects",
        "List girls hostel construction projects",
        
        # Specific project queries (by name)
        "Details about 'Nachuma Market Shed phase 3'",
        "Tell me about 'Boma Stadium Phase 3'",
        "What is the status of 'CHILIPA CDSS GIRLS HOSTEL'",
        "Show progress of 'Chilingani School Block Construction'",
        
        # Project code queries
        "Show details for project MW-CR-DO",
        "What is the status of project code MW-SR-BT",
        
        # Combined criteria queries
        "Show completed education projects in Southern Region",
        "List ongoing school construction in Mchinji",
        "Tell me about education projects with budget in Zomba"
    ]
    
    print("\nTesting Specific Education Project Queries")
    print("="*50)
    
    all_results = []
    
    # First get general education projects
    db_projects = get_database_projects()
    api_response = get_api_projects()
    api_projects = parse_api_response(api_response)
    
    all_results.append({
        'query': "All Education Projects",
        'sql': """SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
FROM proj_dashboard 
WHERE ISLATEST = 1 
AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
ORDER BY PROJECTNAME ASC""",
        'db_results': db_projects,
        'api_results': api_projects
    })
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*50)
        
        # Get API response
        url = "http://localhost:8001/query"
        try:
            response = requests.post(url, json={"message": query})
            result = response.json()
            
            # Extract SQL from API response
            if 'source' in result and 'sql' in result['source']:
                print("\nAPI SQL Query:")
                print(result['source']['sql'].strip())
                sql_query = result['source']['sql'].strip()
            
            # Parse API results
            api_projects = parse_api_response(result)
            
            # Get database results using the same SQL
            conn = sqlite3.connect('malawi_projects1.db')
            if 'source' in result and 'sql' in result['source']:
                db_df = pd.read_sql_query(result['source']['sql'], conn)
                db_projects = db_df.to_dict('records')
            else:
                db_projects = []
            conn.close()
            
            # Store results
            all_results.append({
                'query': query,
                'sql': sql_query,
                'db_results': db_projects,
                'api_results': api_projects
            })
            
            # Compare results
            print(f"\nResults Summary:")
            print(f"API Results: {len(api_projects)}")
            print(f"Database Results: {len(db_projects)}")
            print(f"Counts Match: {'Yes' if len(api_projects) == len(db_projects) else 'No'}")
            
            # Save individual query results
            query_filename = query.replace("'", "").replace(" ", "_").lower()
            with open(f'results/query_test_{query_filename}.md', 'w') as f:
                f.write(f"# Query Test Results: {query}\n\n")
                f.write("## SQL Query\n```sql\n")
                f.write(sql_query + "\n```\n\n")
                f.write("## Results Summary\n")
                f.write(f"* API Results: {len(api_projects)}\n")
                f.write(f"* Database Results: {len(db_projects)}\n")
                f.write(f"* Counts Match: {'Yes' if len(api_projects) == len(db_projects) else 'No'}\n\n")
                
                # Add comparison table
                f.write("## Results Comparison\n\n")
                f.write("| Project Name | Source | Region | District | Status | Budget |\n")
                f.write("|--------------|---------|---------|-----------|---------|----------|\n")
                
                for i in range(min(5, max(len(api_projects), len(db_projects)))):
                    if i < len(db_projects):
                        db_proj = db_projects[i]
                        f.write(f"| {db_proj.get('PROJECTNAME', '')} | Database | ")
                        f.write(f"{db_proj.get('REGION', '')} | {db_proj.get('DISTRICT', '')} | ")
                        f.write(f"{db_proj.get('PROJECTSTATUS', '')} | {db_proj.get('TOTALBUDGET', '')} |\n")
                    
                    if i < len(api_projects):
                        api_proj = api_projects[i]
                        f.write(f"| {api_proj.get('PROJECTNAME', '')} | API | ")
                        f.write(f"{api_proj.get('REGION', '')} | {api_proj.get('DISTRICT', '')} | ")
                        f.write(f"{api_proj.get('PROJECTSTATUS', '')} | {api_proj.get('TOTALBUDGET', '')} |\n")
            
        except Exception as e:
            print(f"Error testing query: {str(e)}")
        
        print("\n" + "="*50)
    
    # Generate comprehensive report
    comprehensive_report = generate_comprehensive_report(all_results)
    
    # Save comprehensive report
    with open('results/comprehensive_query_results.md', 'w') as f:
        f.write(comprehensive_report)
    print("\nComprehensive report saved to results/comprehensive_query_results.md")

if __name__ == "__main__":
    # Run specific query tests with comprehensive report
    test_specific_queries() 