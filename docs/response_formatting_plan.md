# Response Formatting Improvement Plan

## Current Response Format
```json
{
  "response": "The total budget for infrastructure projects is $142,925,000.00...",
  "metadata": {
    "timestamp": "2025-02-21T15:22:34.508864",
    "query_id": "10dcb284-c277-407e-9d68-195d0afdd01d",
    "processing_time": 6.873861074447632
  },
  "source": {
    "type": "sql",
    "sql": "select sum(budget) from proj_dashboard where lower(projectsector) = 'infrastructure';",
    "database": "malawi_projects1.db"
  }
}
```

## Issues to Address
1. Response text contains debugging information and internal steps
2. Numbers are not properly formatted for human readability
3. No clear separation between the answer and supporting information
4. Metadata could be more useful for frontend applications
5. SQL query is shown in raw format

## Proposed Improvements

### 1. Structured Response Format
```json
{
  "answer": {
    "text": "The total budget for infrastructure projects is $142,925,000.",
    "values": {
      "total_budget": 142925000,
      "currency": "USD",
      "formatted_value": "$142,925,000"
    }
  },
  "context": {
    "sector": "infrastructure",
    "project_count": 15,
    "data_timestamp": "2024-02-21"
  },
  "metadata": {
    "timestamp": "2024-02-21T15:22:34Z",
    "query_id": "10dcb284-c277-407e",
    "processing_time_ms": 6873,
    "confidence_score": 0.95
  },
  "source": {
    "type": "sql",
    "query": {
      "raw": "SELECT SUM(budget) FROM proj_dashboard WHERE LOWER(projectsector) = 'infrastructure'",
      "formatted": "SELECT SUM(budget)\nFROM proj_dashboard\nWHERE LOWER(projectsector) = 'infrastructure'",
      "tables": ["proj_dashboard"],
      "columns": ["budget", "projectsector"]
    },
    "database": "malawi_projects1.db"
  }
}
```

### 2. Implementation Steps

#### Phase 1: Response Structure
1. Create new response models in `app/models.py`
   - Separate answer structure from metadata
   - Add structured value fields for numerical responses
   - Include confidence scores

#### Phase 2: Data Formatting
1. Implement number formatting utilities
   - Currency formatting with proper localization
   - Date/time standardization
   - Percentage formatting
2. Add SQL query formatting and cleaning
   - Pretty print SQL queries
   - Extract table and column information

#### Phase 3: Context Enhancement
1. Add relevant contextual information
   - Project counts
   - Date ranges
   - Related categories/sectors
2. Implement confidence scoring
   - Based on query understanding
   - Data completeness metrics

#### Phase 4: Frontend Integration
1. Update frontend components to use new structure
   - Display formatted values
   - Show/hide technical details
   - Add visual indicators for confidence scores

### 3. Technical Requirements

1. New Dependencies
   - `babel` for number/currency formatting
   - `sqlparse` for SQL formatting
   - `pydantic` updates for new models

2. Code Structure Updates
   - New formatting utilities module
   - Enhanced response models
   - SQL analysis utilities
   - Test suite for formatting functions

### 4. Success Metrics

1. User Experience
   - Clearer, more concise answers
   - Consistent number formatting
   - Better context for answers

2. Technical
   - 100% test coverage for formatting functions
   - Response time impact < 50ms
   - Backward compatibility with existing clients

## Timeline

1. Phase 1: 1 week
   - Model updates
   - Basic formatting implementation

2. Phase 2: 1 week
   - Formatting utilities
   - SQL enhancement

3. Phase 3: 1 week
   - Context generation
   - Confidence scoring

4. Phase 4: 1 week
   - Frontend updates
   - Testing and optimization

## Next Steps

1. Create new branch for formatting updates
2. Implement basic response models
3. Add formatting utilities
4. Update tests
5. Create PR for review 