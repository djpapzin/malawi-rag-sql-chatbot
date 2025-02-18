# Query Test: Tell me about school construction projects

## SQL Query
```sql

                SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 100
* Database Results: 198
* Match: No

## First 5 Results Comparison

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
