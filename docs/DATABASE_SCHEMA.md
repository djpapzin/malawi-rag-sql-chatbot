# Database Schema and Setup

## Database Setup
To generate the database, run:
```bash
python scripts/init_db.py
```
This script will create `malawi_projects1.db` in the project root directory with 196 sample infrastructure projects, including realistic project names, budgets, completion percentages, and dates.

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
- `startdate`: Project start date in YYYYMMDD format (stored as integer)
- `completiondata`: Project completion date in YYYYMMDD format (stored as integer)

### Important Implementation Notes
1. **Date Format**: Both date fields are stored as integers in YYYYMMDD format
   - Example: January 1, 2023 is stored as `20230101`
   - SQL queries must transform these values for proper display: 
     ```sql
     substr(startdate,1,4) || '-' || substr(startdate,5,2) || '-' || substr(startdate,7,2) as start_date
     ```

2. **Case Sensitivity**: The `district` field values are case-sensitive
   - SQL queries should use `LOWER()` function for case-insensitive comparisons:
     ```sql
     WHERE LOWER(district) = LOWER('Lilongwe')
     ```

### Sample Data Format
```sql
-- Example record:
('Lilongwe Road Development Phase 1', 'Lilongwe', 'Infrastructure', 'Active', 500000, 0, 20230101, 20240101)
```

### Available Values
1. Districts: Lilongwe, Blantyre, Mzuzu, Zomba, Kasungu, Mangochi, Salima, Nkhata Bay, Karonga, Dedza
2. Sectors: Infrastructure, Water, Energy, Education, Healthcare, Agriculture, Transport
3. Statuses: Active, Planning, Completed, On Hold

Note: This is the only table used in the application. The database is automatically populated with 196 sample records when running the `init_db.py` script.

## For More Information
See the comprehensive [Database Setup and Configuration](DATABASE_SETUP.md) document for detailed information about database usage, access patterns, and troubleshooting.
