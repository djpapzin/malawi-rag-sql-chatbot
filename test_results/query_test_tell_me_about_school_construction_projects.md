# Query Test Results: Tell me about school construction projects

## SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        
AND LOWER(PROJECTSECTOR) = 'education'
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
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | nan |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |
| Construction of Thetula CDSS Staff House | Database | Southern Region | Mwanza | None | 117568824.0 |
| Construction of Thetula CDSS Staff House | API | Southern Region | Mwanza | Not available | MWK 117,568,824.00 |
| Kapoche Teacher House | Database | Central Region | Dedza | Implementation: On track | 100339930.0 |
| Kapoche Teacher House | API | Central Region | Dedza | Implementation: On track | MWK 100,339,930.00 |
| CONSTRUCTION OF CHIRAMBO PRIMARY SCHOOL CLASSROOM BLOCK | Database | Northern Region | Rumphi | None | 99833510.0 |
| CONSTRUCTION OF CHIRAMBO PRIMARY SCHOOL CLASSROOM BLOCK | API | Northern Region | Rumphi | Not available | MWK 99,833,510.00 |
