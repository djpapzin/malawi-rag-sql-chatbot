# Infrastructure Projects Query Response Plan

## Overview
This document outlines the implementation of query responses for the Infrastructure Transparency Chatbot. The chatbot provides access to infrastructure project information from the `malawi_projects1.db` database.

## 1. General Query Responses

### Core Fields
For general queries about multiple projects, the following fields are displayed:
- Project Name (`PROJECTNAME`)
- Fiscal Year (`FISCALYEAR`)
- Region (`REGION`)
- District (`DISTRICT`)
- Total Budget (`TOTALBUDGET`)
- Project Status (`PROJECTSTATUS`)
- Project Sector (`PROJECTSECTOR`)

### Response Format
1. **Project List View**
   ```sql
   SELECT 
       PROJECTNAME,
       FISCALYEAR,
       REGION,
       DISTRICT,
       TOTALBUDGET,
       PROJECTSTATUS,
       PROJECTSECTOR
   FROM proj_dashboard 
   WHERE ISLATEST = 1
   ORDER BY PROJECTNAME ASC
   ```

2. **Summary Statistics**
   The response includes aggregated information:
   - Total projects per region
   - Projects by sector
   - Budget allocation by sector
   - Status distribution

## 2. Specific Project Queries

### Detailed Fields
When querying a specific project, additional details are included:
- All core fields (from general queries)
- Contractor Name (`CONTRACTORNAME`)
- Contract Start Date (`CONTRACTSTARTDATE`)
- Total Expenditure (`TOTALEXPENDITURETODATE`)
- Funding Source (`FUNDINGSOURCE`)
- Project Code (`PROJECTCODE`)
- Last Monitoring Visit (`LASTVISIT`)

### Implementation Details

1. **Query Processing**
   - Natural language queries are parsed to identify project-specific indicators
   - Results are paginated (30 items per page)
   - Language support for English, Russian, and Uzbek

2. **Response Formatting**
   - Project information is displayed in a structured format
   - Budget values include currency formatting
   - Dates are formatted according to locale
   - Statistics are presented in a clear, summarized format

3. **Additional Features**
   - Suggested follow-up questions based on query context
   - Error handling for no results or invalid queries
   - Support for "show more" pagination requests

## API Endpoint

The chatbot uses a single endpoint for all queries:
```
POST /query
Content-Type: application/json

{
    "message": "Show me all projects in Lilongwe",
    "language": "english",
    "page": 1,
    "page_size": 30
}
```

## Response Structure
```json
{
    "response": "Project information...",
    "metadata": {
        "total_results": 10,
        "current_page": 1,
        "total_pages": 1,
        "has_more": false
    },
    "suggested_questions": [
        "What is the status of Project X?",
        "Show me projects in Region Y"
    ]
}
