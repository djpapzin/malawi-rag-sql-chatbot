# Education Projects Comparison

## Summary
* Database Projects: 59
* API Projects: 59
* Match: Yes

## SQL Queries

### Database Query
```sql
SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
FROM proj_dashboard 
WHERE ISLATEST = 1 
AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
ORDER BY PROJECTNAME ASC
```

## First 5 Projects Comparison

| Project Name | Source | Region | District | Status | Budget |
|--------------|---------|---------|-----------|---------|----------|
| Boma Stadium Phase 3 | Database | Central Region | Mchinji | Approved | Not available |
| Boma Stadium Phase 3 | API | Central Region | Mchinji | Approved | Not available |
| Bua Girls Hostel (finishing) | Database | Central Region | Mchinji | Not available | Not available |
| Bua Girls Hostel (finishing) | API | Central Region | Mchinji | None | Not available |
| CHILAWE CLASSROOM BLOCK | Database | Southern Region | Mangochi | Not available | Not available |
| CHILAWE CLASSROOM BLOCK | API | Southern Region | Mangochi | None | Not available |
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | Not available | Not available |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | None | Not available |
| CHIMWALIRE SCHOOL BLOCK | Database | Southern Region | Mangochi | Not available | Not available |
| CHIMWALIRE SCHOOL BLOCK | API | Southern Region | Mangochi | None | Not available |
