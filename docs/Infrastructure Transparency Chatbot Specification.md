# Infrastructure Transparency Chatbot Specification

## Introduction

Dziwani is a rule-based chatbot designed to improve transparency in infrastructure projects in Malawi. The system currently uses pattern matching and SQL templates to process natural language queries about infrastructure projects, with plans to integrate Language Model (LLM) capabilities in future iterations.

### Current Capabilities

1. **Rule-Based Query Processing**
   - Pattern matching for project names and codes
   - Keyword-based query classification
   - Template-based SQL generation
   - Structured response formatting

2. **Query Types**
   - Specific Project Queries: Using project names or codes
   - General Project Queries: Based on sector, location, or status
   - Statistical Queries: Basic aggregations and summaries

3. **Data Coverage**
   - Project details (name, code, location)
   - Financial information (budget, expenditure)
   - Implementation status
   - Contractor details
   - Timeline information

### Future Enhancements

The next phase of development will integrate LLM capabilities to enhance:
- Natural language understanding
- Context-aware responses
- Semantic search capabilities
- Multi-turn conversations
- Dynamic response generation

## Core Functionality

### Query Types

The chatbot supports three primary modes of operation:

1. **Specific Project Queries**
   - Purpose: Provide detailed information about a single project
   - Identification Methods:
     - Exact project name (quoted)
     - Project code (MW-XX-YY format)
     - Fuzzy name matching
     - Case-insensitive matching
   - Core Fields Displayed:
     - Project Name
     - Project Code
     - Location (Region, District)
     - Project Status
     - Total Budget
     - Project Sector
   - Extended Fields:
     - Contractor Details
       - Contractor Name
       - Contract Start Date
       - Contract Signing Date
     - Financial Information
       - Total Budget
       - Expenditure to Date
       - Funding Source
     - Implementation Status
       - Completion Percentage
       - Project Stage
       - Last Monitoring Visit
     - Additional Information
       - Project Description
       - Traditional Authority
       - Start Date
       - Estimated Completion

2. **General Project Queries**
   - Purpose: Provide overview information for multiple projects
   - Query Types:
     - Sector-based (e.g., education, health)
     - Location-based (region, district)
     - Status-based (completed, ongoing)
     - Combined filters
   - Core Fields Displayed:
     - Project Name
     - Location
     - Total Budget
     - Project Status
     - Project Sector
   - Additional Features:
     - Result pagination
     - Sorting options
     - Field filtering
     - Aggregated statistics

3. **Statistical Queries**
   - Purpose: Provide aggregated information and analysis
   - Types:
     - Sector distribution
     - Geographic distribution
     - Budget allocation
     - Implementation status
   - Features:
     - Numerical summaries
     - Percentage calculations
     - Comparative analysis
     - Trend identification

### Response Format

1. **Specific Project Format**
   ```
   Project Name: [Project Name]
   Project Code: [MW-XX-YY]
   Sector: [Sector]
   Region: [Region]
   District: [District]
   Status: [Status]

   Implementation Details:
   - Contractorname: [Name]
   - Startdate: [Date]
   - Completionestidate: [Date]
   - Completionpercentage: [X%]
   - Stage: [Current Stage]

   Financial Information:
   - Totalbudget: MWK [Amount]
   - Totalexpendituretodate: MWK [Amount]
   - Fundingsource: [Source]

   Project Description:
   [Detailed description if available]

   Metadata:
   Results Found: 1
   Query Time: [X.XXX] seconds
   Query Type: [Project Code/Project Name] Search
   ```

2. **General Query Format**
   ```
   Found [X] projects
   Total Budget: MWK [Amount]
   Average Completion: [X%]

   Projects:
   Projectname: [Name]
   Projectcode: [Code]
   Projectsector: [Sector]
   Region: [Region]
   District: [District]
   Projectstatus: [Status]
   Totalbudget: MWK [Amount]
   Completionpercentage: [X%]

   [Additional projects...]

   Metadata:
   Results Found: [X]
   Query Time: [X.XXX] seconds
   Filters Applied:
   - Sector: [If applicable]
   - Region: [If applicable]
   - Status: [If applicable]
   ```

