# Query Test Results: Tell me about education projects in Mchinji

## SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        
AND (LOWER(REGION) LIKE '%mchinji%' OR LOWER(DISTRICT) LIKE '%mchinji%')
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
* API Results: 3
* Database Results: 3
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | None |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Chakhalila Primary school project | Database | Central Region | Mchinji | Approved | None |
| Chakhalila Primary school project | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | None | None |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | Not available | Not available |
