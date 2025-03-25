#!/usr/bin/env python
import sqlite3
import json

def test_education_query():
    """Direct test for education sector query"""
    try:
        # Connect directly to the database
        conn = sqlite3.connect('/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute the query directly
        query = """
            SELECT 
                PROJECTNAME, PROJECTCODE, PROJECTSECTOR, PROJECTSTATUS,
                DISTRICT, BUDGET, FISCALYEAR
            FROM proj_dashboard
            WHERE PROJECTSECTOR = 'Education'
            ORDER BY BUDGET DESC NULLS LAST
            LIMIT 10;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        projects = []
        for row in rows:
            project = {}
            for key in row.keys():
                project[key] = row[key]
            projects.append(project)
        
        # Format for display
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                "Name": project.get("PROJECTNAME", "Unknown"),
                "Code": project.get("PROJECTCODE", "Unknown"),
                "Sector": project.get("PROJECTSECTOR", "Unknown"),
                "Status": project.get("PROJECTSTATUS", "Unknown"),
                "District": project.get("DISTRICT", "Unknown"),
                "Budget": f"MWK {float(project.get('BUDGET', 0)):,.2f}" if project.get("BUDGET") else "Unknown",
                "Fiscal Year": project.get("FISCALYEAR", "Unknown"),
            })
        
        # Print formatted result
        result = {
            "response": f"Found {len(projects)} education sector projects.",
            "projects": formatted_projects,
        }
        
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = test_education_query()
    print(json.dumps(result, indent=2))
