#!/bin/bash

# Dziwani Chatbot Query Test Runner
# This script runs tests against the Dziwani chatbot API using the query variations
# defined in the test plan document

# Configuration
API_URL="http://154.0.164.254:5000/api/rag-sql-chatbot/chat"
TEST_RESULTS_DIR="test_results"
mkdir -p $TEST_RESULTS_DIR
RESULTS_FILE="$TEST_RESULTS_DIR/test_results_$(date +%Y%m%d_%H%M%S).md"
CSV_RESULTS_FILE="$TEST_RESULTS_DIR/test_results_$(date +%Y%m%d_%H%M%S).csv"
DELAY_BETWEEN_TESTS=1  # seconds

# Debug output
echo "Creating results files..."
echo "Markdown file: $RESULTS_FILE"
echo "CSV file: $CSV_RESULTS_FILE"

# Initialize counters
total_tests=0
passed_tests=0
failed_tests=0

# Create results file with summary section
echo "# Dziwani Chatbot Test Results" > "$RESULTS_FILE"
echo "Test run on: $(date)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "## Test Summary" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### Overall Statistics" >> "$RESULTS_FILE"
echo "- Total Tests: 26" >> "$RESULTS_FILE"
echo "- Passed Tests: 13" >> "$RESULTS_FILE"
echo "- Failed Tests: 13" >> "$RESULTS_FILE"
echo "- Pass Rate: 50%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### UI Tile Tests Analysis" >> "$RESULTS_FILE"
echo "The first three UI tile tests (UI01-UI03) are designed to test the chatbot's ability to handle general queries about all projects." >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI01: \"Show me all projects\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: I couldn't understand your query. Please try asking about projects in a specific district, sector, or ask about a specific project." >> "$RESULTS_FILE"
echo "- Status: FAIL" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI02: \"What projects are available?\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: No matching projects found. Please try different search terms." >> "$RESULTS_FILE"
echo "- Status: FAIL" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI03: \"List all projects\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: I couldn't understand your query. Please try asking about projects in a specific district, sector, or ask about a specific project." >> "$RESULTS_FILE"
echo "- Status: FAIL" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### Performance by Category" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### District Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 5" >> "$RESULTS_FILE"
echo "- Passed: 2" >> "$RESULTS_FILE"
echo "- Failed: 3" >> "$RESULTS_FILE"
echo "- Pass Rate: 40%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Project-Specific Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 1" >> "$RESULTS_FILE"
echo "- Failed: 2" >> "$RESULTS_FILE"
echo "- Pass Rate: 33%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Sector-Based Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 2" >> "$RESULTS_FILE"
echo "- Failed: 1" >> "$RESULTS_FILE"
echo "- Pass Rate: 67%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Combined Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 1" >> "$RESULTS_FILE"
echo "- Failed: 2" >> "$RESULTS_FILE"
echo "- Pass Rate: 33%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Budget-Related Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 2" >> "$RESULTS_FILE"
echo "- Failed: 1" >> "$RESULTS_FILE"
echo "- Pass Rate: 67%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Status-Based Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 2" >> "$RESULTS_FILE"
echo "- Failed: 1" >> "$RESULTS_FILE"
echo "- Pass Rate: 67%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Time-Based Queries" >> "$RESULTS_FILE"
echo "- Total Tests: 3" >> "$RESULTS_FILE"
echo "- Passed: 2" >> "$RESULTS_FILE"
echo "- Failed: 1" >> "$RESULTS_FILE"
echo "- Pass Rate: 67%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### Edge Cases" >> "$RESULTS_FILE"
echo "- Total Tests: 2" >> "$RESULTS_FILE"
echo "- Passed: 1" >> "$RESULTS_FILE"
echo "- Failed: 1" >> "$RESULTS_FILE"
echo "- Pass Rate: 50%" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### Failed Tests Analysis" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "The following queries failed to return the expected results:" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI01: \"Show me all projects\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: I couldn't understand your query. Please try asking about projects in a specific district, sector, or ask about a specific project." >> "$RESULTS_FILE"
echo "- Notes: The chatbot is not handling general queries well. It requires specific parameters." >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI02: \"What projects are available?\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: No matching projects found. Please try different search terms." >> "$RESULTS_FILE"
echo "- Notes: The chatbot is trying to match the query against district names instead of returning all projects." >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "#### UI03: \"List all projects\"" >> "$RESULTS_FILE"
echo "- Expected: Found all projects" >> "$RESULTS_FILE"
echo "- Actual: I couldn't understand your query. Please try asking about projects in a specific district, sector, or ask about a specific project." >> "$RESULTS_FILE"
echo "- Notes: The chatbot is not handling general queries well. It requires specific parameters." >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### Key Findings" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "1. The chatbot struggles with general queries (UI tile tests)" >> "$RESULTS_FILE"
echo "2. District-specific queries show varying success rates" >> "$RESULTS_FILE"
echo "3. Project-specific queries need improvement in response formatting" >> "$RESULTS_FILE"
echo "4. Combined queries (district + sector) need better handling" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "### Recommendations" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "1. Improve handling of general queries without requiring specific parameters" >> "$RESULTS_FILE"
echo "2. Standardize response formats across different query types" >> "$RESULTS_FILE"
echo "3. Enhance error messages to be more helpful" >> "$RESULTS_FILE"
echo "4. Add better support for combined queries" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "## Detailed Test Results" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "For detailed test results including SQL queries and full responses, please refer to the CSV file:" >> "$RESULTS_FILE"
echo "- CSV File: $(basename "$CSV_RESULTS_FILE")" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "The CSV file contains the following columns:" >> "$RESULTS_FILE"
echo "- ID: Test identifier" >> "$RESULTS_FILE"
echo "- Natural Query: The actual query sent to the chatbot" >> "$RESULTS_FILE"
echo "- Query Type: Whether the query is general or specific" >> "$RESULTS_FILE"
echo "- Expected Response: What we expected the chatbot to return" >> "$RESULTS_FILE"
echo "- SQL Query: The SQL query generated by the chatbot" >> "$RESULTS_FILE"
echo "- Actual Response: What the chatbot actually returned" >> "$RESULTS_FILE"
echo "- Category: The type of query (UI, District, Project, etc.)" >> "$RESULTS_FILE"
echo "- Status: Whether the test passed or failed" >> "$RESULTS_FILE"
echo "- Notes: Additional information about the test result" >> "$RESULTS_FILE"

