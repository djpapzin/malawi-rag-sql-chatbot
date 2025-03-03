# Dziwani - Infrastructure Transparency Chatbot

A specialized chatbot for querying and exploring Malawi's infrastructure projects database. Named "Dziwani" (meaning "what you should know" in Chichewa), this tool provides a natural language interface to access detailed information about infrastructure projects, their status, and related statistics.

## Features

- Natural language querying of infrastructure projects
- Interactive chat interface with guidance tiles for:
  - Finding projects by sector (Infrastructure, Water, Energy, etc.)
  - Finding projects by location (districts)
  - Finding specific project details
- Detailed project information including:
  - Project Name
  - District
  - Project Sector
  - Project Status
  - Budget (in MWK)
  - Completion Percentage
  - Start and Completion Dates
- Real-time chat responses
- Loading states and error handling
- Responsive design for all devices

## Technical Architecture

### Frontend Components

The frontend of Dziwani uses a lightweight, server-side rendered approach:

- **Technology Stack**:
  - HTML with Jinja2 Templates
  - Vanilla JavaScript (no framework)
  - Plain CSS for styling
  - No build process required

- **Key Files**:
  - `frontend/templates/index.html` - Main chat interface
  - `frontend/static/js/main.js` - Core application logic
  - `frontend/static/css/styles.css` - Main styling
  - `frontend/static/css/loading.css` - Loading animations

- **Features**:
  - Responsive design for mobile and desktop
  - Client-side form validation
  - Interactive chat history
  - Expandable query details for technical users
  - Loading indicators and error handling

### Backend Components

The backend is built on FastAPI with LangChain for RAG-based SQL generation:

- **Technology Stack**:
  - FastAPI web framework
  - SQLite database
  - LangChain for RAG-SQL capabilities
  - Python 3.11+
  - Jinja2 for templating

- **Key Components**:
  - `app/main.py` - Entry point and API configuration
  - `app/database/langchain_sql.py` - SQL generation with LangChain
  - `app/models.py` - Data models and database connection
  - `app/routers/` - API endpoint routing
  - `app/llm/` - LLM integration and response handling

- **Features**:
  - Natural language to SQL conversion
  - Response cleaning and formatting
  - Error handling and rate limiting
  - Database query optimization
  - Conversation context management

### Deployment Architecture

- FastAPI serves both the API and static frontend files
- No separate frontend build/deployment needed
- Designed to run on port 5000 with gunicorn workers
- Supports deployment via systemd, supervisor, or nohup

## Quick Start

### Prerequisites

- Python 3.8+
- SQLite3
- Conda (for environment management)

### Installation

```bash
# Create and activate virtual environment
conda create -n rag-sql-env python=3.11
conda activate rag-sql-env

# Install dependencies
pip install -r requirements.txt

# Database Setup
# The application uses malawi_projects1.db which contains data imported from pmisProjects.sql
# If you need to regenerate the database:
python scripts/convert_database.py
```

### Database Structure

The application uses a SQLite database file `malawi_projects1.db` with a single table `proj_dashboard` containing data on Malawi's infrastructure projects. This database is populated with real project data imported from the pmisProjects.sql dump file. Key fields include:

- `PROJECTNAME`: Name of the infrastructure project
- `DISTRICT`: District location (e.g., Lilongwe, Blantyre, etc.)
- `PROJECTSECTOR`: Sector (Education, Health, Roads and bridges, etc.)
- `PROJECTSTATUS`: Current project status
- `BUDGET`: Project budget
- `COMPLETIONPERCENTAGE`: Project completion (0-100)
- `STARTDATE`: Start date
- `COMPLETIONDATA`: Completion date
- `PROJECTDESC`: Detailed description of the project
- `FUNDINGSOURCE`: Source of project funding

The database contains 1048 real infrastructure projects.

## Database
The application uses a SQLite database located at:
`malawi_projects1.db` (in the project root directory)

This database was created from a real SQL dump file containing actual Malawi infrastructure projects data.

For detailed information about the database schema, setup, and usage, see:
- [Database Setup and Configuration](docs/DATABASE_SETUP.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)

