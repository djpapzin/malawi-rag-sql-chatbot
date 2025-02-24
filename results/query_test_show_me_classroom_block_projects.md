# Query Test Results: Show me classroom block projects

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
            
AND (
            LOWER(PROJECTNAME) = LOWER('classroom block') OR LOWER(PROJECTNAME) = LOWER('classroom block project') OR LOWER(PROJECTNAME) = LOWER('classroom block construction') OR LOWER(PROJECTNAME) LIKE LOWER('classroom block%') OR LOWER(PROJECTNAME) LIKE LOWER('% classroom block %')
        )
ORDER BY
            CASE 
                WHEN LOWER(PROJECTNAME) = LOWER('classroom block') THEN 1
                WHEN LOWER(PROJECTNAME) = LOWER('classroom block project') THEN 2
                WHEN LOWER(PROJECTNAME) = LOWER('classroom block construction') THEN 3
                WHEN LOWER(PROJECTNAME) LIKE LOWER('classroom block%') THEN 4
                WHEN LOWER(PROJECTNAME) LIKE LOWER('% classroom block %') THEN 5
                ELSE 6
            END,
            CASE 
                WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                ELSE 3
            END
LIMIT 1
```

## Results Summary
* API Results: 1
* Database Results: 1
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Construction of Classroom block at Katete Junior primary school in T/A Malili | Database | Central Region | Lilongwe | None | None |
| Construction of Classroom block at Katete Junior primary school in T/A Malili | API | Central Region | Lilongwe | Not available | Not available |