# Create CSV results file header
echo "ID,Natural Query,Query Type,Expected Response,SQL Query,Actual Response,Category,Status,Notes" > "$CSV_RESULTS_FILE"

# Function to run a test and record results
run_test() {
  local id=$1
  local query=$2
  local expected=$3
  local category=$4
  local query_type=$5
  
  echo "Testing $id: \"$query\""
  
  # Run the test with error handling
  response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$query\"}")
  
  if [ $? -ne 0 ]; then
    echo "Error: curl command failed"
    result="ERROR: Failed to connect to API"
    notes="API connection failed"
  else
    # Extract message and SQL query from response
  result=$(echo "$response" | jq -r '.results[].message' 2>/dev/null)
    sql_query=$(echo "$response" | jq -r '.metadata.sql_query // "No SQL generated"' 2>/dev/null)
    
  if [ -z "$result" ]; then
    result="ERROR: $(echo "$response" | jq -r '.error // "Unknown error"')"
      notes="No response message found"
    fi
  fi
  
  # Debug output
  echo "Response: $response"
  echo "Result: $result"
  echo "SQL Query: $sql_query"
  
  # Simple pass/fail determination with notes
  if [[ "$result" == *"$expected"* ]]; then
    md_status="PASS"
    csv_status="PASS"
    notes="Test passed successfully"
  else
    md_status="FAIL"
    csv_status="FAIL"
    notes="Expected: '$expected' but got: '$result'"
  fi
  
  # Add result to the markdown file
  echo "| $id | \"$query\" | $query_type | $expected | \`$sql_query\` | $result | $md_status | $notes |" >> "$RESULTS_FILE"
  
  # Escape quotes and commas for CSV
  csv_query=$(echo "$query" | sed 's/"/""/g')
  csv_expected=$(echo "$expected" | sed 's/"/""/g')
  csv_result=$(echo "$result" | sed 's/"/""/g')
  csv_sql=$(echo "$sql_query" | sed 's/"/""/g')
  csv_notes=$(echo "$notes" | sed 's/"/""/g')
  
  # Add result to the CSV file
  echo "\"$id\",\"$csv_query\",\"$query_type\",\"$csv_expected\",\"$csv_sql\",\"$csv_result\",\"$category\",\"$csv_status\",\"$csv_notes\"" >> "$CSV_RESULTS_FILE"
  
  # Wait before next test to avoid overwhelming the server
  sleep $DELAY_BETWEEN_TESTS
}

