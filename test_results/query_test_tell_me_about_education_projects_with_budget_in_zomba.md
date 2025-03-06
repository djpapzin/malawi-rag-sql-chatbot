# Query Test Results: Tell me about education projects with budget in Zomba

## SQL Query
```sql
SELECT 
                PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
                TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR
            FROM proj_dashboard
            WHERE ISLATEST = 1
        
AND (LOWER(REGION) LIKE '%zomba%' OR LOWER(DISTRICT) LIKE '%zomba%')
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
* API Results: 2
* Database Results: 2
* Counts Match: Yes

## Results Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Mchengawedi TDC | Database | Southern Region | Zomba | None | None |
| Mchengawedi TDC | API | Southern Region | Zomba | Not available | Not available |
| Mwambo Youth Center Phase 2 | Database | Southern Region | Zomba | None | None |
| Mwambo Youth Center Phase 2 | API | Southern Region | Zomba | Not available | Not available |
