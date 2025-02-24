# Dwizani - Infrastructure Transparency Chatbot

A specialized chatbot for querying and exploring Malawi's infrastructure projects database. Named "Dwizani" (meaning "what you should know" in Chichewa), this tool provides a natural language interface to access detailed information about infrastructure projects, their status, and related statistics.

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

# Generate the database
python scripts/init_db.py
```

### Database Structure

The application uses a single table `proj_dashboard` with the following structure:
- `projectname`: Name of the infrastructure project
- `district`: District location (e.g., Lilongwe, Blantyre, etc.)
- `projectsector`: Sector (Infrastructure, Water, Energy, etc.)
- `projectstatus`: Status (Active, Planning, Completed, On Hold)
- `budget`: Project budget in MWK
- `completionpercentage`: Project completion (0-100)
- `startdate`: Start date (YYYYMMDD format)
- `completiondata`: Completion date (YYYYMMDD format)

The database is automatically populated with 196 sample records when running `init_db.py`.

## Running the Application

1. Start the Backend:
```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

2. Access the Application:
The application will be available at http://localhost:5000

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Query Endpoint
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    message = "List education projects"
    source_lang = "english"
    page = 1
    page_size = 5
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/query" -Method Post -Headers $headers -Body $body
```

### Response Format
```json
{
  "response": {
    "results": [
      {
        "project_name": "Zomba School Construction Phase 1",
        "district": "Zomba",
        "project_sector": "Education",
        "project_status": "Active",
        "total_budget": {
          "amount": 500000,
          "formatted": "MWK 500,000.00"
        },
        "completion_percentage": 45
      }
    ],
    "metadata": {
      "total_results": 1,
      "query_time": "2.5s",
      "sql_query": "SELECT * FROM proj_dashboard WHERE LOWER(projectsector) = 'education'"
    }
  }
}
```

## Environment Variables
Create a `.env` file with:
```
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

## Testing

Run the test suite:
```bash
pytest tests/
```

For testing specific queries:
```bash
python tests/test_tile_queries.py
```

## Documentation

Additional documentation can be found in the `docs/` directory:
- [Database Schema](docs/DATABASE_SCHEMA.md)
- API Documentation
- Frontend Integration Guide
- Testing Guidelines

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
