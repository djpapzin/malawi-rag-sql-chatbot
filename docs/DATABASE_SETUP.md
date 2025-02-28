# Database Setup and Configuration

## Overview
This document provides definitive information about the database used in the Malawi Infrastructure Projects Chatbot.

## Database Details
- **Database File**: `malawi_projects1.db`
- **Location**: Project root directory (`/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db`)
- **Table**: `proj_dashboard`
- **Record Count**: 1048 infrastructure projects

## Database Origin
The database has been created from a real SQL dump file (`pmisProjects.sql`) containing actual Malawi infrastructure projects data. The original SQL dump was imported into an SQLite database for use with the chatbot application.

## Data Migration
If you need to recreate the database from the SQL dump:

```bash
cd /home/dj/malawi-rag-sql-chatbot
sqlite3 malawi_projects1.db < pmisProjects.sql
```

## Database Schema
The database contains a comprehensive schema with many fields. Here are the most important columns:

```sql
CREATE TABLE `proj_dashboard` (
        /* System and metadata fields */
        `G_UUID` varchar (300),
        /* ... many other metadata fields ... */
        
        /* Core project information */
        `PROJECTNAME` varchar (300),
        `PROJECTCODE` varchar (300),
        `PROJECTSTATUS` varchar (300),
        `PROJECTDESC` varchar (300),
        `PROJECTRATIONALE` varchar (300),
        `PROJECTSECTOR` varchar (300),
        `PROJECTTYPE` varchar (300),
        
        /* Location information */
        `REGION` varchar (300),
        `DISTRICT` varchar (300),
        `DISTRICTCODE` varchar (300),
        `TRADITIONALAUTHORITY` varchar (300),
        `MAP_LATITUDE` REAL,
        `MAP_LONGITUDE` REAL,
        
        /* Financial information */
        `BUDGET` Decimal (17),
        `FUNDINGSOURCE` varchar (300),
        `TOTALVALUE` Decimal (17),
        `BUDGETTOTAL` Decimal (17),
        `TOTALEXPENDITUREYEAR` Decimal (17),
        `BUDGETREMAINING` Decimal (17),
        
        /* Progress information */
        `COMPLETIONPERCENTAGE` Decimal (13),
        `STARTDATE` TEXT,
        `COMPLETIONDATA` TEXT,
        `COMPLETIONESTIDATE` TEXT,
        `ACTUALCOMPLETIONDATE` TEXT,
        
        /* Contractor information */
        `CONTRACTORNAME` varchar (300),
        `SIGNINGDATE` TEXT,
        
        /* Additional fields - see full schema in DATABASE_SCHEMA.md */
);
```

## Key Fields for Queries
The most commonly queried fields include:

1. **Project Information**:
   - `PROJECTNAME`: The name of the project
   - `PROJECTDESC`: Detailed description of the project
   - `PROJECTSECTOR`: Sector categorization (e.g., Education, Health)
   - `PROJECTSTATUS`: Current project status

2. **Location Information**:
   - `DISTRICT`: The district where the project is located
   - `REGION`: The region of Malawi

3. **Financial Information**:
   - `BUDGET`: The allocated budget
   - `TOTALVALUE`: The total value of the project

4. **Progress Information**:
   - `COMPLETIONPERCENTAGE`: The percentage of project completion
   - `STARTDATE`: When the project started
   - `COMPLETIONDATA`: Expected completion date

## Important Implementation Notes

### Date Fields
Unlike the test database, date fields in this database are stored as TEXT:
- `STARTDATE`
- `COMPLETIONDATA`
- `SIGNINGDATE`
- `COMPLETIONESTIDATE`
- `ACTUALCOMPLETIONDATE`

### Case Sensitivity
The field names in this database are in ALL CAPS, and when querying them, you should maintain this capitalization:

```sql
SELECT PROJECTNAME, DISTRICT, BUDGET FROM proj_dashboard WHERE PROJECTSECTOR = 'Education'
```

However, the values within fields may still require case-insensitive comparisons:

```sql
SELECT PROJECTNAME, BUDGET FROM proj_dashboard WHERE LOWER(DISTRICT) = LOWER('Lilongwe')
```

## Database Access in Code
The application accesses the database through the DatabaseManager class which looks for the database at:
- Path specified in DATABASE_URL environment variable, or
- Default path: project root directory (`malawi_projects1.db`)

## Common Query Patterns

### Projects by District
```sql
SELECT PROJECTNAME, PROJECTSECTOR, BUDGET, COMPLETIONPERCENTAGE
FROM proj_dashboard
WHERE LOWER(DISTRICT) = LOWER('Lilongwe')
ORDER BY BUDGET DESC
```

### Projects by Sector
```sql
SELECT PROJECTNAME, DISTRICT, BUDGET, COMPLETIONPERCENTAGE
FROM proj_dashboard
WHERE LOWER(PROJECTSECTOR) = LOWER('Education')
ORDER BY COMPLETIONPERCENTAGE DESC
```

### Project Budget Analysis
```sql
SELECT PROJECTSECTOR, 
       COUNT(*) as project_count, 
       SUM(BUDGET) as total_budget, 
       AVG(BUDGET) as average_budget
FROM proj_dashboard
GROUP BY PROJECTSECTOR
ORDER BY total_budget DESC
```

## Troubleshooting
If you encounter database-related issues:

1. Verify the database exists at the expected path
2. Check that the `proj_dashboard` table exists and has records
3. Ensure SQL queries use the correct field names (in ALL CAPS)
4. If needed, recreate the database from the SQL dump file

## Warning About Other Setup Scripts
Note that there are other database setup scripts in the repository that create different database schemas:
- `scripts/setup_db.py`
- `app/database/setup_db.py`

These scripts are **not** used for the current application and should be ignored or removed to prevent confusion.
