# Query Test Results: List ongoing school construction in Mchinji

## SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%mchinji%') OR LOWER(DISTRICT) LIKE LOWER('%mchinji%')) ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 7
* Database Results: 7
* Counts Match: Yes

## Results Comparison

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