## Environment Variables
```ini
TOGETHER_API_KEY=your_api_key
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
├── scripts/              # Setup and utility scripts
│   └── init_db.py       # Database initialization script
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
   - Infrastructure projects
   - Water and sanitation
   - Energy initiatives
   - Education projects
   - Healthcare facilities
   - Agriculture projects
   - Transport infrastructure

2. **Location-based Queries**
   - Projects in specific districts:
     - Lilongwe
     - Blantyre
     - Mzuzu
     - Zomba
     - Kasungu
     - Mangochi
     - Salima
     - Nkhata Bay
     - Karonga
     - Dedza

3. **Status-based Queries**
   - Active projects
   - Planning phase projects
   - Completed projects
   - On Hold projects

## Running the Application

1. Start the Backend:
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000

# Production mode using provided scripts
./start_production.sh  # Starts the application with gunicorn
./restart.sh          # Stops any running instance and restarts the application
```

2. Access the Application:
The application will be available at http://localhost:5000

## Production Deployment

The application is deployed and running at:
- **URL**: https://dziwani.kwantu.support
- **Server IP**: 154.0.164.254
- **Port**: 5000

## Project Structure

```
├── app/                 # FastAPI backend
│   ├── routers/         # API endpoints
│   ├── database/        # Database integration
│   └── main.py          # App entrypoint
├── frontend/            # Frontend static files
│   ├── static/          # CSS and JS files
│   │   ├── css/         # Stylesheets
│   │   └── js/          # JavaScript
│   └── index.html       # Main HTML file
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── malawi_projects1.db  # SQLite database
└── start_production.sh  # Production startup script
```

## Setup and Deployment

For detailed setup and deployment instructions, see:
- [Server Setup](docs/SERVER_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Production Migration Plan](docs/PRODUCTION_MIGRATION_PLAN.md)

## API Usage

The API can be used to query the system programmatically. See [API Usage Guide](docs/API_USAGE.md) for details.

## Troubleshooting

For common issues and solutions, see [Troubleshooting Guide](docs/TROUBLESHOOTING.md).

## Recent Updates

- Fixed frontend integration with proper relative URLs
- Configured Nginx to correctly serve the application on dziwani.kwantu.support
- Added proper SSL certificate for secure HTTPS access
- Created robust startup script for production deployment
- Fixed static file handling in server configuration

## Documentation

Additional documentation can be found in the `docs/` directory:
- [Database Schema](docs/DATABASE_SCHEMA.md)
- API Documentation
- Frontend Integration Guide
- Testing Guidelines

## Server Management

The server is running with the following setup:

- **Runtime Environment**: Conda environment `malawi-rag-sql-chatbot`
- **Web Server**: Gunicorn with Uvicorn workers
- **Port**: 5000
- **Process Management**: Running with `nohup` for persistence
- **Auto-start**: Configured with crontab to start on system reboot

### Current Status

The server is running using `nohup`, which means:

- It will continue running after you log out
- It will not be affected by network disconnections
- It will stop if the server machine reboots (but will restart thanks to crontab)
- It will NOT automatically detect code changes or restart when files are modified

### Checking Server Status

To check if the server is running, use:

```bash
ps -ef | grep gunicorn | grep -v grep
```

### Restarting the Server

After making code changes, you must manually restart the server for changes to take effect:

```bash
# Stop existing server
pkill -f "gunicorn app.main:app"

# Start server again
cd /home/dj/malawi-rag-sql-chatbot
./start_server.sh
```

Alternatively, you can use the provided script:

```bash
./start_server.sh  # This script stops any existing server and starts a new one
```

### Viewing Logs

Server logs are available in:

- `server_access.log` - For access logs
- `server_error.log` - For error logs
- `nohup.out` - For startup and general server output

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Environment Setup

### Local Development (Windows)
```bash
# Create conda environment
conda create -n malawi-chatbot python=3.11
conda activate malawi-chatbot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start backend (port 8000)
python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
NODE_ENV=development npm start
```

### Server Deployment (Linux)
```bash
# Production setup
conda create -n malawi-chatbot python=3.11
conda activate malawi-chatbot

# Install dependencies
pip install -r requirements.txt

# Configure environment
nano .env  # Set PORT=5000, NODE_ENV=production

# Start production server
chmod +x run_production.sh
./run_production.sh
```

## Database Management
The SQLite database should be located at:
`app/database/projects.db`

Initialize with:
```bash
cp malawi_projects1.db app/database/projects.db
```

## Environment Variables
`.env` configuration:
```ini
PORT=5000
NODE_ENV=production
DATABASE_URL=sqlite:///app/database/projects.db
TOGETHER_API_KEY=your-api-key
CORS_ORIGINS='["http://localhost:3000", "https://your-production-domain"]'
```

