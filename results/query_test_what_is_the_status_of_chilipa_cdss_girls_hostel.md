# Query Test Results: What is the status of 'CHILIPA CDSS GIRLS HOSTEL'

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
            LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL') OR LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL project') OR LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL construction') OR LOWER(PROJECTNAME) LIKE LOWER('CHILIPA CDSS GIRLS HOSTEL%') OR LOWER(PROJECTNAME) LIKE LOWER('% CHILIPA CDSS GIRLS HOSTEL %')
        )
ORDER BY
            CASE 
                WHEN LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL') THEN 1
                WHEN LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL project') THEN 2
                WHEN LOWER(PROJECTNAME) = LOWER('CHILIPA CDSS GIRLS HOSTEL construction') THEN 3
                WHEN LOWER(PROJECTNAME) LIKE LOWER('CHILIPA CDSS GIRLS HOSTEL%') THEN 4
                WHEN LOWER(PROJECTNAME) LIKE LOWER('% CHILIPA CDSS GIRLS HOSTEL %') THEN 5
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
| CHILIPA CDSS GIRLS HOSTEL | Database | Southern Region | Mangochi | None | None |
| CHILIPA CDSS GIRLS HOSTEL | API | Southern Region | Mangochi | Not available | Not available |
