# Infrastructure Projects Chatbot Documentation

## Overview

The Infrastructure Projects Chatbot (Dwizani) is designed to make it easy for users to get information about infrastructure projects in Malawi. This document explains both the user-facing functionality and the technical implementation details.

## User Guide

### Basic Operation

```mermaid
graph TD
    A[User] -->|Ask a question| B[Chatbot Interface]
    B -->|Process Query| C[FastAPI Backend]
    C -->|Generate SQL| D[LangChain SQL]
    D -->|Query Database| E[SQLite DB]
    E -->|Format Response| F[Response Generator]
    F -->|Display Results| A
```

### Response Types

1. **General Query Response**
   ```mermaid
   graph TD
       A[General Response] --> B[Project Name]
       A --> C[Fiscal Year]
       A --> D[Location]
       D --> D1[Region]
       D --> D2[District]
       A --> E[Total Budget]
       A --> F[Project Status]
       A --> G[Project Sector]
   ```

2. **Specific Query Response**
   ```mermaid
   graph TD
       A[Detailed Response] --> B[Basic Info]
       B --> B1[Project Name]
       B --> B2[Fiscal Year]
       B --> B3[Location]
       B3 --> B3a[Region]
       B3 --> B3b[District]
       A --> C[Financial Info]
       C --> C1[Total Budget]
       C --> C2[Expenditure to Date]
       C --> C3[Source of Funding]
       A --> D[Project Details]
       D --> D1[Project Status]
       D --> D2[Project Sector]
       D --> D3[Project Code]
       A --> E[Contractor Info]
       E --> E1[Contractor Name]
       E --> E2[Contract Start Date]
       A --> F[Monitoring]
       F --> F1[Last Council Visit]
   ```

## Technical Implementation

### System Architecture

```mermaid
flowchart TD
    A[Frontend - HTML/JS] -->|HTTP POST| B[FastAPI Backend :5000]
    B --> C[LangChain Integration]
    C --> D[Together AI LLM]
    D -->|SQL Generation| E[Query Generator]
    E -->|Execute Query| F[(SQLite Database)]
    F -->|Raw Results| G[Response Formatter]
    G -->|Structured JSON| B
    B -->|JSON Response| A
```

### API Endpoints

1. **Health Check**
   ```http
   GET http://localhost:5000/api/rag-sql-chatbot/health
   ```

2. **Query Endpoint**
   ```http
   POST http://localhost:5000/api/rag-sql-chatbot/query
   Content-Type: application/json

   {
     "message": "Show education projects in Zomba",
     "source_lang": "english",
     "page": 1,
     "page_size": 10
   }
   ```

### Database Schema

The chatbot queries the 'proj_dashboard' table with the following key columns:

```sql
CREATE TABLE proj_dashboard (
    PROJECTNAME TEXT,
    FISCALYEAR TEXT,
    REGION TEXT,
    DISTRICT TEXT,
    TOTALBUDGET NUMERIC,
    PROJECTSTATUS TEXT,
    PROJECTSECTOR TEXT,
    CONTRACTORNAME TEXT,
    CONTRACTSTARTDATE TEXT,
    EXPENDITURETODATE NUMERIC,
    SOURCEOFFUNDING TEXT,
    PROJECTCODE TEXT,
    LASTMONITORINGVISIT TEXT
);
```

### Query Processing Flow

1. **User Input Processing**
   - Validate input
   - Extract key information
   - Determine query type (general vs specific)

2. **SQL Generation**
   - Use Together AI LLM to generate SQL
   - Apply query templates based on question type
   - Ensure proper column names and table references

3. **Response Formatting**
   - Format results based on query type
   - General queries: Basic project information
   - Specific queries: Detailed project information
   - Handle null values and data formatting

4. **Error Handling**
   - Invalid queries
   - No results found
   - Database connection issues
   - LLM generation errors

### Example Queries and Responses

1. **General Query**
   ```sql
   -- Show education projects in Zomba
   SELECT * FROM proj_dashboard 
   WHERE DISTRICT = 'Zomba' 
   AND PROJECTSECTOR = 'Education';
   ```

2. **Specific Query**
   ```sql
   -- Details about Chilipa CDSS Girls Hostel
   SELECT * FROM proj_dashboard 
   WHERE PROJECTNAME LIKE '%Chilipa CDSS Girls Hostel%';
   ```

## Testing and Monitoring

### Health Checks
```powershell
curl http://localhost:5000/api/rag-sql-chatbot/health
```

### Performance Monitoring
- Response times
- Query success rates
- LLM generation accuracy
- Database query performance

## Error Handling

1. **User Input Errors**
   - Invalid query format
   - Unsupported query types
   - Missing required parameters

2. **System Errors**
   - Database connection issues
   - LLM service unavailability
   - Invalid SQL generation

3. **Data Quality Issues**
   - Missing or null values
   - Inconsistent data formats
   - Invalid numerical values

## Future Improvements

1. **Query Processing**
   - Enhanced natural language understanding
   - Better handling of complex queries
   - Support for more query types

2. **Response Quality**
   - More detailed error messages
   - Better handling of edge cases
   - Enhanced response formatting

3. **Performance**
   - Query optimization
   - Caching frequently requested data
   - Batch processing for large result sets