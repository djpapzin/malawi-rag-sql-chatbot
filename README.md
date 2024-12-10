# RAG SQL Chatbot Demo

Repository: https://github.com/djpapzin/RAG-SQL-Chatbot

A chatbot that uses Retrieval Augmented Generation (RAG) to provide natural language interface for querying SQL databases. Currently configured for Malawi infrastructure projects database.

## Features

- Natural language to SQL query conversion
- Context-aware responses about infrastructure projects
- Multi-language support (English, Chichewa)
- Suggested follow-up questions

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL
- Virtual environment

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup database
python app/database/setup_db.py
```

## Configuration

Required environment variables in `.env`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=malawi_projects
DB_USER=your_username
DB_PASSWORD=your_password

# Model Configuration
MODEL_PATH=models/your_model
```

## Database Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE malawi_projects;

# Import schema and data
psql -U postgres malawi_projects < malawi_reporting.sql
```

## Running the Server

```bash
# Start the server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Testing

1. **Unit Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_chatbot.py
```

2. **API Testing**
```bash
# Test database connection
curl http://localhost:8001/test/db

# Test query parser
curl http://localhost:8001/test/parser/show%20all%20projects

# Test chat endpoint
curl -X POST http://localhost:8001/api/rag-sql-chatbot/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all projects in Lilongwe"}'
```

3. **Swagger Documentation**
- Visit `http://localhost:8001/docs` for interactive API documentation

## Project Structure

```
.
├── app/
│   ├── main.py           # FastAPI application
│   ├── models/           # Data models
│   ├── database/         # Database utilities
│   └── services/         # Business logic
├── tests/                # Test files
└── docs/                 # Documentation
```

## Common Issues

### 1. Database Connection Issues
```bash
# Check PostgreSQL is running
# Windows
net start postgresql
# Linux
sudo systemctl status postgresql

# Test connection
python check_db.py
```

### 2. Query Parser Issues
```bash
# Test parser directly
python -m pytest test_components.py -k "test_parser"
```

### 3. Model Loading Issues
```bash
# Verify model files exist
python -c "from app.models import get_model; model = get_model()"
```

## API Documentation

See [RAG SQL Chatbot API Documentation](../rag-pdf-chatbot/docs/rag_sql_chatbot_api.md) for detailed endpoint information.

## Need Help?

1. Check the logs:
```bash
tail -f app.log
```

2. Test components:
```bash
python test_components.py
```

3. Contact support: support@kwantu.net
