# Dwizani - Infrastructure Transparency Chatbot

A specialized chatbot for querying and exploring Malawi's infrastructure projects database. Named "Dwizani" (meaning "what you should know" in Chichewa), this tool provides a natural language interface to access detailed information about infrastructure projects, their status, and related statistics.

## Features

- Natural language querying of infrastructure projects
- Interactive chat interface with guidance tiles for:
  - Finding projects by sector (health, education, roads)
  - Finding projects by location (districts and regions)
  - Finding specific project details
- Detailed project information including:
  - Project Name
  - Fiscal Year
  - Region
  - District
  - Total Budget
  - Project Status
  - Project Sector
- Real-time chat responses
- Loading states and error handling
- Responsive design for all devices

## Quick Start

### Prerequisites

- Python 3.8+
- SQLite3
- Virtual environment

### Installation

```bash
# Create and activate virtual environment
conda create -n rag-sql-bot python=3.11
conda activate rag-sql-bot

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

1. Start the Backend:
```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Access the Application:
The application will be available at http://localhost:8000

## API Endpoints

- `POST /api/rag-sql-chatbot/query`: Main endpoint for querying infrastructure projects
  - Accepts natural language queries
  - Returns project information and metadata
- `GET /api/rag-sql-chatbot/health`: Health check endpoint
  - Monitors database and API status

## Configuration

Required environment variables in `.env`:

```env
# Server Configuration
PORT=8000
HOST=0.0.0.0
NODE_ENV=development

# API Configuration
API_PREFIX=/api/rag-sql-chatbot
CORS_ORIGINS=["http://localhost:3000"]

# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///malawi_projects1.db
```

## Project Structure

```
├── app/                    # Backend application
│   ├── database/          # Database models and queries
│   ├── core/              # Core business logic
│   └── main.py           # FastAPI application
├── frontend/              # Frontend application
│   ├── static/           # Static assets
│   │   ├── css/         # Stylesheets
│   │   ├── js/          # JavaScript files
│   │   └── img/         # Images and icons
│   └── templates/        # HTML templates
├── docs/                  # Documentation
└── tests/                # Test suite
```

## Features in Detail

### Chat Interface
- Clean, modern UI with Tailwind CSS
- Responsive design that works on all devices
- Interactive message history
- Real-time loading states
- Error handling with user-friendly messages

### Query Types
1. **Sector-based Queries**
   - Health sector projects
   - Education initiatives
   - Road infrastructure

2. **Location-based Queries**
   - District-specific projects
   - Regional development initiatives

3. **Project-specific Queries**
   - Contractor information
   - Budget allocation
   - Project timeline
   - Current status

## Testing

Run the test suite:
```bash
pytest tests/
```

## Documentation

Additional documentation can be found in the `docs/` directory:
- API Documentation
- Frontend Integration Guide
- Testing Guidelines

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
