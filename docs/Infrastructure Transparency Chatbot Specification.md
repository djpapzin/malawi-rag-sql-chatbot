# Infrastructure Transparency Chatbot Specification

## Introduction

This document specifies the design and functionality of the Infrastructure Transparency Chatbot, a specialized tool for accessing and querying information about infrastructure projects in Malawi. The chatbot aims to improve transparency and accessibility of infrastructure project data through a natural language interface.

## Core Functionality

### Query Types

The chatbot supports two primary modes of operation:

1. **General Project Queries**
   - Purpose: Provide overview information for multiple projects
   - Core Fields Displayed:
     - Project Name
     - Fiscal Year
     - Region
     - District
     - Total Budget
     - Project Status
     - Project Sector
   - Additional Features:
     - Aggregated statistics
     - Geographic distribution
     - Sector-wise breakdown

2. **Specific Project Queries**
   - Purpose: Provide detailed information about a single project
   - Includes All Core Fields Plus:
     - Contractor Name
     - Contract Start Date
     - Expenditure to Date
     - Source of Funding
     - Project Code
     - Date of Last Council Monitoring Visit

### User Interface

1. **Main Interface**
   - Clean, focused single-page design
   - Language selection (English, Russian, Uzbek)
   - Chat input area
   - Response display area with formatted project information

2. **Welcome Screen**
   - Clear welcome message explaining chatbot capabilities
   - Suggested starter questions
   - Language selection options

3. **Response Display**
   - Structured project information
   - Statistical summaries when relevant
   - Follow-up question suggestions
   - Pagination controls for large result sets

# User interface changes

## URL and name

The chatbot must be presented on a new URL and with a specific name.  The other demos must be removed.

Name - Dziwani (Malawian word that means ‘what you should know’)

## Improve usability

Improve the presentation of the chatbot by providing greater guidance to the user when it first loads (see Gemini example below).

The prompts (and any suggested questions) should be removed once the user has started interacting with the chatbot.

# Tasks to carry out

1. ~~Create a table at the end of this document with the field id’s from the vector database for all the fields.  Provide an example of a value for each field~~   
2. Revise the general query responses as per the table above  
3. Revise the specific query responses as per the table above  
4. Debug why the chatbot is not working  
5. Create sub domain dziwani.kwantu.support  
6. Clone only RAG SQL tab onto that URL (we will leave existing demo un changed)  
7. Change ‘RAG SQL Chatbot’ to ‘Welcome to Dwizani\!’  
8. Change description to be ‘I am Dwizani, a prototype AI chatbot that can answer questions about infrastructure projects.  My name means ‘what you should know’ in Chichewa.  For now I have access to data on projects being constructed in Malawi’  
9. Make header (see line 7\) larger along the lines of example below  
10. Make canvass narrower such that chat area takes up middle of the page  
11. Add following tiles to show the following guidance.  Hide these once the user initiates a chat.

Box one:

**Find projects by sector**

Ask about health, education or roads.

Box two:

**Find project by location**

Ask about a specific district or region in Malawi

Box three:

**Find a specific project**

Ask about a specific project to learn about the contractor and expenditure to date  
![][image1]

# Test cases

