# Development Guide

## Project Structure
```
├── app/                 # FastAPI backend
│   ├── routers/         # API endpoints
│   ├── database/        # SQLite database
│   └── main.py          # App entrypoint
├── frontend/            # React frontend
├── scripts/             # Database scripts
├── requirements.txt     # Python dependencies
└── run_production.sh    # Production script
```

## Workflow

### Backend Development
```bash
conda activate malawi-chatbot
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm start
```

### Testing
```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend
npm test
```

## Debugging Tips
1. Check API responses:
```bash
curl http://localhost:8000/health
```

2. Inspect database:
```bash
sqlite3 app/database/projects.db
```

3. Monitor logs:
```bash
tail -f app.log
```
