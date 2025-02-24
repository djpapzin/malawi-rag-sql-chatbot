# Query Test Results: List all projects in Southern Region

## SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        
AND (LOWER(REGION) LIKE '%southern region%' OR LOWER(DISTRICT) LIKE '%southern region%')
            ORDER BY 
                
            CASE 
                WHEN LOWER(PROJECTSTATUS) = 'ongoing' THEN 1
                WHEN LOWER(PROJECTSTATUS) = 'completed' THEN 2
                WHEN LOWER(PROJECTSTATUS) = 'approved' THEN 3
                ELSE 4
            END
        ,
                TOTALBUDGET DESC,
                COMPLETIONPERCENTAGE DESC
            LIMIT 10
```

## Results Summary
* API Results: 10
* Database Results: 10
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Construction of Three Markets Shed | Database | Southern Region | Phalombe | None | 417685470.0 |
| Construction of Three Markets Shed | API | Southern Region | Phalombe | Not available | MWK 417,685,470.00 |
| Construction of Thetula CDSS Staff House | Database | Southern Region | Mwanza | None | 117568824.0 |
| Construction of Thetula CDSS Staff House | API | Southern Region | Mwanza | Not available | MWK 117,568,824.00 |
| Mthela Bridge | Database | Southern Region | Phalombe | None | 53746008.0 |
| Mthela Bridge | API | Southern Region | Phalombe | Not available | MWK 53,746,008.00 |
| Namatapa School Block | Database | Southern Region | Phalombe | Implementation: On track | 40562552.0 |
| Namatapa School Block | API | Southern Region | Phalombe | Implementation: On track | MWK 40,562,552.00 |
| chikaonga bridge | Database | Southern Region | Phalombe | None | 13666285.0 |
| chikaonga bridge | API | Southern Region | Phalombe | Not available | MWK 13,666,285.00 |
