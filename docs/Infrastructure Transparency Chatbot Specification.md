# Infrastructure Transparency Chatbot Specification

## Introduction

Dwizani (meaning "what you should know" in Chichewa) is an AI-powered chatbot designed to improve transparency in infrastructure projects in Malawi. The system uses a combination of RAG (Retrieval Augmented Generation) and SQL templates to process natural language queries about infrastructure projects.

### Current Capabilities

1. **AI-Powered Query Processing**
   - Natural language understanding
   - Context-aware responses
   - Pattern matching for project names and codes
   - Template-based SQL generation
   - Structured response formatting

2. **User Interface**
   - Modern, responsive chat interface
   - Guidance tiles for common queries
   - Real-time loading states
   - Error handling and recovery
   - Mobile-friendly design

3. **Query Types**
   - Specific Project Queries: Using project names or codes
   - General Project Queries: Based on sector, location, or status
   - Statistical Queries: Basic aggregations and summaries

4. **Data Coverage**
   - Project details (name, code, location)
   - Financial information (budget, expenditure)
   - Implementation status
   - Contractor details
   - Timeline information

## Core Functionality

### Query Types

The chatbot supports three primary modes of operation:

1. **Specific Project Queries**
   - Purpose: Provide detailed information about a single project
   - Identification Methods:
     - Natural language description
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
     - Trend analysis
     - Comparative statistics
     - Distribution metrics

### User Interface

1. **Chat Interface**
   - Clean, modern design using Tailwind CSS
   - Message types:
     - User messages (right-aligned)
     - Bot responses (left-aligned)
     - System messages (centered)
     - Error messages (styled in red)
   - Interactive elements:
     - Message input with send button
     - Loading indicators
     - Error displays
     - Guidance tiles

2. **Guidance System**
   - Project discovery tiles:
     - Find by sector
     - Find by location
     - Find specific project
   - Dynamic hiding on chat initiation
   - Mobile-responsive layout

3. **Error Handling**
   - User-friendly error messages
   - Network error recovery
   - Invalid query handling
   - Timeout management

### Technical Implementation

1. **Frontend Stack**
   - Vanilla JavaScript
   - Tailwind CSS
   - HTML5
   - Fetch API for requests

2. **Backend Stack**
   - FastAPI framework
   - SQLite database
   - RAG-based query processing
   - SQL template engine

3. **API Endpoints**
   - Main query endpoint: `/api/rag-sql-chatbot/query`
   - Health check: `/api/rag-sql-chatbot/health`
   - Response format:
     ```json
     {
       "response": "string",
       "metadata": {
         "query_type": "string",
         "confidence": number,
         "processing_time": number
       },
       "error": string | null
     }
     ```

4. **Performance Considerations**
   - Debounced message sending
   - Optimized database queries
   - Caching where appropriate
   - Efficient error handling

5. **Security Measures**
   - Input sanitization
   - Rate limiting
   - CORS configuration
   - Error message obfuscation

## Development Guidelines

1. **Code Organization**
   - Modular architecture
   - Clear separation of concerns
   - Consistent naming conventions
   - Comprehensive documentation

2. **Testing Strategy**
   - Unit tests for components
   - Integration tests for API
   - End-to-end testing
   - Performance benchmarking

3. **Deployment Process**
   - Environment configuration
   - Build optimization
   - Monitoring setup
   - Backup procedures

4. **Maintenance**
   - Regular updates
   - Performance monitoring
   - Error tracking
   - User feedback integration
