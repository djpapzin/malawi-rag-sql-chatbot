# Query Test Results: Tell me about 'Boma Stadium Phase 3'

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
            LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3') OR LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3 project') OR LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3 construction') OR LOWER(PROJECTNAME) LIKE LOWER('Boma Stadium Phase 3%') OR LOWER(PROJECTNAME) LIKE LOWER('% Boma Stadium Phase 3 %')
        )
ORDER BY
            CASE 
                WHEN LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3') THEN 1
                WHEN LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3 project') THEN 2
                WHEN LOWER(PROJECTNAME) = LOWER('Boma Stadium Phase 3 construction') THEN 3
                WHEN LOWER(PROJECTNAME) LIKE LOWER('Boma Stadium Phase 3%') THEN 4
                WHEN LOWER(PROJECTNAME) LIKE LOWER('% Boma Stadium Phase 3 %') THEN 5
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
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | None |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
