# Query Test Results: What is the status of project code MW-SR-BT

## SQL Query
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

## Results Summary
* API Results: 0
* Database Results: 0
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
