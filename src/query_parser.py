import re

def parse_query(query: str) -> dict:
    """Parse the input query and return the appropriate SQL query components."""
    query = query.strip()
    
    # Extract quoted project name if present
    quoted_pattern = r"'([^']+)'"
    quoted_matches = re.findall(quoted_pattern, query)
    
    # Extract project code if present
    code_pattern = r'\b(?:MW-)?[A-Z]{2}-[A-Z0-9]{2}\b'
    code_matches = re.findall(code_pattern, query.upper())
    
    conditions = []
    order_by = []
    
    # Determine query type and select appropriate columns
    if re.search(r'\b(progress|status)\b', query, re.IGNORECASE):
        base_query = """
            SELECT DISTINCT
                PROJECTNAME, PROJECTSTATUS, COMPLETIONPERCENTAGE,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
    elif re.search(r'\b(budget|cost)\b', query, re.IGNORECASE):
        base_query = """
            SELECT DISTINCT
                PROJECTNAME, TOTALBUDGET, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
    elif re.search(r'\b(contractor|who)\b', query, re.IGNORECASE):
        base_query = """
            SELECT DISTINCT
                PROJECTNAME, CONTRACTORNAME, SIGNINGDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
    else:
        base_query = """
            SELECT DISTINCT
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
        """
    
    if quoted_matches:
        project_name = quoted_matches[0].strip()
        # Remove 'project' keyword if it appears at the end
        project_name = re.sub(r'\s+project$', '', project_name, flags=re.IGNORECASE)
        
        # Add exact match condition with high priority
        conditions.append(f"LOWER(PROJECTNAME) = LOWER('{project_name}')")
        # Add partial match condition with lower priority
        conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')")
        
        order_by.append(f"CASE WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1 "
                       f"WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%') THEN 2 "
                       "ELSE 3 END")
    
    elif code_matches:
        project_code = code_matches[0]
        if not project_code.startswith('MW-'):
            project_code = f'MW-{project_code}'
            
        # Add exact match condition for project code
        conditions.append(f"UPPER(PROJECTCODE) = '{project_code}'")
        order_by.append("1")
    
    # Build the final query
    sql_query = base_query
    if conditions:
        sql_query += f" AND ({' OR '.join(conditions)})"
    if order_by:
        sql_query += f" ORDER BY {', '.join(order_by)}"
        sql_query += " LIMIT 5"  # Only add LIMIT after ORDER BY
    
    return {
        "query": sql_query,
        "is_specific_project": bool(quoted_matches or code_matches)
    } 