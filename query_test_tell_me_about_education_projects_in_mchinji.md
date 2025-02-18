# Query Test: Tell me about education projects in Mchinji

## SQL Query
```sql

                SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%mchinji%') OR LOWER(DISTRICT) LIKE LOWER('%mchinji%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 3
* Database Results: 3
* Match: Yes

## First 5 Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | None |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | None |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | None |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |
