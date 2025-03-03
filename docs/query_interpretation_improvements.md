# Query Interpretation Improvements

Based on our testing of various query formats, we've identified several areas where the RAG-SQL chatbot's query interpretation can be improved. This document outlines specific recommendations for enhancing the system's ability to understand user intent, particularly for district-based queries.

## Current Issues

1. **Limited Pattern Recognition**: The system only recognizes a few specific patterns for district-based queries, missing many common variations.
2. **Rigid Pattern Matching**: The current regex patterns are too strict and miss slight variations in phrasing.
3. **Incomplete District Validation**: The list of valid districts is incomplete, causing valid district queries to fall back to general queries.
4. **Lack of Entity Recognition**: The system doesn't effectively identify district names as location entities regardless of query structure.

## Recommended Improvements

### 1. Expand District Query Patterns

The current implementation has only three patterns for district queries:
```python
district_patterns = [
    r'(?:projects|list).* (?:in|located in|based in|for) (\w+)(?: district)?',
    r'(\w+) (?:district|region).* projects',
    r'show (?:me|all) projects.* (\w+)'
]
```

We should expand these patterns to include more variations:

```python
district_patterns = [
    # Existing patterns
    r'(?:projects|list).* (?:in|located in|based in|for) (\w+)(?: district)?',
    r'(\w+) (?:district|region).* projects',
    r'show (?:me|all) projects.* (\w+)',
    
    # New patterns
    r'which projects are (?:in|located in|based in) (\w+)',
    r'what projects are (?:in|located in|being implemented in) (\w+)',
    r'tell me about (\w+) (?:district)? projects',
    r'projects (?:in|from|of) (\w+)(?: district)?',
    r'(\w+) projects',
    r'(?:all)? projects (?:in|for) (\w+)',
]
```

### 2. Improve District Name Extraction

The current implementation has limitations in extracting district names:

1. It only matches single-word district names (`\w+`)
2. It doesn't handle multi-word district names (e.g., "Nkhata Bay")
3. It doesn't account for potential typos or variations

Improved implementation:

```python
# Use a more flexible pattern for district names
r'(?:projects|list).* (?:in|located in|based in|for) ([A-Za-z\s\-]+?)(?: district)?'

# After extraction, clean up the district name
if district_name:
    district_name = district_name.strip().title()
    # Handle common variations and typos
    district_name_mapping = {
        "Nkhatabay": "Nkhata Bay",
        "Mzimbadistrict": "Mzimba",
        # Add more mappings as needed
    }
    district_name = district_name_mapping.get(district_name.replace(" ", ""), district_name)
```

### 3. Complete District Validation List

The current implementation has an incomplete list of valid districts:

```python
valid_districts = ['Dowa', 'Lilongwe', 'Mwanza', 'Karonga']  # Add full list
```

We should include all districts in Malawi:

```python
valid_districts = [
    'Balaka', 'Blantyre', 'Chikwawa', 'Chiradzulu', 'Chitipa', 'Dedza', 
    'Dowa', 'Karonga', 'Kasungu', 'Likoma', 'Lilongwe', 'Machinga', 
    'Mangochi', 'Mchinji', 'Mulanje', 'Mwanza', 'Mzimba', 'Neno', 
    'Nkhata Bay', 'Nkhotakota', 'Nsanje', 'Ntcheu', 'Ntchisi', 'Phalombe', 
    'Rumphi', 'Salima', 'Thyolo', 'Zomba'
]
```

### 4. Implement Fuzzy Matching for Districts

To handle slight variations or typos in district names, implement fuzzy matching:

```python
from difflib import get_close_matches

def find_closest_district(input_district, valid_districts, cutoff=0.7):
    """Find the closest matching district using fuzzy matching"""
    matches = get_close_matches(input_district, valid_districts, n=1, cutoff=cutoff)
    return matches[0] if matches else None

# In the query generation function
extracted_district = district_name.strip().title()
district_name = find_closest_district(extracted_district, valid_districts)
if district_name:
    # Proceed with district query
    ...
else:
    # Fall back to other query types
    ...
```

### 5. Implement a Fallback Mechanism

When a district name is detected but doesn't match the validation list, instead of falling back to a general query, we should:

1. Log the unrecognized district for future improvements
2. Try fuzzy matching to find the closest district
3. If no match is found, inform the user that the district wasn't recognized

```python
if extracted_district and not district_name:
    logger.info(f"Unrecognized district: {extracted_district}")
    return "", "unknown_district"  # Handle this case in the response generation
```

### 6. Implement Context-Aware Query Processing

Enhance the query processing to be more context-aware:

```python
# Extract potential entities from the query
entities = extract_entities(user_query)

# If a location entity is found, prioritize district-based query
if 'location' in entities:
    district_name = entities['location']
    # Validate and process district query
    ...
```

## Implementation Plan

1. **Short-term fixes**:
   - Expand the district query patterns
   - Complete the list of valid districts
   - Improve district name extraction

2. **Medium-term improvements**:
   - Implement fuzzy matching for districts
   - Add the fallback mechanism
   - Log unrecognized patterns for continuous improvement

3. **Long-term enhancements**:
   - Implement context-aware query processing
   - Consider using a more sophisticated NLP approach for entity recognition
   - Develop a feedback loop to learn from user interactions 