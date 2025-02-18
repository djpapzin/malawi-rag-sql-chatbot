# Query Response Revision Plan

## Overview
This plan outlines the steps to revise both general and specific query responses based on the field mapping from `malawi_projects1.db`.

## 1. General Query Responses

### Core Fields to Include
- Project Name (`PROJECTNAME`)
- Fiscal Year (`FISCALYEAR`)
- Region (`REGION`)
- District (`DISTRICT`)
- Total Budget (`TOTALBUDGET`)
- Project Status (`PROJECTSTATUS`)
- Project Sector (`PROJECTSECTOR`)

### Response Format Updates
1. **List View Response**
   ```sql
   SELECT 
       PROJECTNAME,
       FISCALYEAR,
       REGION,
       DISTRICT,
       TOTALBUDGET,
       PROJECTSTATUS,
       PROJECTSECTOR
   FROM proj_dashboard 
   WHERE ISLATEST = 1
   ```

2. **Summary Statistics Response**
   - Total projects per region
   - Projects by sector
   - Budget allocation by sector
   - Status distribution

## 2. Specific Query Responses

### Detailed Fields to Include
Primary Information:
- All core fields (from general queries)
- Contractor Name (`CONTRACTORNAME`)
- Signing Date (`SIGNINGDATE`)
- Total Expenditure (`TOTALEXPENDITURETODATE`)
- Funding Source (`FUNDINGSOURCE`)
- Project Code (`PROJECTCODE`)
- Last Visit (`LASTVISIT`)

Additional Details:
- Completion Percentage (`COMPLETIONPERCENTAGE`)
- Project Description (`PROJECTDESC`)
- Traditional Authority (`TRADITIONALAUTHORITY`)
- Stage (`STAGE`)
- Start Date (`STARTDATE`)
- Completion Estimate (`COMPLETIONESTIDATE`)
- Location (`MAP_LATITUDE`, `MAP_LONGITUDE`)

### Response Format Updates
1. **Single Project Detail Response**
   ```sql
   SELECT 
       -- Core Fields
       PROJECTNAME, FISCALYEAR, REGION, DISTRICT,
       TOTALBUDGET, PROJECTSTATUS, PROJECTSECTOR,
       -- Extended Fields
       CONTRACTORNAME, SIGNINGDATE, TOTALEXPENDITURETODATE,
       FUNDINGSOURCE, PROJECTCODE, LASTVISIT,
       -- Additional Details
       COMPLETIONPERCENTAGE, PROJECTDESC, TRADITIONALAUTHORITY,
       STAGE, STARTDATE, COMPLETIONESTIDATE,
       MAP_LATITUDE, MAP_LONGITUDE
   FROM proj_dashboard 
   WHERE PROJECTCODE = ? AND ISLATEST = 1
   ```

2. **Project Progress Response**
   - Implementation timeline
   - Budget utilization
   - Completion status
   - Recent updates

## 3. Implementation Steps

1. **Update Query Templates**
   - Revise SQL query templates in `query_builder.py`
   - Update response formatters
   - Add new field mappings

2. **Update Response Formatting**
   - Format monetary values (MWK)
   - Format dates (YYYY-MM-DD)
   - Add geographic hierarchy

3. **Add Data Validation**
   - Check for ISLATEST flag
   - Validate required fields
   - Handle null values

4. **Testing**
   - Test general queries
   - Test specific queries
   - Verify field mappings
   - Check response formats

## 4. Files to Update

1. `app/database/query_builder.py`
   - Update query templates
   - Add new field mappings

2. `app/models.py`
   - Update response models
   - Add new field types

3. `app/sql_tracker.py`
   - Update query tracking
   - Add new field logging

## 5. Quality Checks

- Verify all fields are properly mapped
- Ensure consistent date formats
- Validate monetary value formatting
- Check geographic data accuracy
- Test multi-language support

## Timeline

1. Query Template Updates (Day 1)
2. Response Format Updates (Day 1)
3. Testing and Validation (Day 2)
4. Documentation Updates (Day 2)

## Success Criteria

1. All queries return correct field mappings
2. Responses are properly formatted
3. All data types are handled correctly
4. Geographic hierarchy is maintained
5. Tests pass successfully
