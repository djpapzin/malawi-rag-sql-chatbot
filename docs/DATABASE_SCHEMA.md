# Database Schema and Setup

## Database Setup
To generate the database, run:
```bash
python scripts/init_db.py
```
This script will create `malawi_projects1.db` with 196 sample infrastructure projects, including realistic project names, budgets, completion percentages, and dates.

## Main Table Schema
```sql
CREATE TABLE proj_dashboard (
    projectname TEXT,
    district TEXT,
    projectsector TEXT,
    projectstatus TEXT,
    budget NUMERIC,
    completionpercentage NUMERIC,
    startdate NUMERIC,
    completiondata NUMERIC
);
```

### Column Descriptions
- `projectname`: Name of the infrastructure project
- `district`: District where the project is located (e.g., Lilongwe, Blantyre, Mzuzu, etc.)
- `projectsector`: Sector of the project (e.g., Infrastructure, Water, Energy, etc.)
- `projectstatus`: Current status of the project (Active, Planning, Completed, On Hold)
- `budget`: Project budget in MWK (Malawian Kwacha)
- `completionpercentage`: Project completion percentage (0-100)
- `startdate`: Project start date in YYYYMMDD format
- `completiondata`: Project completion date in YYYYMMDD format

### Sample Data Format
```sql
-- Example record:
('Lilongwe Road Development Phase 1', 'Lilongwe', 'Infrastructure', 'Active', 500000, 0, 20230101, 20240101)
```

### Available Values
1. Districts: Lilongwe, Blantyre, Mzuzu, Zomba, Kasungu, Mangochi, Salima, Nkhata Bay, Karonga, Dedza
2. Sectors: Infrastructure, Water, Energy, Education, Healthcare, Agriculture, Transport
3. Statuses: Active, Planning, Completed, On Hold

Note: This is the only table used in the application. The database is automatically populated with 196 sample records when running the setup script.
