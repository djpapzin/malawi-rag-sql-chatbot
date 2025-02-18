# Infrastructure Projects Database Field Mapping

## Database Overview

The Infrastructure Transparency Chatbot uses a single SQLite database:

- Database: `malawi_projects1.db`
- Location: Project root directory
- Primary Table: `proj_dashboard` (198 unique records)
- Status: Production database
- Note: Single source of truth for all infrastructure project data

## Database Schema

### Core Fields (General Queries)
These fields are displayed for all project queries:

| Field Name | Data Type | Example Value | Description |
|------------|-----------|---------------|-------------|
| PROJECTNAME | varchar(255) | "School Construction" | Project title |
| FISCALYEAR | varchar(10) | "2024-25" | Financial year |
| REGION | varchar(100) | "Central" | Geographic region |
| DISTRICT | varchar(100) | "Lilongwe" | District location |
| TOTALBUDGET | decimal(15,2) | 1500000.00 | Total project budget |
| PROJECTSTATUS | varchar(50) | "In Progress" | Current status |
| PROJECTSECTOR | varchar(100) | "Education" | Project category |

### Extended Fields (Specific Project Queries)
Additional fields displayed for single project queries:

| Field Name | Data Type | Example Value | Description |
|------------|-----------|---------------|-------------|
| CONTRACTORNAME | varchar(255) | "ABC Construction" | Primary contractor |
| CONTRACTSTARTDATE | date | "2024-01-01" | Project start date |
| TOTALEXPENDITURETODATE | decimal(15,2) | 450000.00 | Amount spent |
| FUNDINGSOURCE | varchar(100) | "DDF" | Funding source |
| PROJECTCODE | varchar(100) | "MW-CR-DO" | Project identifier |
| LASTVISIT | date | "2024-01-20" | Last monitoring visit |

### Implementation Notes

1. **Query Filters**
   - All queries include `ISLATEST = 1` to ensure current data
   - Results are ordered by `PROJECTNAME ASC` for consistency

2. **Data Formatting**
   - Budget values: Displayed with MWK currency prefix and thousands separators
   - Dates: Formatted according to locale settings
   - Status: Original case preserved for consistency

3. **Data Validation**
   - Null values are displayed as "N/A"
   - Empty strings are treated as null
   - Zero budgets are displayed as "MWK 0.00"

4. **Query Performance**
   - Primary key: PROJECTCODE
   - Index on ISLATEST for efficient filtering
   - Index on PROJECTNAME for sorting

## Usage Examples

1. **General Query**
   ```sql
   SELECT 
       PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
   FROM proj_dashboard 
   WHERE ISLATEST = 1
   ORDER BY PROJECTNAME ASC;
   ```

2. **Specific Project Query**
   ```sql
   SELECT 
       PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
       CONTRACTORNAME, CONTRACTSTARTDATE, TOTALEXPENDITURETODATE,
       FUNDINGSOURCE, PROJECTCODE, LASTVISIT
   FROM proj_dashboard 
   WHERE PROJECTCODE = ? AND ISLATEST = 1;
   ```
