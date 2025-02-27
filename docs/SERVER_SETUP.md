# Server Setup Guide

## Port Configuration

The application uses different ports for development and production:

- **Production Server (154.0.164.254)**:
  - Port: 5000
  - Host: 0.0.0.0 (all interfaces)
  - Access via: http://154.0.164.254:5000
  - Production domain: https://dziwani.kwantu.support

- **Local Development**:
  - Port: 5001
  - Host: localhost
  - Access via: http://localhost:5001
  - Includes hot-reload for development

## Production Server

The production server is running at:
http://154.0.164.254:5000

## Server Configuration

### Environment Setup

1. Install required system packages:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip sqlite3
```

2. Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd malawi-rag-sql-chatbot
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

1. Ensure SQLite is installed:
```bash
sqlite3 --version
```

2. Initialize the database:
```bash
python scripts/convert_database.py
```

This will create:
- SQLite database: `pmisProjects.db`
- CSV export: `pmisProjects.csv`
- Schema documentation: `DATABASE_SCHEMA.md`

### Running the Server

The server is configured to run on `0.0.0.0:5000` to allow external access.

1. Start the server:
```bash
python -m uvicorn app.main:app --port 5000 --host 0.0.0.0
```

2. Verify the server is running:
```bash
curl http://154.0.164.254:5000/health
```

### Monitoring

1. Check server logs:
```bash
tail -f logs/server.log
```

2. Monitor server status:
```bash
ps aux | grep python
```

### Health Checks

The server includes a health check endpoint:
```bash
curl http://154.0.164.254:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_service": "available"
}
```

## Starting the Server

### Production Server
```bash
# On the server (154.0.164.254)
./run_production.sh
# Or directly:
python -m uvicorn app.main:app --port 5000 --host 0.0.0.0
```

### Local Development
```bash
# On your local machine
./run_development.sh
# Or directly:
python -m uvicorn app.main:app --port 5001 --reload
```

## Important Notes

1. Production (Server):
   - Uses port 5000
   - Binds to all interfaces (0.0.0.0)
   - Accessible via server IP
   - No auto-reload for stability

2. Development (Local):
   - Uses port 5001
   - Binds to localhost only
   - Includes auto-reload
   - Won't conflict with server

3. This setup allows:
   - Independent development on local machine
   - Continuous server operation
   - No port conflicts
   - Clear separation of environments
