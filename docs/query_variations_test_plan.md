# Dziwani Chatbot Query Variations Test Plan

This document provides a comprehensive set of query variations to test the Dziwani chatbot's ability to understand different phrasings of the same intent. Each section contains multiple ways to ask for the same information, organized by query type.

## 1. District-Based Queries

Testing the chatbot's ability to identify district names and return projects in those districts.

### Dowa District Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| D01 | Show me all projects in Dowa district | List of Dowa projects | | |
| D02 | Which projects are in Dowa? | List of Dowa projects | | |
| D03 | List Dowa projects | List of Dowa projects | | |
| D04 | What projects exist in Dowa? | List of Dowa projects | | |
| D05 | Projects located in Dowa | List of Dowa projects | | |
| D06 | Tell me about Dowa district projects | List of Dowa projects | | |
| D07 | What's happening in Dowa? | List of Dowa projects | | |
| D08 | Dowa infrastructure initiatives | List of Dowa projects | | |
| D09 | What are the current projects in Dowa district? | List of Dowa projects | | |
| D10 | Give me information on Dowa projects | List of Dowa projects | | |

### Lilongwe District Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| L01 | Show me all projects in Lilongwe district | List of Lilongwe projects | | |
| L02 | Which projects are in Lilongwe? | List of Lilongwe projects | | |
| L03 | List Lilongwe projects | List of Lilongwe projects | | |
| L04 | What projects exist in Lilongwe? | List of Lilongwe projects | | |
| L05 | Projects located in Lilongwe | List of Lilongwe projects | | |
| L06 | Tell me about Lilongwe district projects | List of Lilongwe projects | | |
| L07 | What's happening in Lilongwe? | List of Lilongwe projects | | |
| L08 | Lilongwe infrastructure initiatives | List of Lilongwe projects | | |
| L09 | What are the current projects in Lilongwe district? | List of Lilongwe projects | | |
| L10 | Give me information on Lilongwe projects | List of Lilongwe projects | | |

## 2. Project-Specific Queries

Testing the chatbot's ability to identify and return details about specific projects.

### Project Details Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| P01 | Tell me about the Rehabilitation of Chimulango irrigation scheme | Project details card | | |
| P02 | What is the Rehabilitation of Chimulango irrigation scheme? | Project details card | | |
| P03 | Details of Rehabilitation of Chimulango irrigation scheme | Project details card | | |
| P04 | Information on Rehabilitation of Chimulango irrigation scheme | Project details card | | |
| P05 | Show me the Rehabilitation of Chimulango irrigation scheme project | Project details card | | |
| P06 | I want to know about Rehabilitation of Chimulango irrigation scheme | Project details card | | |
| P07 | Give me details on Rehabilitation of Chimulango irrigation scheme | Project details card | | |
| P08 | Describe the Rehabilitation of Chimulango irrigation scheme project | Project details card | | |
| P09 | What can you tell me about Rehabilitation of Chimulango irrigation scheme? | Project details card | | |
| P10 | Rehabilitation of Chimulango irrigation scheme information | Project details card | | |

## 3. Sector-Based Queries

Testing the chatbot's ability to identify sector names and return projects in those sectors.

### Health Sector Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| S01 | Show me all health projects | List of health projects | | |
| S02 | Which projects are in the health sector? | List of health projects | | |
| S03 | List health sector projects | List of health projects | | |
| S04 | What health projects exist? | List of health projects | | |
| S05 | Projects in health sector | List of health projects | | |
| S06 | Tell me about health sector projects | List of health projects | | |
| S07 | What's happening in health? | List of health projects | | |
| S08 | Health infrastructure initiatives | List of health projects | | |
| S09 | What are the current health projects? | List of health projects | | |
| S10 | Give me information on health projects | List of health projects | | |

### Education Sector Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| E01 | Show me all education projects | List of education projects | | |
| E02 | Which projects are in the education sector? | List of education projects | | |
| E03 | List education sector projects | List of education projects | | |
| E04 | What education projects exist? | List of education projects | | |
| E05 | Projects in education sector | List of education projects | | |
| E06 | Tell me about education sector projects | List of education projects | | |
| E07 | What's happening in education? | List of education projects | | |
| E08 | Education infrastructure initiatives | List of education projects | | |
| E09 | What are the current education projects? | List of education projects | | |
| E10 | Give me information on education projects | List of education projects | | |

## 4. Combined Queries (District + Sector)

Testing the chatbot's ability to handle queries that combine district and sector filters.

### Combined Query Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| C01 | Show me health projects in Dowa district | List of Dowa health projects | | |
| C02 | Which education projects are in Lilongwe? | List of Lilongwe education projects | | |
| C03 | List road projects in Mzuzu | List of Mzuzu road projects | | |
| C04 | What health initiatives exist in Blantyre? | List of Blantyre health projects | | |
| C05 | Education projects located in Zomba | List of Zomba education projects | | |
| C06 | Tell me about water projects in Karonga district | List of Karonga water projects | | |
| C07 | What's happening with agriculture in Mchinji? | List of Mchinji agriculture projects | | |
| C08 | Infrastructure initiatives in Kasungu education sector | List of Kasungu education projects | | |
| C09 | What are the current health projects in Nkhata Bay district? | List of Nkhata Bay health projects | | |
| C10 | Give me information on Ntcheu road projects | List of Ntcheu road projects | | |

