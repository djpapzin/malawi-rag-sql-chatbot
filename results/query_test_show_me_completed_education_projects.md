# Query Test Results: Show me completed education projects

## SQL Query
```sql
SELECT PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
                FROM proj_dashboard
                WHERE ISLATEST = 1
             AND LOWER(PROJECTSTATUS) LIKE LOWER('%completed%') AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%') ORDER BY PROJECTNAME ASC
```

## Results Summary
* API Results: 0
* Database Results: 0
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
