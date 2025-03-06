# Query Test Results: Show education projects in Zomba district

## SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND (LOWER(REGION) LIKE LOWER('%zomba district%') OR LOWER(DISTRICT) LIKE LOWER('%zomba district%')) AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 0
* Database Results: 0
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
