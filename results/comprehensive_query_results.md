# Comprehensive Query Test Results

## Overview
This report contains the results of various queries testing the infrastructure projects database and API.

## Table of Contents
1. [Specific Project Queries](#specific-project-queries)
2. [General Project Queries](#general-project-queries)

## Specific Project Queries

## General Project Queries

### Query: All Education Projects

### SQL Query
```sql
SELECT PROJECTNAME, REGION, DISTRICT, PROJECTSTATUS, TOTALBUDGET
FROM proj_dashboard 
WHERE ISLATEST = 1 
AND LOWER(PROJECTSECTOR) LIKE LOWER('%education%')
ORDER BY PROJECTNAME ASC
```

### Results Summary
* Database Results: 0
* API Results: 0
* Match: No

### Results Comparison

No results available

