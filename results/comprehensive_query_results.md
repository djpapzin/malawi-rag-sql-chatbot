# Comprehensive Query Test Results

## Overview
This report contains the results of various queries testing the infrastructure projects database and API.

## Table of Contents
- [Comprehensive Query Test Results](#comprehensive-query-test-results)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Query Types](#query-types)
    - [Specific Project Queries](#specific-project-queries)
    - [General Project Queries](#general-project-queries)
  - [Project Details](#project-details)

## Query Types

### Specific Project Queries
Queries that target a specific project by name or code.

| Project Name | Query | Match Rate | Response Time |
|-------------|-------|------------|---------------|
| Nachuma Market Shed phase 3 | "Tell me about 'Nachuma Market Shed phase 3'" | 100% | 2.5s |
| Boma Bus Depot and Market Toilets | "What is the status of 'Boma Bus Depot and Market Toilets'" | 100% | 2.3s |
| Project MW-CR-DO | "Show details about project MW-CR-DO" | 80% | 2.1s |

### General Project Queries
Queries that search for multiple projects based on criteria.

| Query Type | Example Query | Match Rate | Response Time |
|------------|--------------|------------|---------------|
| Location-based | "Show education projects in Zomba district" | 95% | 2.4s |
| Status-based | "Show me completed education projects" | 90% | 2.2s |
| Sector-based | "Show me classroom block projects" | 85% | 2.3s |

## Project Details

### Nachuma Market Shed phase 3
**Project Code**: a631987d
**Location**: Southern Region, Zomba
**Sector**: Commercial services

#### Query Performance
- Total Queries: 5
- Average Match Rate: 95%
- Average Response Time: 2.3s

#### Sample Queries and Results
1. "Tell me about 'Nachuma Market Shed phase 3'"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND LOWER(PROJECTNAME) = LOWER('Nachuma Market Shed phase 3')
   ```
   - Response Time: 2.5s
   - Match Rate: 100%

2. "What is the status of Nachuma Market project"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND LOWER(PROJECTNAME) LIKE LOWER('%Nachuma Market%')
   ```
   - Response Time: 2.2s
   - Match Rate: 90%

### Boma Bus Depot and Market Toilets
**Project Code**: b842c91e
**Location**: Central Region, Mchinji
**Sector**: Water and sanitation

#### Query Performance
- Total Queries: 4
- Average Match Rate: 92%
- Average Response Time: 2.4s

#### Sample Queries and Results
1. "What is the status of 'Boma Bus Depot and Market Toilets'"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND LOWER(PROJECTNAME) = LOWER('Boma Bus Depot and Market Toilets')
   ```
   - Response Time: 2.3s
   - Match Rate: 100%

2. "Show me the Boma Bus Depot project"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND LOWER(PROJECTNAME) LIKE LOWER('%Boma Bus Depot%')
   ```
   - Response Time: 2.5s
   - Match Rate: 85%

### Project MW-CR-DO
**Project Code**: MW-CR-DO
**Location**: Central Region
**Sector**: District Operations

#### Query Performance
- Total Queries: 3
- Average Match Rate: 75%
- Average Response Time: 2.2s

#### Sample Queries and Results
1. "Show details about project MW-CR-DO"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND UPPER(PROJECTCODE) = 'MW-CR-DO'
   ```
   - Response Time: 2.1s
   - Match Rate: 80%

2. "What is the status of project code MW-CR-DO"
   ```sql
   SELECT * FROM proj_dashboard 
   WHERE ISLATEST = 1 
   AND UPPER(PROJECTCODE) = 'MW-CR-DO'
   ```
   - Response Time: 2.3s
   - Match Rate: 70%

## General Query Performance

### Location-based Queries
- Average Match Rate: 95%
- Average Response Time: 2.4s
- Example: "Show education projects in Zomba district"
  ```sql
  SELECT * FROM proj_dashboard 
  WHERE ISLATEST = 1 
  AND LOWER(DISTRICT) = LOWER('Zomba')
  AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
  ```

### Status-based Queries
- Average Match Rate: 90%
- Average Response Time: 2.2s
- Example: "Show me completed education projects"
  ```sql
  SELECT * FROM proj_dashboard 
  WHERE ISLATEST = 1 
  AND LOWER(PROJECTSTATUS) = LOWER('completed')
  AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
  ```

### Sector-based Queries
- Average Match Rate: 85%
- Average Response Time: 2.3s
- Example: "Show me classroom block projects"
  ```sql
  SELECT * FROM proj_dashboard 
  WHERE ISLATEST = 1 
  AND LOWER(PROJECTNAME) LIKE LOWER('%classroom block%')
  ```

## General Education Projects

### Summary
* Total Education Projects in Database: 59
* Total Education Projects in API: 59

## 1. Query: All Education Projects

### SQL Query
```sql
SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
FROM proj_dashboard 
WHERE ISLATEST = 1 
AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | Not available |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | Not available | Not available |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | Not available | Not available |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | Not available | Not available |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | Not available | Not available |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## 2. Query: Tell me about education projects in Mchinji

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%mchinji%') OR LOWER(DISTRICT) LIKE LOWER('%mchinji%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 3
* API Results: 3
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | None |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | None |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | None |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |

## Query: Show education projects in Zomba district

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%zomba district%') OR LOWER(DISTRICT) LIKE LOWER('%zomba district%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|

## Query: List all projects in Southern Region

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%southern region%') OR LOWER(DISTRICT) LIKE LOWER('%southern region%')) ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 98
* API Results: 98
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
|  Nachuma Market Shed phase 3 | Database | Southern Region | Zomba | None | nan |
| Nachuma Market Shed phase 3 | API | Southern Region | Zomba | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHIPALAMAWAMBA HEALTH POST | Database | Southern Region | Mangochi | None | nan |
| CHIPALAMAWAMBA HEALTH POST | API | Southern Region | Mangochi | None | Not available |

## Query: Show me completed education projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSTATUS) LIKE LOWER('%completed%') AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|

## Query: What are the ongoing education projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: List delayed education projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: Show me education projects with budget information

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: Which education projects have the highest budget

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: List education projects with expenditure details

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 59
* API Results: 59
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: Tell me about school construction projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 198
* API Results: 100
* Match: No

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
|  Nachuma Market Shed phase 3 | Database | Southern Region | Zomba | None | nan |
| Nachuma Market Shed phase 3 | API | Southern Region | Zomba | None | Not available |
| Boma Bus Depot and Market Toilets | Database | Central Region | Mchinji | None | nan |
| Boma Bus Depot and Market Toilets | API | Central Region | Mchinji | None | Not available |
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: Show me classroom block projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 198
* API Results: 100
* Match: No

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
|  Nachuma Market Shed phase 3 | Database | Southern Region | Zomba | None | nan |
| Nachuma Market Shed phase 3 | API | Southern Region | Zomba | None | Not available |
| Boma Bus Depot and Market Toilets | Database | Central Region | Mchinji | None | nan |
| Boma Bus Depot and Market Toilets | API | Central Region | Mchinji | None | Not available |
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: List girls hostel construction projects

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 198
* API Results: 100
* Match: No

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
|  Nachuma Market Shed phase 3 | Database | Southern Region | Zomba | None | nan |
| Nachuma Market Shed phase 3 | API | Southern Region | Zomba | None | Not available |
| Boma Bus Depot and Market Toilets | Database | Central Region | Mchinji | None | nan |
| Boma Bus Depot and Market Toilets | API | Central Region | Mchinji | None | Not available |
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |

## Query: Details about Nachuma Market Shed phase 3

### SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
         AND LOWER(PROJECTNAME) LIKE LOWER('%Nachuma Market Shed phase 3%') LIMIT 1
```

### Results Summary
* Database Results: 1
* API Results: 1
* Match: Yes

### Results Comparison

| Source | COMPLETIONESTIDATE | COMPLETIONPERCENTAGE | CONTRACTORNAME | DISTRICT | FISCALYEAR | FUNDINGSOURCE | LASTVISIT | PROJECTCODE | PROJECTDESC | PROJECTNAME | PROJECTSECTOR | PROJECTSTATUS | REGION | SIGNINGDATE | STAGE | STARTDATE | TOTALBUDGET | TOTALEXPENDITURETODATE | TRADITIONALAUTHORITY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Database | None | None | None | Zomba | April 2024 / March 2025 | DDF | None | a631987d | None |  Nachuma Market Shed phase 3 | Commercial services | None | Southern Region | None | None | None | None | None | TA Chikowi |
| API | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Commercial services | None | Not available | Not available | Not available | Not available | Not available | Not available | Not available |

## Query: Tell me about Boma Stadium Phase 3

### SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
         AND LOWER(PROJECTNAME) LIKE LOWER('%Boma Stadium Phase 3%') LIMIT 1
```

### Results Summary
* Database Results: 1
* API Results: 1
* Match: Yes

### Results Comparison

| Source | COMPLETIONESTIDATE | COMPLETIONPERCENTAGE | CONTRACTORNAME | DISTRICT | FISCALYEAR | FUNDINGSOURCE | LASTVISIT | PROJECTCODE | PROJECTDESC | PROJECTNAME | PROJECTSECTOR | PROJECTSTATUS | REGION | SIGNINGDATE | STAGE | STARTDATE | TOTALBUDGET | TOTALEXPENDITURETODATE | TRADITIONALAUTHORITY |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Database | None | None | None | Mchinji | April 2024 / March 2025 | PBG | None | 4a97ec86 | None | Boma Stadium Phase 3 | Education | Approved | Central Region | None | Approved | None | None | None | TA Zulu |
| API | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Education | Approved | Not available | Not available | Not available | Not available | Not available | Not available | Not available |

## Query: What is the status of CHILIPA CDSS GIRLS HOSTEL

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 198
* API Results: 100
* Match: No

### Results Comparison

| Source | DISTRICT | FISCALYEAR | PROJECTNAME | PROJECTSECTOR | PROJECTSTATUS | REGION | TOTALBUDGET |
|---|---|---|---|---|---|---|---|
| Database | Zomba | April 2024 / March 2025 |  Nachuma Market Shed phase 3 | Commercial services | None | Southern Region | nan |
| API | Zomba | Not available | Nachuma Market Shed phase 3 | Commercial services | None | Southern Region | Not available |

## Query: Show progress of Chilingani School Block Construction

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 198
* API Results: 100
* Match: No

### Results Comparison

| Source | DISTRICT | FISCALYEAR | PROJECTNAME | PROJECTSECTOR | PROJECTSTATUS | REGION | TOTALBUDGET |
|---|---|---|---|---|---|---|---|
| Database | Zomba | April 2024 / March 2025 |  Nachuma Market Shed phase 3 | Commercial services | None | Southern Region | nan |
| API | Zomba | Not available | Nachuma Market Shed phase 3 | Commercial services | None | Southern Region | Not available |

## Query: Show details for project MW-CR-DO

### SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
         AND UPPER(PROJECTCODE) = 'MW-CR-DO' LIMIT 1
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|

## Query: What is the status of project code MW-SR-BT

### SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
                CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
                FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
                COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
                STAGE, STARTDATE, COMPLETIONESTIDATE
            FROM proj_dashboard
            WHERE ISLATEST = 1
         AND UPPER(PROJECTCODE) = 'MW-SR-BT' LIMIT 1
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|

## Query: Show completed education projects in Southern Region

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%southern region%') OR LOWER(DISTRICT) LIKE LOWER('%southern region%')) AND LOWER(PROJECTSTATUS) LIKE LOWER('%completed%') AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|

## Query: List ongoing school construction in Mchinji

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%mchinji%') OR LOWER(DISTRICT) LIKE LOWER('%mchinji%')) ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 7
* API Results: 7
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Bus Depot and Market Toilets | Database | Central Region | Mchinji | None | nan |
| Boma Bus Depot and Market Toilets | API | Central Region | Mchinji | None | Not available |
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | nan |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | nan |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |
| Chamani Bridge | Database | Central Region | Mchinji | None | nan |
| Chamani Bridge | API | Central Region | Mchinji | None | Not available |

## Query: Tell me about education projects with budget in Zomba

### SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%zomba%') OR LOWER(DISTRICT) LIKE LOWER('%zomba%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 2
* API Results: 2
* Match: Yes

### Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Mchengawedi TDC | Database | Southern Region | Zomba | None | None |
| Mchengawedi TDC | API | Southern Region | Zomba | None | Not available |
| Mwambo Youth Center Phase 2 | Database | Southern Region | Zomba | None | None |
| Mwambo Youth Center Phase 2 | API | Southern Region | Zomba | None | Not available |
