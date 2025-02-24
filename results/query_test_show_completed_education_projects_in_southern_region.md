# Query Test Results: Show completed education projects in Southern Region

## SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%southern region%') OR LOWER(DISTRICT) LIKE LOWER('%southern region%')) AND LOWER(PROJECTSTATUS) LIKE LOWER('%completed%') AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 0
* Database Results: 0
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
