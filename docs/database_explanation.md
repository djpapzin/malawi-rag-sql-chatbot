# Malawi Infrastructure Projects Database Explanation

## Database Purpose
This database tracks infrastructure development projects across Malawi, focusing on:
- Project metadata and locations
- Financial allocations and expenditures
- Construction timelines and completion status
- Contractor relationships
- Community impact metrics

## proj_dashboard Table Structure

| Category                | Key Fields                          | Description                                                                 |
|-------------------------|-------------------------------------|-----------------------------------------------------------------------------|
| **Project Identification** | `PROJECTNAME`, `PROJECTCODE`, `PROJECTID` | Unique identifiers and names for projects (e.g., school construction)      |
| **Location**            | `REGION`, `DISTRICT`, `MAP_LATITUDE` | Geographical data with district/region tracking and GPS coordinates        |
| **Financials**          | `BUDGET`, `TOTALEXPENDITURETODATE`  | Budget allocations vs actual spending with variance calculations           |
| **Timeline**            | `STARTDATE`, `COMPLETIONESTIDATE`   | Planned vs actual completion dates with overdue tracking                   |
| **Completion Status**   | `COMPLETIONPERCENTAGE`, `ISOVERDUE` | Progress metrics and delay indicators                                       |
| **Contractors**         | `CONTRACTORNAME`, `SIGNINGDATE`     | Contractor agreements and contract details                                 |
| **Community Impact**    | `PEOPLEBENEFITED`, `MALES`, `FEMALES` | Demographic breakdown of beneficiaries                                     |
| **Workflow**            | `G_WORKFLOWUUID`, `ISLATEST_APPROVED` | Approval process tracking with version control                             |
| **Flags/Statuses**      | `ANYFLAG`, `PROJECTSTATUS`          | Quality/issue flags and current project state                              |

## Example Project Comparison

| Field                | Completion of Staff House (Dowa)      | Construction of Dwele Bridge (Dowa)     | Ngomano Health Post (Thyolo)         |
|----------------------|----------------------------------------|------------------------------------------|---------------------------------------|
| **Sector**           | Education                              | Roads and bridges                        | Health                                |
| **Type**             | Teacher house construction             | Bridge construction                      | Health center rehabilitation          |
| **Location**         | Central Region > Dowa                 | Central Region > Dowa                    | Southern Region > Thyolo             |
| **Budget**           | Not specified                          | Not specified                            | Not specified                         |
| **Beneficiaries**    | 700,000 (population served)           | 4,600 (population served)                | 20,000 (population served)           |
| **Funding Source**   | DDF (District Development Fund)        | DDF                                      | PBG (Pooled Basket Funding)           |

## Key Observations
1. **Temporal Tracking**: Projects have multiple entries (e.g., 202410/202411) for monthly updates
2. **Approval Workflow**: Uses `ISLATEST_APPROVED` and `G_WORKFLOWUUID` for version control
3. **Geospatial Data**: Contains GPS coordinates (`MAP_LATITUDE`, `MAP_LONGITUDE`) for mapping
4. **Multi-sector Coverage**: Includes education, health, infrastructure, and community services
5. **Performance Metrics**: Tracks both financial (% spend) and physical (% completion) progress

## How Projects Differ
1. **By Phase**: 
   - Planning (`STAGE` field)
   - Active construction 
   - Handover (`ISPROJECTHANDEDOVER`)
   
2. **By Funding**:
   - DDF: Local district funds
   - PBG: National pooled funds
   - External donor funding (not shown in examples but present in schema)

3. **By Complexity**:
   - Simple projects (single structure)
   - Multi-phase projects (e.g., "Boma Stadium Phase 3")
   - System projects (e.g., water pipeline networks) 