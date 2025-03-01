#!/usr/bin/env python3
"""
Data Verification Tool

This script helps verify data in the database against LLM responses.
It supports various queries to analyze project data and can be used to
check if the LLM's responses match the actual data in the database.
"""

import os
import sys
import sqlite3
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Display formatting constants
HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

def get_db_connection(db_path=None):
    """Get a connection to the SQLite database."""
    if db_path is None:
        # Default to the database in the project root
        db_path = os.path.join(project_root, 'malawi_projects1.db')
    
    if not os.path.exists(db_path):
        print(f"{RED}Error: Database file not found at: {db_path}{ENDC}")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable row factory for named columns
    return conn

def format_currency(amount):
    """Format a number as currency (MWK)."""
    if amount is None:
        return "N/A"
    return f"MWK {amount:,.2f}"

def count_projects_by_sector(conn, sector=None):
    """Count projects by sector."""
    if sector:
        cursor = conn.cursor()
        query = """
        SELECT COUNT(*) as count, SUM(BUDGET) as total_budget
        FROM proj_dashboard
        WHERE LOWER(PROJECTSECTOR) = LOWER(?)
        """
        cursor.execute(query, (sector,))
        result = cursor.fetchone()
        
        print(f"\n{BOLD}{GREEN}=== Projects in {sector.title()} Sector ==={ENDC}")
        print(f"Project Count: {result['count']}")
        print(f"Total Budget: {format_currency(result['total_budget'])}")
        
        # Get a few sample projects
        sample_query = """
        SELECT PROJECTNAME, DISTRICT, PROJECTSTATUS, BUDGET
        FROM proj_dashboard
        WHERE LOWER(PROJECTSECTOR) = LOWER(?)
        ORDER BY BUDGET DESC
        LIMIT 5
        """
        cursor.execute(sample_query, (sector,))
        samples = cursor.fetchall()
        
        print(f"\n{BOLD}Top 5 Projects by Budget:{ENDC}")
        for i, project in enumerate(samples, 1):
            print(f"{i}. {project['PROJECTNAME']} ({project['DISTRICT']})")
            print(f"   Status: {project['PROJECTSTATUS'] or 'Unknown'}")
            print(f"   Budget: {format_currency(project['BUDGET'])}")
            print()
    else:
        # Get counts for all sectors
        cursor = conn.cursor()
        query = """
        SELECT PROJECTSECTOR, COUNT(*) as count, SUM(BUDGET) as total_budget
        FROM proj_dashboard
        GROUP BY PROJECTSECTOR
        ORDER BY count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n{BOLD}{GREEN}=== Project Counts by Sector ==={ENDC}")
        for result in results:
            sector_name = result['PROJECTSECTOR'] or 'Unknown'
            count = result['count']
            budget = result['total_budget']
            print(f"{sector_name}: {count} projects, Total Budget: {format_currency(budget)}")

def count_projects_by_district(conn, district=None):
    """Count projects by district."""
    if district:
        cursor = conn.cursor()
        query = """
        SELECT COUNT(*) as count, SUM(BUDGET) as total_budget
        FROM proj_dashboard
        WHERE LOWER(DISTRICT) = LOWER(?)
        """
        cursor.execute(query, (district,))
        result = cursor.fetchone()
        
        print(f"\n{BOLD}{GREEN}=== Projects in {district.title()} District ==={ENDC}")
        print(f"Project Count: {result['count']}")
        print(f"Total Budget: {format_currency(result['total_budget'])}")
        
        # Get a breakdown by sector for this district
        sector_query = """
        SELECT PROJECTSECTOR, COUNT(*) as count, SUM(BUDGET) as total_budget
        FROM proj_dashboard
        WHERE LOWER(DISTRICT) = LOWER(?)
        GROUP BY PROJECTSECTOR
        ORDER BY count DESC
        """
        cursor.execute(sector_query, (district,))
        sectors = cursor.fetchall()
        
        print(f"\n{BOLD}Breakdown by Sector:{ENDC}")
        for sector in sectors:
            sector_name = sector['PROJECTSECTOR'] or 'Unknown'
            count = sector['count']
            budget = sector['total_budget']
            print(f"{sector_name}: {count} projects, Total Budget: {format_currency(budget)}")
    else:
        # Get counts for all districts
        cursor = conn.cursor()
        query = """
        SELECT DISTRICT, COUNT(*) as count
        FROM proj_dashboard
        GROUP BY DISTRICT
        ORDER BY count DESC
        LIMIT 10
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n{BOLD}{GREEN}=== Top 10 Districts by Project Count ==={ENDC}")
        for result in results:
            district_name = result['DISTRICT'] or 'Unknown'
            count = result['count']
            print(f"{district_name}: {count} projects")