3. **Field Handling**
   - Null values: "Not available"
   - Currency format: "MWK X,XXX.XX"
   - Dates: "Month DD, YYYY"
   - Percentages: "XX.X%"
   - Empty lists: "No projects found matching your criteria."

4. **Response Metadata**
   - Query execution time
   - Total results count
   - Applied filters
   - Query type
   - Data freshness (ISLATEST flag)

5. **Response Types**
   - Single project: Detailed information with all available fields
   - Project list: Summary information with core fields
   - Error responses: Clear error messages with cause
   - Empty results: Informative "no results" message

6. **Field Order**
   - General queries:
     ```python
     general_field_order = [
         'PROJECTNAME',
         'PROJECTCODE',
         'PROJECTSECTOR',
         'REGION',
         'DISTRICT',
         'PROJECTSTATUS',
         'TOTALBUDGET',
         'COMPLETIONPERCENTAGE'
     ]
     ```
   
   - Specific queries:
     ```python
     specific_field_order = [
         # Basic Information
         'PROJECTNAME',
         'PROJECTCODE',
         'PROJECTSECTOR',
         'REGION',
         'DISTRICT',
         'PROJECTSTATUS',
         # Implementation Details
         'CONTRACTORNAME',
         'STARTDATE',
         'COMPLETIONESTIDATE',
         'COMPLETIONPERCENTAGE',
         'STAGE',
         # Financial Information
         'TOTALBUDGET',
         'TOTALEXPENDITURETODATE',
         'FUNDINGSOURCE',
         # Additional Information
         'PROJECTDESC',
         'TRADITIONALAUTHORITY',
         'LASTVISIT'
     ]
     ```

### User Interface

1. **Main Interface**
   - Clean, focused single-page design
   - Language selection (English, Russian, Uzbek)
   - Guidance tiles for:
     - Sector-based search
     - Location-based search
     - Specific project search
     - Project code search
   - Dynamic prompt clearing
   - Optimized canvas layout

2. **Welcome Screen**
   - Title: "Welcome to Dziwani!"
   - Description: Explains meaning in Chichewa
   - Suggested starter questions
   - Language selection options

3. **Response Display**
   - Structured project information
   - Clear field labeling
   - Consistent formatting
   - Proper null value handling
   - Currency formatting
   - Date standardization

## Technical Implementation

### Current Architecture (Rule-Based)

1. **Backend (FastAPI)**
   - Language: Python 3.11+
   - Framework: FastAPI
   - Database: SQLite3
   - Key Components:
     - Query Parser: Rule-based pattern matching
     - Response Generator: Template-based formatting
     - SQL Tracker: Query execution and logging
     - Field Validator: Data consistency checks

