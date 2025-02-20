# Specific Query Implementation Plan

## Overview
This document outlines the implementation plan for handling specific project queries in the Infrastructure Transparency Chatbot. When users request details about a specific project, either by name or code, the system will provide comprehensive project information including contractor details, expenditure, and monitoring data.

## Required Fields
As per the specification, specific project queries will include:

### Core Fields (from general queries)
- Project Name (`PROJECTNAME`)
- Fiscal Year (`FISCALYEAR`)
- Location (`REGION`, `DISTRICT`)
- Total Budget (`TOTALBUDGET`)
- Project Status (`PROJECTSTATUS`)
- Project Sector (`PROJECTSECTOR`)

### Extended Fields (specific to detailed queries)
- Contractor Name (`CONTRACTORNAME`)
- Contract Start Date (`SIGNINGDATE`)
- Expenditure to Date (`TOTALEXPENDITURETODATE`)
- Source of Funding (`FUNDINGSOURCE`)
- Project Code (`PROJECTCODE`)
- Date of Last Council Monitoring Visit (`LASTVISIT`)

## Implementation Components

### 1. Backend Modifications (Python)

#### Query Parser Updates
```python
# In query_parser.py
def parse_query_intent(self, query: str) -> Tuple[str, Dict[str, Any]]:
    # Add project code detection
    project_code = re.search(r'MW-[A-Z]{2}-[A-Z0-9]{2}', query)
    if project_code:
        return f"SELECT * FROM proj_dashboard WHERE PROJECTCODE = '{project_code.group()}'", 
               {"filters": {"project_code": project_code.group()}}
    
    # Add project name matching
    if "details about" in query.lower() or "specific project" in query.lower():
        project_name = re.search(r'"(.*?)"', query)
        if project_name:
            return f"SELECT * FROM proj_dashboard WHERE PROJECTNAME LIKE '%{project_name.group(1)}%'",
                   {"filters": {"project_name": project_name.group(1)}}
```

#### Response Generator Updates
```python
# In response_generator.py
def format_project_details(self, row: pd.Series) -> str:
    return f"""
Project Name: {row['PROJECTNAME']}
Project Code: {row.get('PROJECTCODE', 'N/A')}
Contractor: {row.get('CONTRACTORNAME', 'Not specified')}
Contract Date: {row.get('SIGNINGDATE', 'Not specified')}
Expenditure: MWK {row.get('TOTALEXPENDITURETODATE', 'N/A'):,.2f}
Funding Source: {row.get('FUNDINGSOURCE', 'Not specified')}
Last Inspection: {row.get('LASTVISIT', 'Never')}
"""

def generate_response(self, ...):
    if len(results) == 1:  # Specific project
        return self.format_project_details(results[0])
```

### 2. Frontend Modifications (React)

#### Detailed View Component
```javascript
// In RAGSQLChatbot.js
const renderProjectDetails = (project) => (
  <div className="project-details">
    <Text strong>{project.PROJECTNAME}</Text>
    <div className="detail-row">
      <span className="detail-label">Project Code:</span>
      <span>{project.PROJECTCODE || 'Not available'}</span>
    </div>
    <div className="detail-row">
      <span className="detail-label">Contractor:</span>
      <span>{project.CONTRACTORNAME || 'Not specified'}</span>
    </div>
    {/* Add other detail rows */}
  </div>
);
```

## Implementation Steps

1. **Query Parser Enhancement**
   - Add project code pattern matching
   - Implement project name extraction
   - Add intent detection for specific queries
   - Update SQL query generation

2. **Response Generator Updates**
   - Create detailed response template
   - Add null value handling
   - Implement specific project formatting
   - Update SQL field selection

3. **Frontend Development**
   - Create detailed view component
   - Add styling for detailed view
   - Implement conditional rendering
   - Handle null values in display

4. **Testing and Validation**
   - Test project code queries
   - Test project name queries
   - Verify all fields are displayed
   - Check null value handling

## Testing Plan

### Test Cases
1. **Project Code Queries**
   - Input: "Show details for MW-CR-DO"
   - Expected: Full project details including contractor

2. **Project Name Queries**
   - Input: "Information about 'Nachuma Market Shed phase 3'"
   - Expected: Detailed view if exact match

3. **Null Value Handling**
   - Test projects with missing contractor data
   - Test projects with missing funding data

4. **Mixed Case Queries**
   - Input: "mw-cr-do expenditure details"
   - Expected: Case-insensitive matching

### Success Criteria
- All specified fields are displayed
- Null values show appropriate placeholders
- Project code matching is case-insensitive
- Project name matching handles partial matches
- Response format matches specification

## Next Steps
1. Implement query parser updates
2. Add response generator formatting
3. Create frontend detailed view
4. Run test cases
5. Document any issues or edge cases
