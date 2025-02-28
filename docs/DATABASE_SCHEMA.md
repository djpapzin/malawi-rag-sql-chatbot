# Database Schema and Setup

## Database Setup
The application uses a real Malawi infrastructure projects database imported from an SQL dump file. 

The database file is located at:
```
/home/dj/malawi-rag-sql-chatbot/malawi_projects1.db
```

This database contains 1048 actual infrastructure projects from Malawi.

## Main Table Schema
```sql
CREATE TABLE `proj_dashboard` (
        `G_UUID` varchar (300),
        `G_VALIDDATE` TEXT,
        `G_SEQ` int (11),
        `isLatest` tinyint (1),
        `isLatest_pending` tinyint (1),
        `isLatest_approved` tinyint (1),
        `G_CONTEXT` varchar (300),
        `G_COMMUNITYID` varchar (300),
        `G_APPID` varchar (300),
        `G_PROFILEUUID` varchar (300),
        `G_WORKFLOWUUID` varchar (300),
        `MAP_BOUNDARY` varchar (300),
        `MAP_LATITUDE` REAL,
        `MAP_LONGITUDE` REAL,
        `PROJECTNAME` varchar (300),
        `PROJECTCODE` varchar (300),
        `PROJECTSTATUS` varchar (300),
        `PROJECTDESC` varchar (300),
        `PROJECTRATIONALE` varchar (300),
        `PROJECTSECTOR` varchar (300),
        `PROJECTTYPE` varchar (300),
        `FISCALYEAR` varchar (300),
        `REGION` varchar (300),
        `DISTRICT` varchar (300),
        `DISTRICTCODE` varchar (300),
        `TRADITIONALAUTHORITY` varchar (300),
        `FUNDINGSOURCE` varchar (300),
        `STAGE` varchar (300),
        `PROJECTID` varchar (300),
        `BUDGET` Decimal (17),
        `PROJECTCOMPLETEBINARY` int (11),
        `ISPROJECTCOMPLETE` varchar (300),
        `PROJECTSTALLEDBINARY` int (11),
        `ISPROJECTSTALLED` varchar (300),
        `PROJECTHANDEDBINARY` int (11),
        `ISPROJECTHANDEDOVER` varchar (300),
        `CONTRACTORNAME` varchar (300),
        `SIGNINGDATE` TEXT,
        `TOTALVALUE` Decimal (17),
        `CERTIFICATES` int (11),
        `ADDENDUMCOUNT` int (11),
        `DURATIONS` int (11),
        `BUDGETTOTAL` Decimal (17),
        `TOTALEXPENDITUREYEAR` Decimal (17),
        `BUDGETREMAINING` Decimal (17),
        `CONTEXPENVARIANCE` Decimal (17),
        `CONTEXPENVARIANCEPERCENT` Decimal (13),
        `TECCONVARIANCE` Decimal (17),
        `TECCONVARIANCEPERCENT` Decimal (13),
        `PERCENTSPEND` Decimal (13),
        `CERTIFICATESPAID` int (11),
        `PERCENTCERTIFICATES` Decimal (13),
        `COMPLETIONPERCENTAGE` Decimal (13),
        `MALES` int (11),
        `FEMALES` int (11),
        `TOTALMEMBERS` int (11),
        `TOTALISSUES` int (11),
        `STARTDATE` TEXT,
        `LASTVISIT` TEXT,
        `COMPLETIONDATA` TEXT,
        `ADDENDUM` varchar (300),
        `COMPLETIONESTIDATE` TEXT,
        `ACTUALCOMPLETIONDATE` TEXT,
        `FLAGONE` int (11),
        `FLAGTWO` int (11),
        `FLAGTHREE` int (11),
        `ANYFLAG` int (11),
        `ALLFLAGS` int (11),
        `ISOVERDUE` varchar (300),
        `DAYSOVERDUE` int (11),
        `COMPLETIONSTATUS` varchar (300),
        `PEOPLEBENEFITED` varchar (300),
        `SITEREPORTCOMMENTS` varchar (3000),
        `CONTRACTORUUID` varchar (300),
        `SITEREPORTUUID` varchar (300),
        `COMPLETIONSTATUSUUID` varchar (300),
        `CYCLE` varchar (300),
        `CYCLECODE` varchar (300)
);
```

### Key Column Descriptions
- `PROJECTNAME`: Name of the infrastructure project
- `DISTRICT`: District where the project is located
- `PROJECTSECTOR`: Sector of the project (e.g., Education, Health, etc.)
- `PROJECTSTATUS`: Current status of the project
- `BUDGET`: Project budget
- `COMPLETIONPERCENTAGE`: Project completion percentage
- `STARTDATE`: Project start date
- `COMPLETIONDATA`: Project completion date
- `PROJECTDESC`: Detailed description of the project
- `PROJECTRATIONALE`: Rationale or justification for the project
- `REGION`: Region where the project is located
- `FUNDINGSOURCE`: Source of project funding
- `CONTRACTORNAME`: Name of the contractor
- `TOTALVALUE`: Total contract value
- `MAP_LATITUDE` and `MAP_LONGITUDE`: Geographic coordinates of the project

### Important Implementation Notes
1. **Date Formats**: Date fields are stored as TEXT
   - When querying, you may need to format them for proper display

2. **Case Sensitivity**: Field values may be case-sensitive
   - SQL queries should use `LOWER()` function for case-insensitive comparisons:
     ```sql
     WHERE LOWER(DISTRICT) = LOWER('Lilongwe')
     ```

### Primary Sectors
Based on the data analysis, the primary project sectors include:
- Agriculture and environment
- Commercial services
- Community security initiatives
- Education
- Health
- Roads and bridges
- Water and sanitation

### Database Statistics
- Total number of records: 1048
- Top districts by project count:
  - Lilongwe: 89 projects
  - Dedza: 57 projects
  - Mulanje: 56 projects
  - Mangochi: 56 projects
  - Mzimba: 55 projects

## For More Information
See the comprehensive [Database Setup and Configuration](DATABASE_SETUP.md) document for detailed information about database usage, access patterns, and troubleshooting.
