# Database Setup and Configuration

## Overview
This document provides definitive information about the database used in the Malawi Infrastructure Projects Chatbot.

## Database Details
- **Database File**: `malawi_projects1.db`
- **Location**: Project root directory (`/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db`)
- **Table**: `proj_dashboard`
- **Record Count**: 196 infrastructure projects

## Database Schema
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

## Important Notes
1. **Date Format**: Both date fields (`startdate` and `completiondata`) are stored as integers in YYYYMMDD format
   - Example: January 1, 2023 is stored as `20230101`
   - SQL queries must transform these values for proper date display

2. **Case Sensitivity**: The `district` field values are case-sensitive
   - SQL queries should use `LOWER()` function for case-insensitive comparisons
   - Example: `WHERE LOWER(district) = LOWER('Lilongwe')`

## Database Creation
To recreate the database from scratch:

```bash
cd /home/dj/malawi-rag-sql-chatbot
python scripts/init_db.py
```

This script will:
1. Create a new `malawi_projects1.db` file
2. Create the `proj_dashboard` table
3. Populate it with 196 sample infrastructure projects

## Database Access in Code
The application accesses the database through the `DatabaseManager` class in `app/models.py`, which looks for the database in the following locations:
1. Path specified in `DATABASE_URL` environment variable
2. Default path: project root directory (`malawi_projects1.db`)

## SQL Query Transformations
When working with this database, queries need two important transformations:

1. **Case-insensitive district comparisons**:
   ```sql
   -- Original query
   WHERE district = 'Lilongwe'
   
   -- Transformed query
   WHERE LOWER(district) = LOWER('Lilongwe')
   ```

2. **Date formatting**:
   ```sql
   -- Original query
   SELECT startdate as start_date
   
   -- Transformed query
   SELECT substr(startdate,1,4) || '-' || substr(startdate,5,2) || '-' || substr(startdate,7,2) as start_date
   ```

## Troubleshooting
If you encounter database-related issues:

1. Verify the database exists at the root directory
2. Check that the `proj_dashboard` table exists and has records
3. Ensure SQL queries handle case sensitivity and date formatting correctly
4. If needed, recreate the database using the `init_db.py` script

## Warning About Other Setup Scripts
Note that there are other database setup scripts in the repository that create different database schemas:
- `scripts/setup_db.py`
- `app/database/setup_db.py`

These scripts are **not** used for the current application and should be ignored or removed to prevent confusion.