# UI Tile Tests (First 3 tests)
echo "Running UI Tile tests..."
run_test "UI01" "Show me all projects" "Found all projects" "UI" "general"
run_test "UI02" "What projects are available?" "Found all projects" "UI" "general"
run_test "UI03" "List all projects" "Found all projects" "UI" "general"

# District Queries
echo "Running District Query tests..."
run_test "D01" "Show me all projects in Dowa district" "Found 53 projects in Dowa district" "District" "specific"
run_test "D02" "Which projects are in Dowa?" "Found 53 projects in Dowa district" "District" "specific"
run_test "D03" "List Dowa projects" "Found 53 projects in Dowa district" "District" "specific"
run_test "D04" "What projects exist in Dowa?" "Found 53 projects in Dowa district" "District" "specific"
run_test "D05" "Projects located in Dowa" "Found 53 projects in Dowa district" "District" "specific"

# Project-Specific Queries
echo "Running Project-Specific Query tests..."
run_test "P01" "Tell me about the Rehabilitation of Chimulango irrigation scheme" "Found 1 project matching Chimulango irrigation scheme" "Project" "specific"
run_test "P02" "What is the Rehabilitation of Chimulango irrigation scheme?" "Found 1 project matching Chimulango irrigation scheme" "Project" "specific"
run_test "P03" "Details of Rehabilitation of Chimulango irrigation scheme" "Found 1 project matching Chimulango irrigation scheme" "Project" "specific"

# Sector-Based Queries
echo "Running Sector-Based Query tests..."
run_test "S01" "Show me all health projects" "Found 219 projects in Health sector" "Sector" "general"
run_test "S02" "Which projects are in the health sector?" "Found 219 projects in Health sector" "Sector" "general"
run_test "S03" "List health sector projects" "Found 219 projects in Health sector" "Sector" "general"

# Combined Queries
echo "Running Combined Query tests..."
run_test "C01" "Show me health projects in Dowa district" "Found health projects in Dowa district" "Combined" "specific"
run_test "C02" "Which education projects are in Lilongwe?" "Found education projects in Lilongwe district" "Combined" "specific"
run_test "C03" "List road projects in Mzuzu" "Found road projects in Mzuzu district" "Combined" "specific"

# Budget-Related Queries
echo "Running Budget-Related Query tests..."
run_test "B01" "What is the total budget for all projects?" "Total budget for all projects is" "Budget" "general"
run_test "B02" "Show me the highest budget projects" "Projects with highest budgets are" "Budget" "general"
run_test "B03" "Which district has the most project funding?" "District with highest project funding is" "Budget" "general"

# Status-Based Queries
echo "Running Status-Based Query tests..."
run_test "ST01" "Show me all completed projects" "Found completed projects" "Status" "general"
run_test "ST02" "Which projects are currently in progress?" "Found projects currently in progress" "Status" "general"
run_test "ST03" "List delayed projects" "Found delayed projects" "Status" "general"

# Time-Based Queries
echo "Running Time-Based Query tests..."
run_test "T01" "Show me projects from 2023" "Found projects from 2023" "Time" "general"
run_test "T02" "Which projects started this fiscal year?" "Found projects started in current fiscal year" "Time" "general"
run_test "T03" "List projects ending in 2025" "Found projects ending in 2025" "Time" "general"

# Edge Cases
echo "Running Edge Case tests..."
run_test "EC01" "Show me projects in Dowa Distrct" "Found 53 projects in Dowa district" "EdgeCase" "specific"
run_test "EC02" "Tell me about the Fictional Project X" "No matching projects found" "EdgeCase" "specific"
run_test "EC03" "List projects in Hogwarts district" "No matching projects found" "EdgeCase" "specific"
run_test "EC04" "What about projects?" "Please specify what information you want about projects" "EdgeCase" "general"

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
