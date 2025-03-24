# RAG PDF & SQL Chatbot: Technology Stack & API Summary

## Overview
The RAG PDF & SQL Chatbot is a comprehensive web application that uses Retrieval Augmented Generation (RAG) to answer questions based on both PDF documents and SQL databases. It provides a unified interface for users to upload documents, query document content, and ask questions about structured data in databases. The system also includes an NLP Demo component for showcasing natural language processing capabilities.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Database**: 
  - SQLite with SQLAlchemy (SQL Chatbot)
  - FAISS Vector Database (PDF Chatbot)
- **Natural Language Processing**: LangChain framework

### Frontend
- **Languages**: JavaScript, HTML, CSS
- **Framework**: React 18
- **UI Components**: Ant Design
- **HTTP Client**: Axios
- **Build Tool**: Create React App

### Database
- **SQL Chatbot**: SQLite database containing infrastructure project data
- **PDF Chatbot**: FAISS vector store for document embeddings

## External APIs & Services

### LLM (Large Language Model) Services
- **Together AI**: Used for natural language processing
  - **Models**:
    - **PDF Chatbot**: mistralai/Mixtral-8x7B-Instruct-v0.1
    - **SQL Chatbot**: mistralai/Mixtral-8x7B-Instruct-v0.1 (code implementation exists but may be conditionally used)
    - **NLP Demo**: mistralai/Mixtral-8x7B-Instruct-v0.1
  - **Use Cases in Project**:
    - Natural language to SQL conversion (implementation exists but may be conditionally used)
    - PDF document question answering
    - Response generation
    - Context understanding
    - Multi-language support
    - Text analysis and summarization (NLP Demo)

### Translation Services
- **Azure AI Translation**: Used for multi-language support
  - **Supported Languages**: 
    - English
    - Russian
    - Uzbek
    - Chichewa
    - Tumbuka
    - Yao

## Architecture & Data Flow

### PDF Chatbot Flow
1. User uploads PDF documents through the web interface
2. Documents are processed and embedded into FAISS vector store
3. User inputs a natural language query about document content
4. Query is vectorized and used to retrieve relevant document chunks
5. LLM generates a response based on the retrieved context
6. Response is presented to the user through the web interface

### SQL Chatbot Flow
1. User inputs a natural language query about infrastructure projects
2. If LLM is enabled, query may be enhanced using LLM
3. SQL is executed against the SQLite database (currently using predefined queries)
4. Results are formatted into a structured response
5. If LLM is enabled and translation is required, response may be translated using LLM
6. Response is presented to the user through the web interface

### NLP Demo Flow
1. User inputs text for analysis or a specific NLP task
2. Text is sent to the NLP Demo API
3. LLM processes the text based on the requested operation (summarization, sentiment analysis, etc.)
4. Results are formatted and returned to the frontend
5. Response is presented to the user through the web interface

## Components

### RAG PDF Chatbot
- Document upload and processing
- Vector-based document search
- Question answering using RAG
- Multi-language support

### RAG SQL Chatbot
- Database querying with predefined SQL queries
- Structured response formatting
- Optional LLM enhancement for queries (if enabled)
- Optional LLM translation for responses (if enabled)
- Multi-language support

### NLP Demo
- Text summarization
- Sentiment analysis
- Entity extraction
- Topic modeling
- Language detection and translation

## Security & Configuration
- CORS configured for specific origins
- Environment variables used for sensitive configuration
- API keys securely managed
- Production deployment behind Nginx reverse proxy

## Deployment Architecture
- **Development Environment**:
  - Frontend: http://localhost:3000
  - PDF Chatbot API: http://localhost:8000
  - SQL Chatbot API: http://localhost:8001
  - NLP Demo API: http://localhost:8002

- **Server Testing Environment**:
  - Frontend: http://154.0.164.254:3000
  - PDF Chatbot API: http://154.0.164.254:8000
  - SQL Chatbot API: http://154.0.164.254:8001
  - NLP Demo API: http://154.0.164.254:8002

- **Production Environment**:
  - Frontend: https://ai.kwantu.support
  - PDF Chatbot API: https://ai.kwantu.support/api/rag-pdf-chatbot
  - SQL Chatbot API: https://ai.kwantu.support/api/rag-sql-chatbot
  - NLP Demo API: https://ai.kwantu.support/api/nlp-demo

## Process Management
- **Supervisor**: Used for process management in production
- **Systemd**: Service files for automatic startup and monitoring

## Development & Testing
- Testing with pytest and pytest-asyncio
- Development workflow includes Git version control
- Logging configuration for different environments
- Health check endpoints for monitoring service status

---

This document provides a high-level overview of the technology stack and external APIs used in the RAG PDF & SQL Chatbot project. For more detailed implementation information, please refer to the code and documentation in the repository.