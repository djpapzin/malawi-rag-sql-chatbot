# Specific Project Query Test Results

## Summary
* **Total Tests:** 30
* **Passed:** 27 (90.0%)
* **Failed:** 3 (10.0%)

## Test Categories
* **Exact Match:** 4/4 (100.0%)
* **Case Sensitivity:** 1/3 (33.3%)
* **Partial Match:** 2/3 (66.7%)
* **Format:** 4/4 (100.0%)
* **Edge Case:** 5/5 (100.0%)
* **SQL Injection:** 2/2 (100.0%)
* **Special Chars:** 3/3 (100.0%)
* **Whitespace:** 3/3 (100.0%)
* **Mixed:** 3/3 (100.0%)

## Test Results

| Category | Test Description | Query | Expected | API Results | DB Results | Status |
|----------|-----------------|--------|-----------|-------------|------------|--------|
| Exact Match | Full Quoted Name | `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |
| Exact Match | With Project Keyword | `Show details for 'CHILIPA CDSS GIRLS HOSTEL project'` | N/A | 0 | 0 | PASS |
| Exact Match | Full Project Code | `Show details for project MW-CR-DO` | N/A | 0 | 0 | PASS |
| Exact Match | Code with Status | `Project code MW-CR-DO status` | N/A | 0 | 0 | PASS |
| Case Sensitivity | All Lowercase | `Tell me about 'chilipa cdss girls hostel'` | N/A | 0 | 0 | PASS |
| Case Sensitivity | Lowercase Code | `Show details for project mw-cr-do` | 1 | 0 | 0 | FAIL |
| Case Sensitivity | Mixed Case | `What is the status of CHILIPA cdss GIRLS hostel` | 1 | 0 | 0 | FAIL |
| Partial Match | Beginning | `Tell me about 'CHILIPA CDSS'` | N/A | 0 | 0 | PASS |
| Partial Match | End | `Show status of 'GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |
| Partial Match | Project Code | `Project MW-CR` | 1 | 0 | 0 | FAIL |
| Format | Progress Query | `What is the progress of 'CHILIPA CDSS GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |
| Format | Budget Query | `Show me the budget for 'CHILIPA CDSS GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |
| Format | Contractor Query | `Who is the contractor for 'CHILIPA CDSS GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |
| Format | Completion Date Query | `When will 'CHILIPA CDSS GIRLS HOSTEL' be completed` | N/A | 0 | 0 | PASS |
| Edge Case | Non-existent Project | `Tell me about 'Non Existent Project'` | N/A | 0 | 0 | PASS |
| Edge Case | Invalid Project Code | `Show details for project XX-YY-ZZ` | 0 | 0 | 0 | PASS |
| Edge Case | Multiple Projects | `Tell me about 'CHILIPA CDSS GIRLS HOSTEL' and 'Another Project'` | N/A | 0 | 0 | PASS |
| Edge Case | Empty Project Name | `Tell me about ''` | 0 | 0 | 0 | PASS |
| Edge Case | Single Character | `Tell me about 'A'` | N/A | 0 | 0 | PASS |
| SQL Injection | DROP TABLE | `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'; DROP TABLE proj_dashboard;--'` | N/A | 0 | 0 | PASS |
| SQL Injection | UNION Attack | `Show details for project MW-CR-DO' UNION SELECT * FROM proj_dashboard--` | N/A | 0 | 0 | PASS |
| Special Chars | Single Quote | `Tell me about 'Project's Name'` | N/A | 0 | 0 | PASS |
| Special Chars | Double Quote | `Show details for 'Project "Name"'` | N/A | 0 | 0 | PASS |
| Special Chars | Semicolon | `Tell me about 'Project;Name'` | N/A | 0 | 0 | PASS |
| Whitespace | Extra Spaces | `Tell me about '   CHILIPA CDSS GIRLS HOSTEL   '` | N/A | 0 | 0 | PASS |
| Whitespace | Multiple Spaces | `Show details for project    MW-CR-DO   ` | N/A | 0 | 0 | PASS |
| Whitespace | Tabs and Newlines | `Tell me about '	CHILIPA CDSS GIRLS HOSTEL
'` | N/A | 0 | 0 | PASS |
| Mixed | Code and District | `Show budget and status for project MW-CR-DO in Lilongwe district` | N/A | 0 | 0 | PASS |
| Mixed | Name and Status | `List all completed projects like 'CHILIPA CDSS'` | N/A | 0 | 0 | PASS |
| Mixed | Sector and Name | `What is the total budget for projects in education sector including 'CHILIPA CDSS GIRLS HOSTEL'` | N/A | 0 | 0 | PASS |

## Detailed Results

### Exact Match: Full Quoted Name
**Query:** `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Exact Match: With Project Keyword
**Query:** `Show details for 'CHILIPA CDSS GIRLS HOSTEL project'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Exact Match: Full Project Code
**Query:** `Show details for project MW-CR-DO`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Exact Match: Code with Status
**Query:** `Project code MW-CR-DO status`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Case Sensitivity: All Lowercase
**Query:** `Tell me about 'chilipa cdss girls hostel'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Case Sensitivity: Lowercase Code
**Query:** `Show details for project mw-cr-do`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Case Sensitivity: Mixed Case
**Query:** `What is the status of CHILIPA cdss GIRLS hostel`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Partial Match: Beginning
**Query:** `Tell me about 'CHILIPA CDSS'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Partial Match: End
**Query:** `Show status of 'GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Partial Match: Project Code
**Query:** `Project MW-CR`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Format: Progress Query
**Query:** `What is the progress of 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Format: Budget Query
**Query:** `Show me the budget for 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Format: Contractor Query
**Query:** `Who is the contractor for 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Format: Completion Date Query
**Query:** `When will 'CHILIPA CDSS GIRLS HOSTEL' be completed`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Edge Case: Non-existent Project
**Query:** `Tell me about 'Non Existent Project'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Edge Case: Invalid Project Code
**Query:** `Show details for project XX-YY-ZZ`

**Results:**
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Edge Case: Multiple Projects
**Query:** `Tell me about 'CHILIPA CDSS GIRLS HOSTEL' and 'Another Project'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Edge Case: Empty Project Name
**Query:** `Tell me about ''`

**Results:**
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Edge Case: Single Character
**Query:** `Tell me about 'A'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### SQL Injection: DROP TABLE
**Query:** `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'; DROP TABLE proj_dashboard;--'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### SQL Injection: UNION Attack
**Query:** `Show details for project MW-CR-DO' UNION SELECT * FROM proj_dashboard--`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Special Chars: Single Quote
**Query:** `Tell me about 'Project's Name'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Special Chars: Double Quote
**Query:** `Show details for 'Project "Name"'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Special Chars: Semicolon
**Query:** `Tell me about 'Project;Name'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Whitespace: Extra Spaces
**Query:** `Tell me about '   CHILIPA CDSS GIRLS HOSTEL   '`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Whitespace: Multiple Spaces
**Query:** `Show details for project    MW-CR-DO   `

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Whitespace: Tabs and Newlines
**Query:** `Tell me about '	CHILIPA CDSS GIRLS HOSTEL
'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Mixed: Code and District
**Query:** `Show budget and status for project MW-CR-DO in Lilongwe district`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Mixed: Name and Status
**Query:** `List all completed projects like 'CHILIPA CDSS'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

### Mixed: Sector and Name
**Query:** `What is the total budget for projects in education sector including 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: N/A
* API Results: 0
* DB Results: 0
* Status: PASS