## 5. Budget-Related Queries

Testing the chatbot's ability to understand and respond to budget-related inquiries.

### Budget Query Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| B01 | What is the total budget for all projects? | Total budget figure | | |
| B02 | Show me the highest budget projects | List of high-budget projects | | |
| B03 | Which district has the most project funding? | District with highest funding | | |
| B04 | What's the average project budget? | Average budget figure | | |
| B05 | Show projects with budgets over 100 million MWK | List of high-budget projects | | |
| B06 | Which sector receives the most funding? | Sector with highest funding | | |
| B07 | Compare budgets between health and education sectors | Budget comparison | | |
| B08 | What percentage of the budget goes to infrastructure? | Budget percentage | | |
| B09 | List projects by budget (highest to lowest) | Sorted project list | | |
| B10 | How is the budget distributed across districts? | Budget distribution | | |

## 6. Status-Based Queries

Testing the chatbot's ability to filter projects by their implementation status.

### Status Query Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| ST01 | Show me all completed projects | List of completed projects | | |
| ST02 | Which projects are currently in progress? | List of in-progress projects | | |
| ST03 | List delayed projects | List of delayed projects | | |
| ST04 | What projects are on track? | List of on-track projects | | |
| ST05 | Projects with implementation delays | List of delayed projects | | |
| ST06 | Tell me about projects that are behind schedule | List of delayed projects | | |
| ST07 | What's the status of projects in Lilongwe? | Status of Lilongwe projects | | |
| ST08 | Show completed infrastructure initiatives | List of completed projects | | |
| ST09 | Which health projects are still in planning phase? | List of planned health projects | | |
| ST10 | Give me information on recently completed projects | List of completed projects | | |

## 7. Time-Based Queries

Testing the chatbot's ability to understand temporal aspects of projects.

### Time-Based Query Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| T01 | Show me projects from 2023 | List of 2023 projects | | |
| T02 | Which projects started this fiscal year? | List of current fiscal year projects | | |
| T03 | List projects ending in 2025 | List of projects ending in 2025 | | |
| T04 | What projects were active between 2022 and 2024? | List of projects in that timeframe | | |
| T05 | Projects initiated last year | List of last year's projects | | |
| T06 | Tell me about upcoming projects | List of upcoming projects | | |
| T07 | What's the timeline for Lilongwe water projects? | Timeline information | | |
| T08 | Show infrastructure initiatives planned for next fiscal year | List of planned projects | | |
| T09 | Which projects have the longest implementation period? | List of long-duration projects | | |
| T10 | Give me information on projects by timeline | Timeline-sorted projects | | |

## 8. Edge Cases and Negative Tests

Testing the chatbot's robustness with unusual or invalid queries.

### Edge Case Variations

| ID | Query Variation | Expected Result | Actual Result | Status |
|----|----------------|-----------------|---------------|--------|
| EC01 | Show me projects in Dowa District with typos | List of Dowa projects despite typos | | |
| EC02 | Tell me about non-existent project | Appropriate error message | | |
| EC03 | List projects in non-existent district | Appropriate error message | | |
| EC04 | What about projects? (vague query) | Request for clarification | | |
| EC05 | [empty message] | Request for input | | |
| EC06 | Show me ALL projects | Appropriate handling of large result set | | |
| EC07 | Tell me about Dowa and Lilongwe projects | Multi-district handling | | |
| EC08 | Projects with unusual characters: $#@! | Graceful error handling | | |
| EC09 | Very long query with excessive detail | Proper extraction of intent | | |
| EC10 | Non-English query | Appropriate response | | |

## Test Execution Script

```bash
#!/bin/bash

# Function to run a test and record results
run_test() {
  local id=$1
  local query=$2
  local expected=$3
  
  echo "Testing $id: \"$query\""
  
  # Run the test
  result=$(curl -s -X POST http://154.0.164.254:5000/api/rag-sql-chatbot/chat \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$query\"}" | jq -r '.results[].message')
  
  # Print result summary
  echo "  Result: ${result:0:100}..."
  echo "  Expected: $expected"
  
  # Determine if test passed (basic check - can be enhanced)
  if [[ "$result" == *"$expected"* ]]; then
    echo "  Status: PASS"
  else
    echo "  Status: FAIL"
  fi
  
  echo ""
  sleep 1
}

# Example usage
run_test "D01" "Show me all projects in Dowa district" "Found projects in Dowa district"
run_test "P01" "Tell me about the Rehabilitation of Chimulango irrigation scheme" "Project Details"
```

## Results Analysis Template

After running the tests, complete this analysis to identify patterns in successes and failures:

1. **Success Rate by Category:**
   - District Queries: ___%
   - Project-Specific Queries: ___%
   - Sector-Based Queries: ___%
   - Combined Queries: ___%
   - Budget-Related Queries: ___%
   - Status-Based Queries: ___%
   - Time-Based Queries: ___%
   - Edge Cases: ___%

2. **Common Failure Patterns:**
   - Pattern 1: [Description]
   - Pattern 2: [Description]

3. **Recommended Improvements:**
   - Improvement 1: [Description]
   - Improvement 2: [Description]

4. **Priority Areas:**
   - High Priority: [Areas]
   - Medium Priority: [Areas]
   - Low Priority: [Areas]
