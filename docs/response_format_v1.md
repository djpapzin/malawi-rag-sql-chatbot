# Response Format Specification V1

## Query Types and Response Formats

### 1. General Query Format
```json
{
  "query_type": "general",
  "results": [
    {
      "project_name": "string",
      "fiscal_year": "string",
      "location": {
        "region": "string",
        "district": "string"
      },
      "total_budget": {
        "amount": "number",
        "formatted": "string"
      },
      "project_status": "string",
      "project_sector": "string"
    }
  ],
  "metadata": {
    "total_results": "number",
    "query_time": "string",
    "sql_query": "string"
  }
}
```

### 2. Specific Query Format
```json
{
  "query_type": "specific",
  "results": [
    {
      "project_name": "string",
      "fiscal_year": "string",
      "location": {
        "region": "string",
        "district": "string"
      },
      "total_budget": {
        "amount": "number",
        "formatted": "string"
      },
      "project_status": "string",
      "contractor": {
        "name": "string",
        "contract_start_date": "string"
      },
      "expenditure_to_date": {
        "amount": "number",
        "formatted": "string"
      },
      "project_sector": "string",
      "source_of_funding": "string",
      "project_code": "string",
      "last_monitoring_visit": "string"
    }
  ],
  "metadata": {
    "total_results": "number",
    "query_time": "string",
    "sql_query": "string"
  }
}
```

## Example Responses

### General Query Example
Query: "Show me all infrastructure projects"
```json
{
  "query_type": "general",
  "results": [
    {
      "project_name": "Mangochi Road Rehabilitation",
      "fiscal_year": "2023-2024",
      "location": {
        "region": "Southern",
        "district": "Mangochi"
      },
      "total_budget": {
        "amount": 50000000,
        "formatted": "MWK 50,000,000"
      },
      "project_status": "In Progress",
      "project_sector": "Infrastructure"
    }
  ],
  "metadata": {
    "total_results": 1,
    "query_time": "2024-02-21T15:30:00Z",
    "sql_query": "SELECT projectname, fiscalyear, region, district, totalbudget, projectstatus, projectsector FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'"
  }
}
```

### Specific Query Example
Query: "Give me details about the Mangochi Road Rehabilitation project"
```json
{
  "query_type": "specific",
  "results": [
    {
      "project_name": "Mangochi Road Rehabilitation",
      "fiscal_year": "2023-2024",
      "location": {
        "region": "Southern",
        "district": "Mangochi"
      },
      "total_budget": {
        "amount": 50000000,
        "formatted": "MWK 50,000,000"
      },
      "project_status": "In Progress",
      "contractor": {
        "name": "ABC Construction Ltd",
        "contract_start_date": "2023-07-01"
      },
      "expenditure_to_date": {
        "amount": 25000000,
        "formatted": "MWK 25,000,000"
      },
      "project_sector": "Infrastructure",
      "source_of_funding": "World Bank",
      "project_code": "MNG-RD-2023-001",
      "last_monitoring_visit": "2024-01-15"
    }
  ],
  "metadata": {
    "total_results": 1,
    "query_time": "2024-02-21T15:30:00Z",
    "sql_query": "SELECT * FROM proj_dashboard WHERE projectname = 'Mangochi Road Rehabilitation'"
  }
}
```

## Implementation Notes

1. Database Field Mappings:
   - PROJECTNAME -> project_name
   - FISCALYEAR -> fiscal_year
   - REGION -> location.region
   - DISTRICT -> location.district
   - TOTALBUDGET -> total_budget.amount
   - PROJECTSTATUS -> project_status
   - PROJECTSECTOR -> project_sector

2. Formatting Rules:
   - Currency amounts should be formatted with thousands separators
   - Dates should be in ISO format (YYYY-MM-DD)
   - Status values should be properly capitalized
   - All string values should be trimmed of whitespace

3. Query Type Detection:
   - General queries typically ask for lists or summaries
   - Specific queries typically ask for details about a particular project
   - Query type should be determined by the presence of specific project identifiers or keywords 