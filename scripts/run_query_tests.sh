#!/bin/bash

# Dziwani Chatbot Query Test Runner
# This script runs tests against the Dziwani chatbot API using the query variations
# defined in the test plan document

# Configuration
API_URL="http://154.0.164.254:5000/api/rag-sql-chatbot/chat"
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).md"
CSV_RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).csv"
DELAY_BETWEEN_TESTS=1  # seconds

# Create results file header
cat > $RESULTS_FILE << EOL
# Dziwani Chatbot Test Results
Test run on: $(date)

| ID | Query | Expected Result | Actual Result | Status |
|----|-------|----------------|---------------|--------|
EOL

# Create CSV results file header
echo "ID,Query,Expected Result,Actual Result,Status,Category,Full Response" > $CSV_RESULTS_FILE

# Function to run a test and record results
run_test() {
  local id=$1
  local query=$2
  local expected=$3
  local category=$4
  
  echo "Testing $id: \"$query\""
  
  # Run the test
  response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$query\"}")
  
  # Extract just the message part for readability
  result=$(echo "$response" | jq -r '.results[].message' 2>/dev/null)
  if [ -z "$result" ]; then
    result="ERROR: $(echo "$response" | jq -r '.error // "Unknown error"')"
  fi
  
  # Truncate long results for the table
  short_result="${result:0:100}"
  if [ ${#result} -gt 100 ]; then
    short_result="${short_result}..."
  fi
  
  # Simple pass/fail determination (can be enhanced)
  if [[ "$result" == *"$expected"* ]]; then
    md_status="PASS"
    csv_status="PASS"
  else
    md_status="FAIL"
    csv_status="FAIL"
  fi
  
  # Add result to the markdown file
  echo "| $id | \"$query\" | $expected | $short_result | $md_status |" >> $RESULTS_FILE
  
  # Escape quotes and commas for CSV
  csv_query=$(echo "$query" | sed 's/"/""/g')
  csv_expected=$(echo "$expected" | sed 's/"/""/g')
  csv_result=$(echo "$short_result" | sed 's/"/""/g')
  csv_full_response=$(echo "$result" | sed 's/"/""/g')
  
  # Add result to the CSV file
  echo "\"$id\",\"$csv_query\",\"$csv_expected\",\"$csv_result\",\"$csv_status\",\"$category\",\"$csv_full_response\"" >> $CSV_RESULTS_FILE
  
  # Wait before next test to avoid overwhelming the server
  sleep $DELAY_BETWEEN_TESTS
}

# District Queries
echo "Running District Query tests..."
run_test "D01" "Show me all projects in Dowa district" "Dowa" "District"
run_test "D02" "Which projects are in Dowa?" "Dowa" "District"
run_test "D03" "List Dowa projects" "Dowa" "District"
run_test "D04" "What projects exist in Dowa?" "Dowa" "District"
run_test "D05" "Projects located in Dowa" "Dowa" "District"

# Project-Specific Queries
echo "Running Project-Specific Query tests..."
run_test "P01" "Tell me about the Rehabilitation of Chimulango irrigation scheme" "Chimulango" "Project"
run_test "P02" "What is the Rehabilitation of Chimulango irrigation scheme?" "Chimulango" "Project"
run_test "P03" "Details of Rehabilitation of Chimulango irrigation scheme" "Chimulango" "Project"

# Sector-Based Queries
echo "Running Sector-Based Query tests..."
run_test "S01" "Show me all health projects" "health" "Sector"
run_test "S02" "Which projects are in the health sector?" "health" "Sector"
run_test "S03" "List health sector projects" "health" "Sector"

# Combined Queries
echo "Running Combined Query tests..."
run_test "C01" "Show me health projects in Dowa district" "health" "Combined"
run_test "C02" "Which education projects are in Lilongwe?" "education" "Combined"
run_test "C03" "List road projects in Mzuzu" "road" "Combined"

# Budget-Related Queries
echo "Running Budget-Related Query tests..."
run_test "B01" "What is the total budget for all projects?" "budget" "Budget"
run_test "B02" "Show me the highest budget projects" "budget" "Budget"
run_test "B03" "Which district has the most project funding?" "funding" "Budget"

# Status-Based Queries
echo "Running Status-Based Query tests..."
run_test "ST01" "Show me all completed projects" "completed" "Status"
run_test "ST02" "Which projects are currently in progress?" "progress" "Status"
run_test "ST03" "List delayed projects" "delayed" "Status"

# Time-Based Queries
echo "Running Time-Based Query tests..."
run_test "T01" "Show me projects from 2023" "2023" "Time"
run_test "T02" "Which projects started this fiscal year?" "fiscal" "Time"
run_test "T03" "List projects ending in 2025" "2025" "Time"

# Edge Cases
echo "Running Edge Case tests..."
run_test "EC01" "Show me projects in Dowa Distrct" "Dowa" "EdgeCase" # Typo in District
run_test "EC02" "Tell me about the Fictional Project X" "not found" "EdgeCase"
run_test "EC03" "List projects in Hogwarts district" "not found" "EdgeCase"
run_test "EC04" "What about projects?" "more specific" "EdgeCase"

echo "Testing complete! Results saved to $RESULTS_FILE and $CSV_RESULTS_FILE"

# Generate summary statistics from CSV file which is more reliable
total=$(grep -c "^\"" $CSV_RESULTS_FILE) 
total=$((total - 1))  # Subtract header row
passed=$(grep -c "\"PASS\"" $CSV_RESULTS_FILE)
failed=$((total - passed))
pass_rate=$(echo "scale=2; $passed / $total * 100" | bc)

# Calculate category-specific statistics
district_total=$(grep -c "\"District\"" $CSV_RESULTS_FILE)
district_passed=$(grep "\"District\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
district_rate=$(echo "scale=2; $district_passed / $district_total * 100" | bc)

project_total=$(grep -c "\"Project\"" $CSV_RESULTS_FILE)
project_passed=$(grep "\"Project\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
project_rate=$(echo "scale=2; $project_passed / $project_total * 100" | bc)

sector_total=$(grep -c "\"Sector\"" $CSV_RESULTS_FILE)
sector_passed=$(grep "\"Sector\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
sector_rate=$(echo "scale=2; $sector_passed / $sector_total * 100" | bc)

combined_total=$(grep -c "\"Combined\"" $CSV_RESULTS_FILE)
combined_passed=$(grep "\"Combined\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
combined_rate=$(echo "scale=2; $combined_passed / $combined_total * 100" | bc)

budget_total=$(grep -c "\"Budget\"" $CSV_RESULTS_FILE)
budget_passed=$(grep "\"Budget\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
budget_rate=$(echo "scale=2; $budget_passed / $budget_total * 100" | bc)

status_total=$(grep -c "\"Status\"" $CSV_RESULTS_FILE)
status_passed=$(grep "\"Status\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
status_rate=$(echo "scale=2; $status_passed / $status_total * 100" | bc)

time_total=$(grep -c "\"Time\"" $CSV_RESULTS_FILE)
time_passed=$(grep "\"Time\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
time_rate=$(echo "scale=2; $time_passed / $time_total * 100" | bc)

edge_total=$(grep -c "\"EdgeCase\"" $CSV_RESULTS_FILE)
edge_passed=$(grep "\"EdgeCase\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
edge_rate=$(echo "scale=2; $edge_passed / $edge_total * 100" | bc)

# UI testing statistics (initially 0 since these are manual tests)
ui_total=$(grep -c "\"UI\"" $CSV_RESULTS_FILE)
ui_passed=$(grep "\"UI\"" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
ui_rate=0
if [ $ui_total -gt 0 ]; then
  ui_rate=$(echo "scale=2; $ui_passed / $ui_total * 100" | bc)
fi

# Append summary to results file
cat >> $RESULTS_FILE << EOL

## Test Summary
- Total Tests: $total
- Passed: $passed
- Failed: $failed
- Pass Rate: ${pass_rate}%

### Category-Specific Results
- District Queries: $district_passed/$district_total (${district_rate}%)
- Project-Specific Queries: $project_passed/$project_total (${project_rate}%)
- Sector-Based Queries: $sector_passed/$sector_total (${sector_rate}%)
- Combined Queries: $combined_passed/$combined_total (${combined_rate}%)
- Budget-Related Queries: $budget_passed/$budget_total (${budget_rate}%)
- Status-Based Queries: $status_passed/$status_total (${status_rate}%)
- Time-Based Queries: $time_passed/$time_total (${time_rate}%)
- Edge Cases: $edge_passed/$edge_total (${edge_rate}%)
- UI-Based Testing: $ui_passed/$ui_total (${ui_rate}%)

## Recommendations
Based on the test results, here are some areas that may need improvement:
- [To be filled in after analysis]
EOL

echo "Summary statistics:"
echo "- Total Tests: $total"
echo "- Passed: $passed"
echo "- Failed: $failed"
echo "- Pass Rate: ${pass_rate}%"
echo ""
echo "Category-specific pass rates:"
echo "- District Queries: ${district_rate}%"
echo "- Project-Specific Queries: ${project_rate}%"
echo "- Sector-Based Queries: ${sector_rate}%"
echo "- Combined Queries: ${combined_rate}%"
echo "- Budget-Related Queries: ${budget_rate}%"
echo "- Status-Based Queries: ${status_rate}%"
echo "- Time-Based Queries: ${time_rate}%"
echo "- Edge Cases: ${edge_rate}%"
echo "- UI-Based Testing: ${ui_rate}%"