The test cases documented [here](https://docs.google.com/spreadsheets/d/1aakw-tTU9ZLIC-nP9eJ7WAC-8SdYFmV8/edit?gid=1388114324#gid=1388114324) should be extended.  These currently cover:

* Initial listing shows with the following info: Name / Location / Total budget  
* Detailed project overview shows with the following info: Name / Location / Budget / Progress  
* Suggested questions give sensible answers  
* Non relevant questions gives no answer  
* Translation works

# Malawi Infrastructure Projects Database Explanation	

## Database Overview

There are three databases in the project:

1. `malawi_projects1.db` (Main Database)  
     
   - Location: Root directory and app directory  
   - Tables:  
     * `proj_dashboard`:  
       1. Total number of fields = 76 (columns)  
       2. Total number of records = 396 (rows)  
          * Total number of records = 198 (rows)

## Active Database Schema (`malawi_projects1.db`)

### proj\_dashboard Table (396 records)

Currently used for active queries. Contains comprehensive project information.

#### Core Fields (General Queries)

| Field ID | Data Type | Example Value | Description |
| :---- | :---- | :---- | :---- |
| PROJECTNAME | varchar(100) | "Completion of Staff House" | Project name |
| FISCALYEAR | varchar(100) | "April 2024 / March 2025" | Financial year |
| REGION | varchar(100) | "Central Region" | Geographic region |
| DISTRICT | varchar(100) | "Dowa" | District location |
| TOTALBUDGET | decimal(15,2) | 700000.00 | Total project budget |
| PROJECTSTATUS | varchar(100) | "approved" | Current status |
| PROJECTSECTOR | varchar(100) | "Education" | Sector classification |

#### Extended Fields (Specific Project Queries)

| Field ID | Data Type | Example Value | Description |
| :---- | :---- | :---- | :---- |
| CONTRACTORNAME | varchar(100) | "ABC Construction Ltd" | Implementing contractor |
| SIGNINGDATE | date | "2023-07-15" | Contract signing date |
| TOTALEXPENDITURETODATE | decimal(15,2) | 450000.00 | Amount spent |
| FUNDINGSOURCE | varchar(100) | "DDF" | Funding source |
| PROJECTCODE | varchar(100) | "MW-CR-DO" | Project identifier |
| LASTVISIT | date | "2024-01-20" | Last monitoring visit |

#### Additional Useful Fields

| Field ID | Data Type | Example Value | Description |
| :---- | :---- | :---- | :---- |
| COMPLETIONPERCENTAGE | decimal(11,2) | 45.50 | Progress percentage |
| PROJECTDESC | varchar(100) | "Teacher house construction..." | Project description |
| TRADITIONALAUTHORITY | varchar(100) | "TA Name" | Traditional authority |
| STAGE | varchar(100) | "Construction" | Project stage |
| STARTDATE | date | "2023-08-01" | Start date |
| COMPLETIONESTIDATE | date | "2024-12-31" | Estimated completion |
| MAP\_LATITUDE | float | -13.5201 | Project latitude |
| MAP\_LONGITUDE | float | 33.8543 | Project longitude |

#### System Fields

| Field ID | Data Type | Example Value | Description |
| :---- | :---- | :---- | :---- |
| G\_UUID | varchar(100) | "000ccd30-aefa-4277-cfab-9027353d3a1f" | Unique identifier |
| ISLATEST | tinyint(1) | 1 | Current version flag |
| ISLATEST\_PENDING | tinyint(1) | 0 | Pending changes flag |
| ISLATEST\_APPROVED | tinyint(1) | 1 | Approval status flag |

### Core Fields to Include (General Query)

- Project Name (`PROJECTNAME`)  
- Fiscal Year (`FISCALYEAR`)  
- Region (`REGION`)  
- District (`DISTRICT`)  
- Total Budget (`TOTALBUDGET`)  
- Project Status (`PROJECTSTATUS`)  
- Project Sector (`PROJECTSECTOR`)

### Response Format Updates  
`1. **List View Response**`  
   ```` ```sql ````  
   `SELECT`  
    `   PROJECTNAME,`  
    `   FISCALYEAR,`  
    `   REGION,`  
    `   DISTRICT,`  
    `   TOTALBUDGET,`  
    `   PROJECTSTATUS,`  
    `   PROJECTSECTOR`  
   `FROM proj_dashboard`  
   `WHERE ISLATEST = 1`  
   ```` ``` ````

### Detailed Fields to Include

Primary Information:

- All core fields (from general queries)  
- Contractor Name (`CONTRACTORNAME`)  
- Signing Date (`SIGNINGDATE`)  
- Total Expenditure (`TOTALEXPENDITURETODATE`)  
- Funding Source (`FUNDINGSOURCE`)  
- Project Code (`PROJECTCODE`)  
- Last Visit (`LASTVISIT`)

## Technical Implementation

### Architecture

1. **Backend (FastAPI)**
   - Language: Python 3.11+
   - Framework: FastAPI
   - Database: SQLite3
   - Key Components:
     - Query Parser: Natural language to SQL conversion
     - Response Generator: Structured response formatting
     - Multi-language Support: Translation handling

2. **Frontend (React)**
   - Framework: React 18+
   - Key Components:
     - Chat Interface: User input and response display
     - Language Selector: Multi-language support
     - Response Formatter: Structured data display

3. **Database**
   - Type: SQLite3
   - Main Table: proj_dashboard
   - Records: 198 unique projects
   - Version Control: ISLATEST flag system

### API Endpoints

1. **/query**
   - Method: POST
   - Purpose: Process natural language queries
   - Parameters:
     ```json
     {
       "query": "string",
       "language": "string",
       "page": "integer",
       "page_size": "integer"
     }
     ```
   - Response:
     ```json
     {
       "response": "string",
       "projects": [],
       "statistics": {},
       "suggestions": [],
       "total_results": "integer",
       "page": "integer"
     }
     ```

### Data Processing

1. **Query Processing**
   - Natural language parsing
   - Intent classification
   - Entity extraction
   - SQL query generation

2. **Response Generation**
   - Data formatting
   - Statistical analysis
   - Translation
   - Follow-up suggestion generation

3. **Error Handling**
   - Invalid queries
   - No results found
   - Database connection issues
   - Translation failures

### Security Measures

1. **Input Validation**
   - Query sanitization
   - Parameter validation
   - SQL injection prevention

2. **Rate Limiting**
   - Request throttling
   - Maximum query complexity
   - Response size limits

3. **Error Logging**
   - Query logging
   - Error tracking
   - Performance monitoring

## Deployment and Maintenance

### Development Environment

1. **Local Setup**
   - Node.js 18+
   - Python 3.11+
   - SQLite3
   - Git

2. **Dependencies**
   - Frontend: package.json
   - Backend: requirements.txt
   - Development: dev-requirements.txt

### Deployment Process

1. **Backend Deployment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Start FastAPI server
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Frontend Deployment**
   ```bash
   # Install dependencies
   npm install
   
   # Build production bundle
   npm run build
   
   # Start production server
   npm start
   ```

### Testing

1. **Unit Tests**
   - Query parser tests
   - Response generator tests
   - Translation tests
   - API endpoint tests

2. **Integration Tests**
   - Frontend-backend communication
   - Database operations
   - Multi-language support
   - Error handling

3. **Performance Tests**
   - Response time monitoring
   - Database query optimization
   - Memory usage tracking
   - Load testing

### Maintenance

1. **Database Updates**
   - Regular data synchronization
   - Schema version control
   - Data quality checks
   - Backup procedures

2. **Monitoring**
   - Error rate tracking
   - Response time monitoring
   - Usage statistics
   - User feedback collection

3. **Documentation**
   - API documentation
   - Database schema
   - Deployment guides
   - User guides

## Future Enhancements

1. **Functionality**
   - Advanced statistical analysis
   - Geographic visualization
   - Document attachment support
   - Real-time data updates

2. **User Experience**
   - Mobile optimization
   - Offline support
   - Voice interface
   - Accessibility improvements

3. **Integration**
   - External data sources
   - Authentication systems
   - Reporting tools
   - Notification systems
