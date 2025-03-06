# Query Test Results: List girls hostel construction projects

## SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        
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
| Dowa Turn Off Market Shed | Database | Central Region | Dowa | Approved | 70000000.0 |
| Dowa Turn Off Market Shed | API | Central Region | Dowa | Approved | MWK 70,000,000.00 |
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | nan |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | nan |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |
| Construction of Malambo police unit | Database | Central Region | Ntchisi | Implementation: On track or Implementation: Delayed | 449177950.0 |
| Construction of Malambo police unit | API | Central Region | Ntchisi | Implementation: On track or Implementation: Delayed | MWK 449,177,950.00 |
| Construction of Three Markets Shed | Database | Southern Region | Phalombe | None | 417685470.0 |
| Construction of Three Markets Shed | API | Southern Region | Phalombe | Not available | MWK 417,685,470.00 |
