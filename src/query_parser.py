import re
from typing import Optional, Dict
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

# Common sectors and their variations
SECTORS = {
    "agriculture": ["agriculture", "farming", "food security", "crop", "livestock"],
    "education": ["education", "school", "university", "college", "learning"],
    "health": ["health", "hospital", "clinic", "medical", "healthcare"],
    "infrastructure": ["infrastructure", "road", "bridge", "transport", "construction"],
    "energy": ["energy", "power", "electricity", "solar", "hydro"],
    "water": ["water", "sanitation", "irrigation", "water supply", "wastewater"],
    "rural development": ["rural", "village", "community", "development"],
    "urban development": ["urban", "city", "town", "municipal"],
    "environment": ["environment", "climate", "conservation", "forestry"],
    "governance": ["governance", "administration", "public sector", "government"]
}

def validate_sector(sector_name: str) -> Optional[str]:
    """Validate and normalize a sector name."""
    sector_name = sector_name.lower().strip()
    
    # Check for exact matches in sector names
    for main_sector, variations in SECTORS.items():
        if sector_name in variations or sector_name == main_sector:
            return main_sector.title()
    
    # Try fuzzy matching for close matches
    for main_sector, variations in SECTORS.items():
        for variation in variations:
            if get_close_matches(sector_name, [variation], n=1, cutoff=0.7):
                return main_sector.title()
    
    return None

def clean_project_name(project_name: str) -> str:
    """Clean and normalize a project name."""
    # Remove common prefixes and suffixes
    prefixes = ["the ", "a ", "an "]
    suffixes = [" project", " scheme", " program", " programme"]
    
    name = project_name.strip()
    name = name.lower()
    
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    
    return name.strip()

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
    
    # Use LLM to classify the query
    classification = llm_service.classify_query(query)
    query_type = classification["query_type"]
    extracted_info = classification["extracted_info"]
    
    conditions = []
    order_by = []
    
    # Build base query based on classification
    if query_type == "specific_project":
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
        
        # Add conditions based on extracted info
        if extracted_info.get("project_name"):
            project_name = clean_project_name(extracted_info["project_name"])
            conditions.append(f"LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%')")
            # Improved ordering for project name matches
            order_by.append(f"""
                CASE 
                    WHEN LOWER(PROJECTNAME) = LOWER('{project_name}') THEN 1
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name}%') THEN 2
                    WHEN LOWER(PROJECTNAME) LIKE LOWER('%{project_name.split()[0]}%') THEN 3
                    ELSE 4
                END
            """)
    
    elif query_type == "district_query":
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
        
        if extracted_info.get("district"):
            district = extracted_info["district"].strip()
            validated_district = validate_district(district)
            if validated_district:
                conditions.append(f"LOWER(DISTRICT) LIKE '%{validated_district.lower()}%'")
    
    elif query_type == "sector_query":
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
        
        if extracted_info.get("sector"):
            sector = extracted_info["sector"].strip()
            validated_sector = validate_sector(sector)
            if validated_sector:
                conditions.append(f"LOWER(PROJECTSECTOR) LIKE LOWER('%{validated_sector}%')")
                # Add ordering to prioritize exact sector matches
                order_by.append(f"""
                    CASE 
                        WHEN LOWER(PROJECTSECTOR) = LOWER('{validated_sector}') THEN 1
                        WHEN LOWER(PROJECTSECTOR) LIKE LOWER('%{validated_sector}%') THEN 2
                        ELSE 3
                    END
                """)
    
    else:  # general_query
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
    
    # Add additional conditions based on extracted info
    if extracted_info.get("status"):
        status = extracted_info["status"].strip()
        conditions.append(f"LOWER(PROJECTSTATUS) LIKE LOWER('%{status}%')")
    
    if extracted_info.get("budget"):
        budget = extracted_info["budget"].strip()
        conditions.append(f"TOTALBUDGET LIKE '%{budget}%'")
    
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
        "is_specific_project": classification["is_specific_project"],
        "query_type": query_type,
        "confidence": classification["confidence"]
    } 