See full documentation in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## Data Verification Tools

To verify the accuracy of the LLM's responses against the actual database, you can use the provided data verification tools in the `scripts` directory:

### Verify Data Tool

The `verify_data.py` script provides comprehensive database statistics and can be used to check project counts, budgets, and other metrics:

```bash
# Get a database summary
python scripts/verify_data.py

# Check projects in a specific sector
python scripts/verify_data.py sector health

# Check projects in a specific district
python scripts/verify_data.py district lilongwe

# Search for specific projects
python scripts/verify_data.py search "maternity"

# Get details about a specific project
python scripts/verify_data.py project "Construction of a Maternity Block"
```

### Budget Correction Tool

The `fix_llm_budget.py` script helps correct budget magnitude errors in LLM responses:

```bash
# Process a file containing LLM responses
python scripts/fix_llm_budget.py input_file.txt -o corrected_output.txt

# Process text from stdin
python scripts/fix_llm_budget.py

# Or use the executable directly
./scripts/fix_llm_budget.py input_file.txt
```

This tool automatically:
- Corrects known project budgets to their verified values
- Fixes magnitude errors (e.g., when budgets are reported 10x larger than actual)
- Highlights all corrections made to the text

For more details on LLM data verification and known discrepancies, see [LLM Data Verification](docs/LLM_DATA_VERIFICATION.md).

### SQL Query Inspector

The `inspect_sql_queries.py` script allows you to inspect the SQL queries generated by LangChain for natural language queries:

```bash
# Process a natural language query
python scripts/inspect_sql_queries.py ask "How many projects are in the health sector?"

# Run a direct SQL query
python scripts/inspect_sql_queries.py sql "SELECT COUNT(*) FROM proj_dashboard WHERE projectsector = 'Health'"

# Compare actual data with LLM responses
python scripts/inspect_sql_queries.py compare count health
python scripts/inspect_sql_queries.py compare budget education
```

### Known Discrepancies

During verification, the following discrepancies were found between the LLM responses and the actual database:

1. **Health Sector Projects**:
   - Actual count: 219 projects
   - LLM reported count (in some responses): 43 or 54 projects
   - Actual budget: MWK 53,044,625,236.90
   - LLM reported budget (in some responses): ~MWK 13-14 billion

2. **Project Budget Discrepancies**:
   - The LLM reported "Construction of a Maternity Block and 1no. Staff house at Liwera Health Centre" with a budget of MWK 1,950,000,000.00
   - Actual budget in database: MWK 195,000,000.00 (10x smaller)

These discrepancies highlight the importance of verifying LLM responses against the actual database when accurate figures are required.

# Malawi RAG SQL Chatbot

This document provides information about the Malawi RAG SQL Chatbot deployment and maintenance.

## Server Configuration

The server is running with the following setup:

- **Runtime Environment**: Conda environment `malawi-rag-sql-chatbot`
- **Web Server**: Gunicorn with Uvicorn workers
- **Port**: 5000
- **Process Management**: Running with `nohup` for persistence
- **Auto-start**: Configured with crontab to start on system reboot

## Server Management

### Current Status

The server is running using `nohup`, which means:

- It will continue running after you log out
- It will not be affected by network disconnections
- It will stop if the server machine reboots (but will restart thanks to crontab)
- It will NOT automatically detect code changes or restart when files are modified

### Checking Server Status

To check if the server is running, use:

```bash
ps -ef | grep gunicorn | grep -v grep
```

### Restarting the Server

After making code changes, you must manually restart the server for changes to take effect:

```bash
# Stop existing server
pkill -f "gunicorn app.main:app"

# Start server again
cd /home/dj/malawi-rag-sql-chatbot
./start_server.sh
```

Alternatively, you can use the provided script:

```bash
./start_server.sh  # This script stops any existing server and starts a new one
```

### Viewing Logs

Server logs are available in:

- `server_access.log` - For access logs
- `server_error.log` - For error logs
- `nohup.out` - For startup and general server output

## Development Notes

- The server does NOT support hot-reloading
- All code changes require a manual server restart
- The SQL query parsing is sensitive to syntax issues; be careful when modifying `langchain_sql.py`

## Testing the API

You can test if the API is working correctly using:
```bash
curl -X POST http://154.0.164.254:5000/api/chat -H "Content-Type: application/json" -d '{"message":"What health projects are in Machinga?"}'
