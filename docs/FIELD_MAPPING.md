# Malawi Infrastructure Projects Field Mapping

## Database Overview

The project uses a single SQLite database:

1. `malawi_projects1.db` (Main Database)
   - Location: Root directory (`c:\Users\lfana\Documents\Kwantu\rag-sql-chatbot\`)
   - Table: 
     * `proj_dashboard` (198 records)
   - Status: Production database
   - Note: Contains the complete schema with all required fields for infrastructure projects

## Active Database Schema (`malawi_projects1.db`)

### proj_dashboard Table (198 records)
Currently used for all queries. Contains comprehensive project information.

#### Core Fields (General Queries)

| Field ID | Data Type | Example Value | Description |
|----------|-----------|---------------|-------------|
| PROJECTNAME | varchar(100) | "Completion of Staff House" | Project name |
| FISCALYEAR | varchar(100) | "April 2024 / March 2025" | Financial year |
| REGION | varchar(100) | "Central Region" | Geographic region |
| DISTRICT | varchar(100) | "Dowa" | District location |
| TOTALBUDGET | decimal(15,2) | 700000.00 | Total project budget |
| PROJECTSTATUS | varchar(100) | "approved" | Current status |
| PROJECTSECTOR | varchar(100) | "Education" | Sector classification |

#### Extended Fields (Specific Project Queries)

| Field ID | Data Type | Example Value | Description |
|----------|-----------|---------------|-------------|
| CONTRACTORNAME | varchar(100) | "ABC Construction Ltd" | Implementing contractor |
| SIGNINGDATE | date | "2023-07-15" | Contract signing date |
| TOTALEXPENDITURETODATE | decimal(15,2) | 450000.00 | Amount spent |
| FUNDINGSOURCE | varchar(100) | "DDF" | Funding source |
| PROJECTCODE | varchar(100) | "MW-CR-DO" | Project identifier |
| LASTVISIT | date | "2024-01-20" | Last monitoring visit |

#### Additional Useful Fields

| Field ID | Data Type | Example Value | Description |
|----------|-----------|---------------|-------------|
| COMPLETIONPERCENTAGE | decimal(11,2) | 45.50 | Progress percentage |
| PROJECTDESC | varchar(100) | "Teacher house construction..." | Project description |
| TRADITIONALAUTHORITY | varchar(100) | "TA Name" | Traditional authority |
| STAGE | varchar(100) | "Construction" | Project stage |
| STARTDATE | date | "2023-08-01" | Start date |
| COMPLETIONESTIDATE | date | "2024-12-31" | Estimated completion |
| MAP_LATITUDE | float | -13.5201 | Project latitude |
| MAP_LONGITUDE | float | 33.8543 | Project longitude |

#### System Fields

| Field ID | Data Type | Example Value | Description |
|----------|-----------|---------------|-------------|
| G_UUID | varchar(100) | "000ccd30-aefa-4277-cfab-9027353d3a1f" | Unique identifier |
| ISLATEST | tinyint(1) | 1 | Current version flag |
| ISLATEST_PENDING | tinyint(1) | 0 | Pending changes flag |
| ISLATEST_APPROVED | tinyint(1) | 1 | Approval status flag |

## Query Guidelines

### For General Queries
```sql
SELECT 
    PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
    TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR 
FROM proj_dashboard 
WHERE ISLATEST = 1;
```

### For Specific Project Details
```sql
SELECT * FROM proj_dashboard 
WHERE PROJECTCODE = 'MW-CR-DO' 
AND ISLATEST = 1;
```

## Important Notes

1. Database Usage:
   - Single source of truth: `malawi_projects1.db`
   - Single table: `proj_dashboard`
   - Always include `WHERE ISLATEST = 1` in queries

2. Data Formats:
   - Monetary values in Malawi Kwacha (MWK)
   - Dates in YYYY-MM-DD format
   - Geographic hierarchy: Region > District > Traditional Authority

3. Status Tracking:
   - Use ISLATEST flags for version control
   - PROJECTSTATUS for current state
   - COMPLETIONPERCENTAGE for progress

4. Spatial Data:
   - MAP_LATITUDE and MAP_LONGITUDE available for geographic plotting
   - REGION and DISTRICT for administrative boundaries

## Recent Database Changes (2025-02-18)
1. Removed duplicate records (reduced from 396 to 198 unique projects)
2. Removed unused tables (proj_dashboard_v2 and projects)
3. Simplified database structure to single table architecture
