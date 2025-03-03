#!/bin/bash

# Dziwani Chatbot Query Test Runner
# This script runs tests against the Dziwani chatbot API using the query variations
# defined in the test plan document

# Configuration
API_URL="http://154.0.164.254:5000/api/rag-sql-chatbot/chat"
RESULTS_FILE="test_results_$(date +%Y%m%d_%H%M%S).md"
DELAY_BETWEEN_TESTS=1  # seconds

# Create results file header
cat > $RESULTS_FILE << EOL
# Dziwani Chatbot Test Results
Test run on: $(date)

| ID | Query | Expected Result | Actual Result | Status |
|----|-------|----------------|---------------|--------|
EOL

# Function to run a test and record results
run_test() {
  local id=$1
  local query=$2
  local expected=$3
  
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
    status="✅ PASS"
  else
    status="❌ FAIL"
  fi
  
  # Add result to the file
  echo "| $id | \"$query\" | $expected | $short_result | $status |" >> $RESULTS_FILE
  
  # Wait before next test to avoid overwhelming the server
  sleep $DELAY_BETWEEN_TESTS
}

# District Queries
echo "Running District Query tests..."
run_test "D01" "Show me all projects in Dowa district" "Dowa"
run_test "D02" "Which projects are in Dowa?" "Dowa"
run_test "D03" "List Dowa projects" "Dowa"
run_test "D04" "What projects exist in Dowa?" "Dowa"
run_test "D05" "Projects located in Dowa" "Dowa"

# Project-Specific Queries
echo "Running Project-Specific Query tests..."
run_test "P01" "Tell me about the Rehabilitation of Chimulango irrigation scheme" "Chimulango"
run_test "P02" "What is the Rehabilitation of Chimulango irrigation scheme?" "Chimulango"
run_test "P03" "Details of Rehabilitation of Chimulango irrigation scheme" "Chimulango"

# Sector-Based Queries
echo "Running Sector-Based Query tests..."
run_test "S01" "Show me all health projects" "health"
run_test "S02" "Which projects are in the health sector?" "health"
run_test "S03" "List health sector projects" "health"

# Combined Queries
echo "Running Combined Query tests..."
run_test "C01" "Show me health projects in Dowa district" "health" 
run_test "C02" "Which education projects are in Lilongwe?" "education"
run_test "C03" "List road projects in Mzuzu" "road"

# Budget-Related Queries
echo "Running Budget-Related Query tests..."
run_test "B01" "What is the total budget for all projects?" "budget"
run_test "B02" "Show me the highest budget projects" "budget"
run_test "B03" "Which district has the most project funding?" "funding"

# Status-Based Queries
echo "Running Status-Based Query tests..."
run_test "ST01" "Show me all completed projects" "completed"
run_test "ST02" "Which projects are currently in progress?" "progress"
run_test "ST03" "List delayed projects" "delayed"

# Time-Based Queries
echo "Running Time-Based Query tests..."
run_test "T01" "Show me projects from 2023" "2023"
run_test "T02" "Which projects started this fiscal year?" "fiscal"
run_test "T03" "List projects ending in 2025" "2025"

# Edge Cases
echo "Running Edge Case tests..."
run_test "EC01" "Show me projects in Dowa Distrct" "Dowa" # Typo in District
run_test "EC02" "Tell me about the Fictional Project X" "not found"
run_test "EC03" "List projects in Hogwarts district" "not found"
run_test "EC04" "What about projects?" "more specific"

echo "Testing complete! Results saved to $RESULTS_FILE"

# Generate summary statistics
total=$(grep -c "^|" $RESULTS_FILE)
passed=$(grep -c "✅ PASS" $RESULTS_FILE)
failed=$(grep -c "❌ FAIL" $RESULTS_FILE)
pass_rate=$(echo "scale=2; $passed / ($total - 1) * 100" | bc)

# Append summary to results file
cat >> $RESULTS_FILE << EOL

## Test Summary
- Total Tests: $(($total - 1))
- Passed: $passed
- Failed: $failed
- Pass Rate: ${pass_rate}%

## Recommendations
Based on the test results, here are some areas that may need improvement:
- [To be filled in after analysis]
EOL

echo "Summary statistics:"
echo "- Total Tests: $(($total - 1))"
echo "- Passed: $passed"
echo "- Failed: $failed"
echo "- Pass Rate: ${pass_rate}%"
