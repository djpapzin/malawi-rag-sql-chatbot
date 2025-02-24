# Specific Project Query Test Results

## Summary
* **Total Tests:** 19
* **Passed:** 9 (47.4%)
* **Failed:** 10 (52.6%)

## Test Categories
* **Exact Match:** 3/4 (75.0%)
* **Case Sensitivity:** 0/3 (0.0%)
* **Partial Match:** 2/3 (66.7%)
* **Format:** 0/4 (0.0%)
* **Edge Case:** 4/5 (80.0%)

## Test Results

| Category | Test Description | Query | Expected | API Results | DB Results | Status |
|----------|-----------------|--------|-----------|-------------|------------|--------|
| Exact Match | Full Quoted Name | `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'` | 1 | 0 | 0 | FAIL |
| Exact Match | With Project Keyword | `Show details for 'CHILIPA CDSS GIRLS HOSTEL project'` | 0 | 0 | 0 | PASS |
| Exact Match | Full Project Code | `Show details for project MW-CR-DO` | 0 | 0 | 0 | PASS |
| Exact Match | Code with Status | `Project code MW-CR-DO status` | 0 | 0 | 0 | PASS |
| Case Sensitivity | All Lowercase | `Tell me about 'chilipa cdss girls hostel'` | 1 | 0 | 0 | FAIL |
| Case Sensitivity | Lowercase Code | `Show details for project mw-cr-do` | 1 | 0 | 0 | FAIL |
| Case Sensitivity | Mixed Case | `What is the status of CHILIPA cdss GIRLS hostel` | 1 | 0 | 0 | FAIL |
| Partial Match | Beginning | `Tell me about 'CHILIPA CDSS'` | 0 | 0 | 0 | PASS |
| Partial Match | End | `Show status of 'GIRLS HOSTEL'` | 0 | 0 | 0 | PASS |
| Partial Match | Project Code | `Project MW-CR` | 1 | 0 | 0 | FAIL |
| Format | Progress Query | `What is the progress of 'CHILIPA CDSS GIRLS HOSTEL'` | 1 | 0 | 0 | FAIL |
| Format | Budget Query | `Show me the budget for 'CHILIPA CDSS GIRLS HOSTEL'` | 1 | 0 | 0 | FAIL |
| Format | Contractor Query | `Who is the contractor for 'CHILIPA CDSS GIRLS HOSTEL'` | 1 | 0 | 0 | FAIL |
| Format | Completion Date Query | `When will 'CHILIPA CDSS GIRLS HOSTEL' be completed` | 1 | 0 | 0 | FAIL |
| Edge Case | Non-existent Project | `Tell me about 'Non Existent Project'` | 0 | 0 | 0 | PASS |
| Edge Case | Invalid Project Code | `Show details for project XX-YY-ZZ` | 0 | 0 | 0 | PASS |
| Edge Case | Multiple Projects | `Tell me about 'CHILIPA CDSS GIRLS HOSTEL' and 'Another Project'` | 1 | 0 | 0 | FAIL |
| Edge Case | Empty Project Name | `Tell me about ''` | 0 | 0 | 0 | PASS |
| Edge Case | Single Character | `Tell me about 'A'` | 0 | 0 | 0 | PASS |

## Detailed Results

### Exact Match: Full Quoted Name
**Query:** `Tell me about 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Exact Match: With Project Keyword
**Query:** `Show details for 'CHILIPA CDSS GIRLS HOSTEL project'`

**Results:**
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Exact Match: Full Project Code
**Query:** `Show details for project MW-CR-DO`

**Results:**
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Exact Match: Code with Status
**Query:** `Project code MW-CR-DO status`

**Results:**
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Case Sensitivity: All Lowercase
**Query:** `Tell me about 'chilipa cdss girls hostel'`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

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
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

### Partial Match: End
**Query:** `Show status of 'GIRLS HOSTEL'`

**Results:**
* Expected Count: 0
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
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Format: Budget Query
**Query:** `Show me the budget for 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Format: Contractor Query
**Query:** `Who is the contractor for 'CHILIPA CDSS GIRLS HOSTEL'`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Format: Completion Date Query
**Query:** `When will 'CHILIPA CDSS GIRLS HOSTEL' be completed`

**Results:**
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

### Edge Case: Non-existent Project
**Query:** `Tell me about 'Non Existent Project'`

**Results:**
* Expected Count: 0
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
* Expected Count: 1
* API Results: 0
* DB Results: 0
* Status: PASS

**Discrepancy Details:**
* Expected 1 results but got 0

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
* Expected Count: 0
* API Results: 0
* DB Results: 0
* Status: PASS

