# Infrastructure Projects Query Response Plan

## Overview
This document outlines the implementation of query responses for the Infrastructure Transparency Chatbot. The chatbot provides access to infrastructure project information from the `malawi_projects1.db` database.

## Query Types and Responses

### 1. General Project Queries

#### Input Pattern Examples
- "Show me education projects"
- "List health projects in Southern Region"
- "What projects are completed in Lilongwe?"

#### Response Format
```
Project: [PROJECTNAME]
Sector: [PROJECTSECTOR]
Location: [REGION], [DISTRICT]
Status: [PROJECTSTATUS]
Budget: MWK [TOTALBUDGET formatted with commas]
Completion: [COMPLETIONPERCENTAGE]%
```

#### Implementation Details
- Implemented in `response_generator.py`
- Uses `_format_project_list()` method
- Handles pagination automatically
- Formats currency and percentages
- Provides "Not available" for null values

### 2. Specific Project Queries

#### Input Pattern Examples
- "Tell me about Project X"
- "Show details for Completion of Staff House"
- "What is the status of Project Y?"

#### Response Format
```markdown
# [PROJECTNAME]
Project Code: [PROJECTCODE]
Sector: [PROJECTSECTOR]
Status: [PROJECTSTATUS]
Stage: [STAGE]

## Location
Region: [REGION]
District: [DISTRICT]
Traditional Authority: [TRADITIONALAUTHORITY]

## Financial Details
Total Budget: MWK [TOTALBUDGET]
Total Expenditure to Date: MWK [TOTALEXPENDITURETODATE]
Funding Source: [FUNDINGSOURCE]

## Timeline
Start Date: [STARTDATE]
Estimated Completion Date: [COMPLETIONESTIDATE]
Last Site Visit: [LASTVISIT]
Completion Percentage: [COMPLETIONPERCENTAGE]%

## Contractor Details
Contractor: [CONTRACTORNAME]
Contract Signing Date: [SIGNINGDATE]

## Project Description
[PROJECTDESC]
```

#### Implementation Details
- Implemented in `response_generator.py`
- Uses `_format_single_project()` method
- Formats dates as "Month DD, YYYY"
- Formats currency with commas and 2 decimal places
- Sections information for better readability
- Handles missing data gracefully

### 3. Error Handling

#### No Results Found
```
"No projects found matching your criteria."
```

#### Invalid Query
```
"I couldn't understand your query. Please try asking about specific projects, sectors, or locations."
```

#### Database Error
```
"Sorry, I encountered an error while fetching the data. Please try again."
```

## Implementation Notes

### 1. Data Formatting
- Currency: "MWK 123,456.78"
- Dates: "February 18, 2025"
- Percentages: "45.5%"
- Null values: "Not available"

### 2. Performance Optimizations
- Efficient DataFrame handling
- Proper connection management
- Query result caching
- Pagination support

### 3. Testing Coverage
- General queries
- Specific project queries
- Edge cases
- Response formatting
- Error scenarios

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
