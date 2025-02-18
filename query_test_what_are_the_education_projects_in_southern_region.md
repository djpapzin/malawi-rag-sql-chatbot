# Query Test: What are the education projects in Southern Region

## SQL Query
```sql

                SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%southern region%') OR LOWER(DISTRICT) LIKE LOWER('%southern region%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 23
* Database Results: 23
* Match: Yes

## First 5 Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | nan |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | None | nan |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |
| CONSTRUCTION OF  STAFF HOUSE AT ST JOHNS PRIMARY SCHOOL | Database | Southern Region | Blantyre | None | nan |
| CONSTRUCTION OF  STAFF HOUSE AT ST JOHNS PRIMARY SCHOOL | API | Southern Region | Blantyre | None | Not available |
| Chilingani School Block Construction | Database | Southern Region | Blantyre | None | nan |
| Chilingani School Block Construction | API | Southern Region | Blantyre | None | Not available |
