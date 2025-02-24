# Query Test Results: Show progress of 'Chilingani School Block Construction'

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
            LOWER(PROJECTNAME) = LOWER('Chilingani School Block') OR LOWER(PROJECTNAME) = LOWER('Chilingani School Block project') OR LOWER(PROJECTNAME) = LOWER('Chilingani School Block construction') OR LOWER(PROJECTNAME) LIKE LOWER('Chilingani School Block%') OR LOWER(PROJECTNAME) LIKE LOWER('% Chilingani School Block %')
        )
ORDER BY
            CASE 
                WHEN LOWER(PROJECTNAME) = LOWER('Chilingani School Block') THEN 1
                WHEN LOWER(PROJECTNAME) = LOWER('Chilingani School Block project') THEN 2
                WHEN LOWER(PROJECTNAME) = LOWER('Chilingani School Block construction') THEN 3
                WHEN LOWER(PROJECTNAME) LIKE LOWER('Chilingani School Block%') THEN 4
                WHEN LOWER(PROJECTNAME) LIKE LOWER('% Chilingani School Block %') THEN 5
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
| Chilingani School Block Construction | Database | Southern Region | Blantyre | None | None |
| Chilingani School Block Construction | API | Southern Region | Blantyre | Not available | Not available |
