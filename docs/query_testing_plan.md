# Testing Plan for Query Interpretation Improvements

This document outlines a systematic approach to test the RAG-SQL chatbot's ability to correctly interpret various query formats after implementing the recommended improvements.

## Test Categories

### 1. District-Based Queries

Test all variations documented in `query_variations.md`, including:

| Query Format | Example | Expected Result |
|--------------|---------|-----------------|
| Show me all projects in [District] district | "Show me all projects in Dowa district" | Projects in Dowa district |
| Which projects are in [District]? | "Which projects are in Dowa?" | Projects in Dowa district |
| List projects in [District] | "List projects in Dowa" | Projects in Dowa district |
| Projects located in [District] | "Projects located in Dowa" | Projects in Dowa district |
| What projects are being implemented in [District]? | "What projects are being implemented in Dowa?" | Projects in Dowa district |
| Tell me about [District] projects | "Tell me about Dowa projects" | Projects in Dowa district |
| [District] district projects | "Dowa district projects" | Projects in Dowa district |
| Find projects in [District] | "Find projects in Dowa" | Projects in Dowa district |
| Give me a list of [District] projects | "Give me a list of Dowa projects" | Projects in Dowa district |
| What's happening in [District]? | "What's happening in Dowa?" | Projects in Dowa district |
| [District] development initiatives | "Dowa development initiatives" | Projects in Dowa district |
| Infrastructure in [District] | "Infrastructure in Dowa" | Projects in Dowa district |
| Current projects in [District] | "Current projects in Dowa" | Projects in Dowa district |
| [District] area projects | "Dowa area projects" | Projects in Dowa district |

### 2. Edge Cases

| Query | Expected Result |
|-------|-----------------|
| "Dowa" (just the district name) | Projects in Dowa district |
| "Projects with Dowa in the name" | Projects with "Dowa" in the project name |
| "Projects near Dowa" | Projects in Dowa district |
| "Dowa district" | Projects in Dowa district |
| "Tell me about the Dowa Turn Off Market project" | Specific project details |
| "Compare Dowa and Lilongwe projects" | Projects in both districts |

### 3. Typos and Variations

| Query | Expected Result |
|-------|-----------------|
| "Projects in Dwa" (typo) | Projects in Dowa district |
| "Projects in dowa" (lowercase) | Projects in Dowa district |
| "Projects in DOWA" (uppercase) | Projects in Dowa district |
| "Projects in Dowa District" (capitalized) | Projects in Dowa district |

### 4. Combined Filters

| Query | Expected Result |
|-------|-----------------|
| "Health projects in Dowa" | Health sector projects in Dowa district |
| "Completed projects in Dowa" | Completed projects in Dowa district |
| "Ongoing projects in Dowa" | Ongoing projects in Dowa district |
| "Bridge projects in Dowa" | Bridge-related projects in Dowa district |
| "High budget projects in Dowa" | High budget projects in Dowa district |
| "Recent projects in Dowa" | Recent projects in Dowa district |

### 5. Context Maintenance

| Query Sequence | Expected Result |
|----------------|-----------------|
| 1. "Show me projects in Dowa" <br> 2. "Which ones are related to health?" | 1. Projects in Dowa <br> 2. Health projects in Dowa |
| 1. "Projects in Dowa" <br> 2. "What about in Lilongwe?" | 1. Projects in Dowa <br> 2. Projects in Lilongwe |
| 1. "Show me Dowa projects" <br> 2. "Sort by budget" | 1. Projects in Dowa <br> 2. Projects in Dowa sorted by budget |

## Testing Methodology

### Automated Testing

Create a script to automatically run all test queries and verify the results:

```python
import requests
import json

def test_query(query, expected_district=None):
    """
    Test a query and check if it returns results for the expected district
    """
    response = requests.post(
        "http://154.0.164.254:5000/api/rag-sql-chatbot/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"message": query})
    )
    
    data = response.json()
    
    # Check if the SQL query contains the expected district filter
    sql_query = data.get("metadata", {}).get("sql_query", "").lower()
    
    if expected_district:
        district_filter = f"district like '%{expected_district.lower()}%'"
        if district_filter not in sql_query:
            print(f"❌ FAIL: Query '{query}' did not filter by {expected_district}")
            print(f"SQL: {sql_query}")
            return False
        else:
            print(f"✅ PASS: Query '{query}' correctly filtered by {expected_district}")
            return True
    
    return None

# Run tests
test_cases = [
    {"query": "Show me all projects in Dowa district", "expected_district": "Dowa"},
    {"query": "Which projects are in Dowa?", "expected_district": "Dowa"},
    {"query": "List projects in Dowa", "expected_district": "Dowa"},
    # Add all test cases here
]

for test in test_cases:
    test_query(test["query"], test["expected_district"])
```

### Manual Testing

For each test category:

1. Execute the query using the chat interface
2. Verify that the results are filtered by the correct district
3. Check the SQL query in the metadata to confirm the correct WHERE clause is used
4. Document any discrepancies or unexpected behaviors

## Test Results Documentation

Create a test results document with the following format:

```
# Query Interpretation Test Results

Date: YYYY-MM-DD
Version: X.X.X

## Summary
- Total Tests: XX
- Passed: XX
- Failed: XX
- Pass Rate: XX%

## Detailed Results

### District-Based Queries
| Query | Expected | Actual | SQL Query | Status |
|-------|----------|--------|-----------|--------|
| "Show me all projects in Dowa district" | Dowa projects | Dowa projects | SELECT ... WHERE district LIKE '%dowa%' | ✅ PASS |
| ... | ... | ... | ... | ... |

### Edge Cases
...

### Typos and Variations
...

### Combined Filters
...

### Context Maintenance
...

## Issues Identified
1. ...
2. ...

## Recommendations
1. ...
2. ...
```

## Continuous Improvement

After each testing cycle:

1. Identify patterns in failed queries
2. Update the query classification logic to handle these patterns
3. Refine the LLM prompts based on test results
4. Re-test to verify improvements

## Success Criteria

The implementation will be considered successful when:

1. At least 90% of the district-based query variations return the correct district-filtered results
2. Edge cases are handled appropriately
3. The system can handle typos and variations in district names
4. Combined filters work correctly with district filters
5. Context is maintained appropriately across related queries 