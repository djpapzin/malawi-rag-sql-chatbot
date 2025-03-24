# Frontend Requirements: Specific Project Query Display

## Overview
When a user queries about a specific project (e.g., "Tell me about the Nyandule Classroom Block project"), the backend returns a detailed response containing 12 standardized fields. Currently, not all fields are being displayed in the frontend. This document outlines what fields should be displayed and their specifications.

## Backend Response Structure
The API returns data in this format:
```json
{
  "results": [
    {
      "type": "specific",
      "message": "Project Details",
      "data": {
        "Name of project": "Nyandule Classroom Block",
        "Fiscal year": "April 2022 / March 2023",
        "Location": "Lilongwe",
        "Budget": "MWK 49,500,000.00",
        "Status": "Implementation: On track",
        "Contractor name": "BuildCo Ltd",
        "Contract start date": "April 15, 2022",
        "Expenditure to date": "MWK 25,000,000.00",
        "Sector": "Education",
        "Source of funding": "World Bank",
        "Project code": "MW-ED-01",
        "Date of last Council monitoring visit": "January 10, 2024"
      }
    }
  ],
  "metadata": {
    "query_time": "2024-03-10T11:27:45.123456",
    "total_results": 1,
    "sql_query": "...",
    "confidence": 0.9
  }
}
```

## Field Specifications

### Required Fields
All 12 fields must be displayed for specific project queries:

1. **Name of project**
   - Type: Text
   - Primary identifier of the project
   - Example: "Nyandule Classroom Block"

2. **Fiscal year**
   - Type: Text (Date range)
   - Format: "Month Year / Month Year"
   - Example: "April 2022 / March 2023"

3. **Location**
   - Type: Text
   - District name in Malawi
   - Example: "Lilongwe"

4. **Budget**
   - Type: Currency
   - Format: "MWK XX,XXX,XXX.XX"
   - Example: "MWK 49,500,000.00"

5. **Status**
   - Type: Text
   - Shows project implementation status
   - Example: "Implementation: On track"
   - Visual Requirement: Status should be easily distinguishable
     - Positive statuses (e.g., "On track")
     - Warning statuses (e.g., "Delayed")
     - Critical statuses (e.g., "Stalled")

6. **Contractor name**
   - Type: Text
   - Name of the implementing contractor
   - Example: "BuildCo Ltd"

7. **Contract start date**
   - Type: Date
   - Format: "MMMM DD, YYYY"
   - Example: "April 15, 2022"

8. **Expenditure to date**
   - Type: Currency
   - Format: "MWK XX,XXX,XXX.XX"
   - Example: "MWK 25,000,000.00"

9. **Sector**
   - Type: Text
   - Project sector category
   - Example: "Education"

10. **Source of funding**
    - Type: Text
    - Funding organization/source
    - Example: "World Bank"

11. **Project code**
    - Type: Text
    - Unique project identifier
    - Example: "MW-ED-01"

12. **Date of last Council monitoring visit**
    - Type: Date
    - Format: "MMMM DD, YYYY"
    - Example: "January 10, 2024"

## Display Requirements

1. **Field Presence**
   - All 12 fields must be displayed
   - Use "Not available" for null or empty values
   - No fields should be hidden or omitted

2. **Data Formatting**
   - Dates should be consistently formatted
   - Currency values should include the "MWK" prefix and proper thousand separators
   - Status should be visually distinct based on project state

3. **User Experience**
   - Information should be easily scannable
   - Layout should be responsive for different screen sizes
   - Project name should be prominently displayed
   - Related information should be visually grouped

4. **Accessibility**
   - Text should be readable and properly contrasted
   - Currency and date formats should be consistent
   - Status indicators should not rely solely on color

## Quality Assurance Checklist
- [ ] All 12 fields are visible
- [ ] Currency values show proper formatting
- [ ] Dates are consistently formatted
- [ ] Empty values show "Not available"
- [ ] Status is visually distinct
- [ ] Layout works on mobile devices
- [ ] All text is clearly readable
