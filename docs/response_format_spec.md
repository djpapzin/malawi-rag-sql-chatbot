# Response Format Specification

## Response Types

### 1. General Query Response
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
      "budget": {
        "amount": "number",
        "formatted": "string"
      },
      "status": "string",
      "sector": "string"
    }
  ],
  "summary": {
    "total_projects": "number",
    "total_budget": {
      "amount": "number",
      "formatted": "string"
    }
  },
  "metadata": {
    "query_timestamp": "string",
    "query_id": "string"
  }
}
```

### 2. Specific Query Response
```json
{
  "query_type": "specific",
  "result": {
    "project_name": "string",
    "fiscal_year": "string",
    "location": {
      "region": "string",
      "district": "string"
    },
    "budget": {
      "amount": "number",
      "formatted": "string"
    },
    "status": "string",
    "contractor": {
      "name": "string",
      "contract_start_date": "string"
    },
    "expenditure_to_date": {
      "amount": "number",
      "formatted": "string"
    },
    "sector": "string",
    "funding_source": "string",
    "project_code": "string",
    "last_monitoring_visit": "string"
  },
  "metadata": {
    "query_timestamp": "string",
    "query_id": "string"
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
      "budget": {
        "amount": 50000000,
        "formatted": "MWK 50,000,000"
      },
      "status": "In Progress",
      "sector": "Infrastructure"
    }
  ],
  "summary": {
    "total_projects": 15,
    "total_budget": {
      "amount": 142925000,
      "formatted": "MWK 142,925,000"
    }
  },
  "metadata": {
    "query_timestamp": "2024-02-21T15:22:34Z",
    "query_id": "10dcb284-c277-407e"
  }
}
```

### Specific Query Example
Query: "Show me details for Mangochi Road Rehabilitation project"
```json
{
  "query_type": "specific",
  "result": {
    "project_name": "Mangochi Road Rehabilitation",
    "fiscal_year": "2023-2024",
    "location": {
      "region": "Southern",
      "district": "Mangochi"
    },
    "budget": {
      "amount": 50000000,
      "formatted": "MWK 50,000,000"
    },
    "status": "In Progress",
    "contractor": {
      "name": "ABC Construction Ltd",
      "contract_start_date": "2023-07-01"
    },
    "expenditure_to_date": {
      "amount": 25000000,
      "formatted": "MWK 25,000,000"
    },
    "sector": "Infrastructure",
    "funding_source": "World Bank",
    "project_code": "MNG-RD-2023-001",
    "last_monitoring_visit": "2024-01-15"
  },
  "metadata": {
    "query_timestamp": "2024-02-21T15:22:34Z",
    "query_id": "10dcb284-c277-407e"
  }
}
```

## Implementation Steps

1. Update Response Models
   - Create new Pydantic models in `app/models.py`
   - Add type validation for all fields
   - Implement currency and date formatting

2. Update Query Processing
   - Add query type detection
   - Modify SQL queries to fetch appropriate fields
   - Implement field mapping from database to response format

3. Add Data Formatting
   - Currency formatting for budget and expenditure
   - Date formatting for all date fields
   - Location formatting (region/district) 