2. **Query Processing**
   The system uses a rule-based approach for query processing with the following components:

   1. **Project Name Extraction**
      ```python
      # Quoted project names
      quoted_pattern = r"'([^']+)'"
      
      # Project name phrases
      phrases = [
          r"about\s+(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)",
          r"show\s+(?:me\s+)?(?:the\s+)?(?:details?\s+(?:about|for|of)\s+)?(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)",
          r"what\s+is\s+(?:the\s+)?(?:status|budget|progress)\s+(?:of|for)\s+(.+?)(?:\s+(?:project|construction|building|status|budget|details?|progress|contractor|completion)|$)"
      ]
      ```

   2. **Project Code Detection**
      ```python
      # Project code patterns
      code_patterns = [
          r"(?:project|code)\s+(?:code\s+)?(?:MW-)?([A-Za-z]{2}-[A-Z0-9]{2})",
          r"(?:project|code)\s+([A-Za-z]{2}-[A-Z0-9]{2})",
          r"(?:MW|mw)-([A-Za-z]{2}-[A-Z0-9]{2})",
          r"(?:project|code)\s+([A-Za-z]{2})"
      ]
      ```

   3. **Query Classification**
      - **Specific Project Queries**
        - Exact project name (quoted)
        - Project code (MW-XX-YY format)
        - Case-insensitive matching
        - Fuzzy name matching
      
      - **General Project Queries**
        - Sector-based (education, health, etc.)
        - Location-based (region, district)
        - Status-based (ongoing, completed)
        - Combined criteria

   4. **SQL Generation**
      - **Specific Project Queries**
        ```sql
        SELECT 
            PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
            TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
            CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
            FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
            COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
            STAGE, STARTDATE, COMPLETIONESTIDATE
        FROM proj_dashboard
        WHERE ISLATEST = 1
        AND [project_conditions]
        ORDER BY [relevance_conditions]
        LIMIT 1
        ```
      
      - **General Project Queries**
        ```sql
        SELECT 
            PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
            TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
        FROM proj_dashboard
        WHERE ISLATEST = 1
        AND [filter_conditions]
        ORDER BY 
            CASE 
                WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                ELSE 3
            END,
            TOTALBUDGET DESC,
            COMPLETIONPERCENTAGE DESC
        LIMIT 10
        ```

   5. **Result Prioritization**
      ```python
      # Project name matching priority
      ORDER BY
          CASE 
              WHEN LOWER(PROJECTNAME) = LOWER('[name]') THEN 1
              WHEN LOWER(PROJECTNAME) LIKE LOWER('[name]%') THEN 2
              WHEN LOWER(PROJECTNAME) LIKE LOWER('%[name]%') THEN 3
              ELSE 4
          END,
          CASE 
              WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
              WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
              ELSE 3
          END
      ```

   6. **Field Validation**
      - Required fields for specific queries
      - Optional fields for general queries
      - Null value handling
      - Data type validation
      - Format validation

   7. **Error Handling**
      - Invalid project names/codes
      - Missing required fields
      - Database connection issues
      - Query execution errors
      - Response formatting errors

### Planned LLM Integration

Future implementation will enhance the current rule-based system with LLM capabilities:

1. **Query Understanding**
   - Natural language understanding
   - Intent classification
   - Entity extraction
   - Context awareness
   - Ambiguity resolution

2. **Response Generation**
   - Natural language generation
   - Context-aware responses
   - Dynamic formatting
   - Multi-turn conversation support

3. **Enhanced Features**
   - Semantic search
   - Query reformulation
   - Explanation generation
   - Confidence scoring
   - Follow-up suggestion

### Security Measures

1. **Input Validation**
   - Query sanitization
   - Parameter validation
   - SQL injection prevention
   - Error masking

2. **Rate Limiting**
   - Request throttling
   - Maximum query complexity
   - Response size limits

3. **Monitoring**
   - Query logging
   - Error tracking
   - Performance metrics
   - Resource utilization

## Deployment

1. **Environment**
   - Subdomain: dziwani.kwantu.support
   - Node.js 18+
   - Python 3.11+
   - SQLite3
   - Git

2. **Configuration**
   - Environment variables
   - Database connection
   - API endpoints
   - Rate limits
   - Cache settings

3. **Monitoring**
   - Performance tracking
   - Error logging
   - Usage statistics
   - Resource utilization

## Testing Strategy

1. **Query Testing**
   - Specific project queries
   - General project queries
   - Statistical queries
   - Edge cases
   - Error scenarios

2. **Response Validation**
   - Field availability
   - Format consistency
   - Null handling
   - Currency formatting
   - Date formatting

3. **Performance Testing**
   - Response times
   - Resource usage
   - Concurrent requests
   - Data consistency

4. **Integration Testing**
   - API endpoints
   - Database operations
   - Frontend integration
   - Error handling
