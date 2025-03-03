import re
from typing import Optional
from difflib import get_close_matches

# Complete list of Malawi districts
MALAWI_DISTRICTS = [
    'Balaka', 'Blantyre', 'Chikwawa', 'Chiradzulu', 'Chitipa', 'Dedza', 
    'Dowa', 'Karonga', 'Kasungu', 'Likoma', 'Lilongwe', 'Machinga', 
    'Mangochi', 'Mchinji', 'Mulanje', 'Mwanza', 'Mzimba', 'Neno', 
    'Nkhata Bay', 'Nkhotakota', 'Nsanje', 'Ntcheu', 'Ntchisi', 'Phalombe', 
    'Rumphi', 'Salima', 'Thyolo', 'Zomba'
]

# Common variations and typos in district names
DISTRICT_VARIATIONS = {
    "nkhatabay": "Nkhata Bay",
    "nkata bay": "Nkhata Bay",
    "nkhotacota": "Nkhotakota",
    "lilongway": "Lilongwe",
    "blantire": "Blantyre",
    "blantrye": "Blantyre",
    "zomba city": "Zomba",
    "mzuzu": "Mzimba",  # Mzuzu is in Mzimba district
}

def extract_district_from_query(query: str) -> Optional[str]:
    """Extract district name from a query using enhanced pattern matching."""
    query = query.lower().strip()
    
    # Expanded patterns for district queries
    district_patterns = [
        r'(?:projects|list).* (?:in|located in|based in|for) ([A-Za-z\s\-]+?)(?: district)?(?:\s|$|\.|\?)',
        r'([A-Za-z\s\-]+?) (?:district|region).* projects',
        r'show (?:me|all|the) projects.* (?:in|for|at) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        r'which projects are (?:in|located in|based in) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        r'what projects are (?:in|located in|being implemented in) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        r'tell me about ([A-Za-z\s\-]+?) (?:district)? projects',
        r'projects (?:in|from|of) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        r'([A-Za-z\s\-]+?) projects',
        r'(?:all)? projects (?:in|for) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        r'(?:infrastructure|development) (?:in|for|at) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
    ]
    
    # Try each pattern
    for pattern in district_patterns:
        match = re.search(pattern, query)
        if match:
            district_name = match.group(1).strip()
            return clean_district_name(district_name)
    
    # If no match found through patterns, check for direct district mentions
    for district in MALAWI_DISTRICTS:
        if district.lower() in query:
            return district
    
    return None

def clean_district_name(district_name: str) -> str:
    """Clean and normalize a district name."""
    district_name = district_name.strip().title()
    normalized_key = district_name.lower().replace(" ", "")
    if normalized_key in DISTRICT_VARIATIONS:
        return DISTRICT_VARIATIONS[normalized_key]
    return district_name

def validate_district(district_name: str) -> Optional[str]:
    """Validate a district name against the list of known districts."""
    if district_name in MALAWI_DISTRICTS:
        return district_name
    matches = get_close_matches(district_name, MALAWI_DISTRICTS, n=1, cutoff=0.7)
    if matches:
        return matches[0]
    return None

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
    
    # Check for district first
    district_name = extract_district_from_query(query)
    if district_name:
        validated_district = validate_district(district_name)
        if validated_district:
            conditions.append(f"LOWER(DISTRICT) LIKE '%{validated_district.lower()}%'")
    
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
    else:
        sql_query += " ORDER BY TOTALBUDGET DESC"  # Default ordering
    
    sql_query += " LIMIT 10"  # Always limit results
    
    return {
        "query": sql_query,
        "is_specific_project": bool(quoted_matches or code_matches)
    } 