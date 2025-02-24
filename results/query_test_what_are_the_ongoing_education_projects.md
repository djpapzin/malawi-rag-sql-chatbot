# Query Test Results: What are the ongoing education projects

## SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 59
* Database Results: 59
* Counts Match: Yes

## Results Comparison

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
