# Infrastructure Transparency Chatbot

A specialized chatbot for querying and exploring Malawi's infrastructure projects database. This tool provides a natural language interface to access detailed information about infrastructure projects, their status, and related statistics.

## Features

- Natural language querying of infrastructure projects
- Detailed project information including:
  - Project Name
  - Fiscal Year
  - Region
  - District
  - Total Budget
  - Project Status
  - Project Sector
- Multi-language support (English, Russian, Uzbek)
- Suggested follow-up questions
- Project statistics and summaries
- Pagination for large result sets

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js and npm (for frontend)
- SQLite3
- Virtual environment

### Installation

```bash
# Backend Setup
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Frontend Setup
cd frontend
npm install
```

## Running the Application

1. Start the Backend:
```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Start the Frontend:
```bash
# From the frontend directory
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## API Endpoints

- `POST /query`: Main endpoint for querying infrastructure projects
  - Accepts natural language queries
  - Returns project information and metadata
  - Supports pagination and language selection

## Configuration

Required environment variables in `.env`:

```env
# Database Configuration
DATABASE_URL=sqlite:///malawi_projects1.db

# API Configuration
PORT=8000
HOST=0.0.0.0
```

## Project Structure

```
├── app/                    # Backend application
│   ├── database/          # Database models and queries
│   ├── core/              # Core business logic
│   └── main.py           # FastAPI application
├── frontend/              # React frontend application
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Documentation

For more detailed information, see:
- [Infrastructure Transparency Chatbot Specification](docs/Infrastructure%20Transparency%20Chatbot%20Specification.md)
- [Field Mapping Documentation](docs/FIELD_MAPPING.md)
- [Query Response Plan](docs/query_response_plan.md)
