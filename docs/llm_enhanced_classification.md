# LLM-Enhanced Query Classification Proposal

## Current Approach vs. Proposed Approach

### Current Approach
The current system relies heavily on regex patterns to identify query types and extract entities like district names. While this works for standard phrasings, it has limitations:

1. Brittle to variations in phrasing
2. Requires manual pattern creation for each query type
3. Difficult to maintain as query complexity increases
4. Limited ability to handle ambiguous or complex queries

### Proposed Hybrid Approach
We propose a hybrid system that combines the strengths of both regex and LLM-based classification:

1. **First Pass: Regex Patterns**
   - Fast and deterministic for common query patterns
   - No API call overhead for straightforward queries
   - Handles the majority of expected query formats

2. **Second Pass: LLM Classification**
   - Processes queries that don't match regex patterns
   - Extracts intent and parameters from natural language
   - Handles variations, typos, and complex phrasings
   - Provides more robust entity extraction

## Implementation Plan

### 1. LLM Classification Function

```python
async def classify_query_with_llm(user_query: str) -> dict:
    """
    Use LLM to classify the query type and extract relevant parameters.
    
    Args:
        user_query: The user's natural language query
        
    Returns:
        dict: Classification results with query type and extracted parameters
    """
    # Construct a prompt that asks the LLM to classify the query
    prompt = f"""
    You are an assistant for a Malawi infrastructure project database.
    Classify this user query: "{user_query}"
    
    Return a JSON object with the following structure:
    {{
        "query_type": "district|project|sector|budget|status|time|combined",
        "parameters": {{
            "districts": ["district_name1", "district_name2"],
            "projects": ["project_name1", "project_name2"],
            "sectors": ["sector_name1", "sector_name2"],
            "budget_range": {{"min": null, "max": null}},
            "status": ["completed", "in_progress", "planned"],
            "time_range": {{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}
        }}
    }}
    
    Only include parameters that are relevant to the query.
    """
    
    # Call the LLM API with the prompt
    llm_response = await call_llm_api(prompt)
    
    # Parse the JSON response
    try:
        classification = json.loads(llm_response)
        return classification
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return valid JSON
        return {
            "query_type": "unknown",
            "parameters": {}
        }
```

### 2. Integration into Query Processing Pipeline

```python
async def process_user_query(user_query: str):
    """
    Process a user query using the hybrid approach.
    
    Args:
        user_query: The user's natural language query
        
    Returns:
        dict: Query results
    """
    # First try regex patterns
    regex_result = try_regex_patterns(user_query)
    
    if regex_result and regex_result["query_type"] != "unknown":
        # If regex found a match, use it
        classification = regex_result
    else:
        # Otherwise, fall back to LLM classification
        classification = await classify_query_with_llm(user_query)
    
    # Generate SQL based on the classification
    sql_query = generate_sql_from_classification(classification)
    
    # Execute the query and return results
    results = await execute_sql_query(sql_query)
    return results
```

### 3. SQL Generation from Classification

```python
def generate_sql_from_classification(classification: dict) -> str:
    """
    Generate SQL query based on the classification.
    
    Args:
        classification: Query classification with type and parameters
        
    Returns:
        str: SQL query
    """
    query_type = classification["query_type"]
    params = classification["parameters"]
    
    # Base query
    sql = "SELECT * FROM projects"
    where_clauses = []
    
    # Add filters based on parameters
    if "districts" in params and params["districts"]:
        districts = ", ".join([f"'{d}'" for d in params["districts"]])
        where_clauses.append(f"district IN ({districts})")
    
    if "sectors" in params and params["sectors"]:
        sectors = ", ".join([f"'{s}'" for s in params["sectors"]])
        where_clauses.append(f"sector IN ({sectors})")
    
    if "projects" in params and params["projects"]:
        project_clauses = []
        for project in params["projects"]:
            project_clauses.append(f"title LIKE '%{project}%'")
        where_clauses.append("(" + " OR ".join(project_clauses) + ")")
    
    if "budget_range" in params:
        budget = params["budget_range"]
        if budget.get("min") is not None:
            where_clauses.append(f"budget >= {budget['min']}")
        if budget.get("max") is not None:
            where_clauses.append(f"budget <= {budget['max']}")
    
    if "status" in params and params["status"]:
        statuses = ", ".join([f"'{s}'" for s in params["status"]])
        where_clauses.append(f"status IN ({statuses})")
    
    if "time_range" in params:
        time_range = params["time_range"]
        if time_range.get("start") is not None:
            where_clauses.append(f"start_date >= '{time_range['start']}'")
        if time_range.get("end") is not None:
            where_clauses.append(f"end_date <= '{time_range['end']}'")
    
    # Add WHERE clause if we have conditions
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    # Add limit
    sql += " LIMIT 10"
    
    return sql
```

## Benefits of the Hybrid Approach

1. **Improved Robustness**
   - Handles a wider variety of query phrasings
   - Better tolerance for typos and grammatical errors
   - Can understand implicit intents

2. **Reduced Maintenance**
   - Less need to manually create and update regex patterns
   - Automatically adapts to new query variations

3. **Enhanced User Experience**
   - More natural interaction with the chatbot
   - Higher success rate for non-standard queries
   - Better handling of complex, multi-parameter queries

4. **Graceful Degradation**
   - If the LLM service is unavailable, falls back to regex patterns
   - If regex patterns don't match, tries LLM classification

## Implementation Considerations

1. **Performance**
   - LLM API calls add latency
   - Cache common query classifications to improve response time

2. **Cost**
   - LLM API calls have associated costs
   - Use regex for common patterns to minimize API usage

3. **Error Handling**
   - Implement robust error handling for LLM API failures
   - Provide graceful fallbacks when classification fails

4. **Testing**
   - Comprehensive testing with the query variations document
   - Regular evaluation of classification accuracy
   - A/B testing of regex vs. LLM approaches

## Next Steps

1. Implement the LLM classification function
2. Integrate with existing query processing pipeline
3. Set up monitoring for classification accuracy
4. Develop a feedback loop to improve classification over time
5. Establish metrics for evaluating system performance
