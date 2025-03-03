"""
Example implementation for improved district query handling in the RAG-SQL chatbot.
This code demonstrates how to enhance the system's ability to interpret various
district-based query formats.
"""

import re
from difflib import get_close_matches
from typing import Tuple, Optional, List

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
    """
    Extract district name from a query using enhanced pattern matching.
    
    Args:
        query: The user's natural language query
        
    Returns:
        The extracted district name or None if no district is found
    """
    # Normalize the query
    query = query.lower().strip()
    
    # Expanded patterns for district queries
    district_patterns = [
        # Standard patterns
        r'(?:projects|list).* (?:in|located in|based in|for) ([A-Za-z\s\-]+?)(?: district)?(?:\s|$|\.|\?)',
        r'([A-Za-z\s\-]+?) (?:district|region).* projects',
        r'show (?:me|all|the) projects.* (?:in|for|at) ([A-Za-z\s\-]+?)(?:\s|$|\.|\?)',
        
        # Additional patterns
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
    """
    Clean and normalize a district name, handling variations and typos.
    
    Args:
        district_name: The extracted district name
        
    Returns:
        Cleaned and normalized district name
    """
    # Basic normalization
    district_name = district_name.strip().title()
    
    # Check for known variations
    normalized_key = district_name.lower().replace(" ", "")
    if normalized_key in DISTRICT_VARIATIONS:
        return DISTRICT_VARIATIONS[normalized_key]
    
    return district_name

def validate_district(district_name: str) -> Optional[str]:
    """
    Validate a district name against the list of known districts,
    using fuzzy matching for slight variations.
    
    Args:
        district_name: The district name to validate
        
    Returns:
        The validated district name or None if invalid
    """
    # Direct match
    if district_name in MALAWI_DISTRICTS:
        return district_name
    
    # Fuzzy match
    matches = get_close_matches(district_name, MALAWI_DISTRICTS, n=1, cutoff=0.7)
    if matches:
        return matches[0]
    
    return None

def generate_district_sql_query(district: str, limit: int = 10, offset: int = 0) -> str:
    """
    Generate a SQL query for retrieving projects in a specific district.
    
    Args:
        district: The validated district name
        limit: Maximum number of results to return
        offset: Offset for pagination
        
    Returns:
        SQL query string
    """
    sql_query = f"""
    SELECT 
        projectname as project_name,
        fiscalyear as fiscal_year,
        district as location,
        budget as total_budget,
        projectstatus as status,
        projectsector as project_sector
    FROM 
        proj_dashboard 
    WHERE 
        LOWER(district) LIKE '%{district.lower()}%'
    ORDER BY 
        budget DESC
    LIMIT {limit}
    OFFSET {offset};
    """
    return sql_query.strip()

def process_district_query(query: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Process a user query to determine if it's a district-based query
    and generate the appropriate SQL query.
    
    Args:
        query: The user's natural language query
        
    Returns:
        Tuple of (is_district_query, district_name, sql_query)
    """
    # Extract district name
    district_name = extract_district_from_query(query)
    if not district_name:
        return False, None, None
    
    # Validate district name
    validated_district = validate_district(district_name)
    if not validated_district:
        # Log unrecognized district for future improvements
        print(f"Unrecognized district: {district_name}")
        return True, district_name, None
    
    # Generate SQL query
    sql_query = generate_district_sql_query(validated_district)
    return True, validated_district, sql_query

# Example usage
if __name__ == "__main__":
    test_queries = [
        "Show me all projects in Zomba district",
        "Which projects are in Dowa?",
        "List projects in Lilongwe",
        "Projects located in Blantyre",
        "What projects are being implemented in Karonga?",
        "Tell me about Mzimba projects",
        "Nkhata Bay district projects",
        "Projects in Mulanje",
        "Infrastructure in Chitipa",
        "Nkhatabay projects",  # Variation
        "Projects in Blantrye",  # Typo
    ]
    
    for query in test_queries:
        is_district, district, sql = process_district_query(query)
        if is_district and district and sql:
            print(f"Query: '{query}'")
            print(f"Detected District: {district}")
            print(f"SQL Query: {sql}")
            print("-" * 80)
        elif is_district and district:
            print(f"Query: '{query}'")
            print(f"Detected District: {district} (not validated)")
            print("-" * 80)
        else:
            print(f"Query: '{query}'")
            print("Not recognized as a district query")
            print("-" * 80) 