def search_projects(conn, keyword):
    """Search for projects containing a keyword in their name or description."""
    cursor = conn.cursor()
    query = """
    SELECT PROJECTNAME, DISTRICT, PROJECTSECTOR, PROJECTSTATUS, BUDGET
    FROM proj_dashboard
    WHERE PROJECTNAME LIKE ? OR PROJECTDESC LIKE ?
    LIMIT 10
    """
    search_term = f"%{keyword}%"
    cursor.execute(query, (search_term, search_term))
    results = cursor.fetchall()
    
    print(f"\n{BOLD}{GREEN}=== Projects Matching '{keyword}' ==={ENDC}")
    if not results:
        print(f"No projects found matching '{keyword}'")
        return
    
    for i, project in enumerate(results, 1):
        print(f"{i}. {project['PROJECTNAME']} ({project['DISTRICT']})")
        print(f"   Sector: {project['PROJECTSECTOR'] or 'Unknown'}")
        print(f"   Status: {project['PROJECTSTATUS'] or 'Unknown'}")
        print(f"   Budget: {format_currency(project['BUDGET'])}")
        print()

def get_project_details(conn, project_name):
    """Get detailed information about a specific project."""
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM proj_dashboard
    WHERE PROJECTNAME LIKE ?
    LIMIT 1
    """
    cursor.execute(query, (f"%{project_name}%",))
    project = cursor.fetchone()
    
    if not project:
        print(f"\n{RED}Project not found: {project_name}{ENDC}")
        return
    
    print(f"\n{BOLD}{GREEN}=== Details for Project: {project['PROJECTNAME']} ==={ENDC}")
    print(f"District: {project['DISTRICT'] or 'Unknown'}")
    print(f"Sector: {project['PROJECTSECTOR'] or 'Unknown'}")
    print(f"Status: {project['PROJECTSTATUS'] or 'Unknown'}")
    print(f"Budget: {format_currency(project['BUDGET'])}")
    print(f"Completion: {project['COMPLETIONPERCENTAGE'] or 'Unknown'}%")
    print(f"Start Date: {project['STARTDATE'] or 'Unknown'}")
    print(f"Description: {project['PROJECTDESC'] or 'Not available'}")
    print(f"Contractor: {project['CONTRACTORNAME'] or 'Unknown'}")
    
    if project['MAP_LATITUDE'] and project['MAP_LONGITUDE']:
        print(f"Location: {project['MAP_LATITUDE']}, {project['MAP_LONGITUDE']}")

def run_custom_query(conn, query):
    """Run a custom SQL query against the database."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print(f"\n{YELLOW}Query returned no results.{ENDC}")
            return
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        print(f"\n{BOLD}{GREEN}=== Custom Query Results ==={ENDC}")
        print(f"{BOLD}{', '.join(columns)}{ENDC}")
        print("-" * 80)
        
        for row in results:
            row_data = []
            for col in columns:
                value = row[col]
                # Format currency values if they seem like money
                if col in ['BUDGET', 'TOTALVALUE', 'BUDGETTOTAL']:
                    if value is not None:
                        value = format_currency(value)
                row_data.append(str(value))
            print(", ".join(row_data))
    except sqlite3.Error as e:
        print(f"\n{RED}SQL Error: {e}{ENDC}")

def export_to_json(conn, query, output_file):
    """Export query results to a JSON file."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = []
        for row in results:
            data.append({key: row[key] for key in row.keys()})
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n{GREEN}Data exported to {output_file}{ENDC}")
    except sqlite3.Error as e:
        print(f"\n{RED}SQL Error: {e}{ENDC}")
    except IOError as e:
        print(f"\n{RED}I/O Error: {e}{ENDC}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Verify data in the database against LLM responses.')
    parser.add_argument('--db', help='Path to the SQLite database file')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Sector command
    sector_parser = subparsers.add_parser('sector', help='Analyze projects by sector')
    sector_parser.add_argument('name', nargs='?', help='Sector name (e.g., health, education)')
    
    # District command
    district_parser = subparsers.add_parser('district', help='Analyze projects by district')
    district_parser.add_argument('name', nargs='?', help='District name (e.g., Lilongwe, Zomba)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for projects by keyword')
    search_parser.add_argument('keyword', help='Keyword to search for')
    
    # Project details command
    project_parser = subparsers.add_parser('project', help='Get details for a specific project')
    project_parser.add_argument('name', help='Project name (or part of it)')
    
    # Custom query command
    query_parser = subparsers.add_parser('query', help='Run a custom SQL query')
    query_parser.add_argument('sql', help='SQL query to run')
    query_parser.add_argument('--output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Connect to the database
    conn = get_db_connection(args.db)
    
    try:
        if args.command == 'sector':
            count_projects_by_sector(conn, args.name)
        elif args.command == 'district':
            count_projects_by_district(conn, args.name)
        elif args.command == 'search':
            search_projects(conn, args.keyword)
        elif args.command == 'project':
            get_project_details(conn, args.name)
        elif args.command == 'query':
            if args.output:
                export_to_json(conn, args.sql, args.output)
            else:
                run_custom_query(conn, args.sql)
        else:
            # Default: show summary data
            print(f"{BOLD}{BLUE}=== Malawi Projects Database Verification Tool ==={ENDC}")
            print(f"Database: {os.path.abspath(conn.execute('PRAGMA database_list').fetchone()[2])}")
            
            # Get total project count
            total = conn.execute('SELECT COUNT(*) as count FROM proj_dashboard').fetchone()['count']
            print(f"Total Projects: {total}")
            
            # Show sector and district summaries
            count_projects_by_sector(conn)
            count_projects_by_district(conn)
    finally:
        conn.close()

if __name__ == '__main__':
    main() 