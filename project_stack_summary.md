# Malawi RAG SQL Chatbot: Technology Stack & API Summary

## Overview
The Malawi RAG SQL Chatbot is a web application that uses natural language processing to answer questions about infrastructure projects in Malawi. It converts natural language queries into SQL, retrieves data from a database, and presents the information in a user-friendly format.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy
- **Natural Language Processing**: LangChain framework

### Frontend
- **Languages**: HTML, CSS, JavaScript
- **Framework**: Vanilla JavaScript (no major framework)
- **Styling**: Custom CSS

### Database
- **Type**: SQLite
- **Tables**: Main table `proj_dashboard` containing Malawi infrastructure project data
- **Access Pattern**: SQL queries generated from natural language input

## External APIs & Services

### LLM (Large Language Model) Services
- **Together AI**: Used for natural language processing
  - Model: meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K
  - Purposes:
    - Query classification
    - Natural language to SQL conversion
    - Response generation

### Translation Services
- **Azure Cognitive Services Translation API**:
  - Endpoint: https://api.cognitive.microsofttranslator.com/
  - Used for translating user queries and responses between English and other languages

### Monitoring & Tracing
- **LangSmith**: Used for LLM observability and tracing
  - Endpoint: https://api.smith.langchain.com
  - Purposes:
    - Monitoring LLM performance
    - Tracing query execution paths

## Architecture & Data Flow

1. User inputs a natural language query about Malawi infrastructure projects
2. LLM classifies the query (specific project query vs. general query)
3. Query is translated to SQL using LLM
4. SQL is executed against the SQLite database
5. Results are formatted into a structured response
6. Response is presented to the user through the web interface

## Security & Configuration
- CORS configured for specific origins
- SSL/TLS encryption implemented
- Environment variables used for sensitive configuration

## Development & Testing
- Testing with pytest and pytest-asyncio
- Development workflow includes Git version control
- Logging configuration for different environments

---

This document provides a high-level overview of the technology stack and external APIs used in the Malawi RAG SQL Chatbot project. For more detailed implementation information, please refer to the code and documentation in the repository. 