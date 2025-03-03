#!/bin/bash

# Dziwani Chatbot UI Test Recorder
# This script helps document manual UI testing results

# Configuration
RESULTS_FILE="ui_test_results_$(date +%Y%m%d_%H%M%S).md"
CSV_RESULTS_FILE="ui_test_results_$(date +%Y%m%d_%H%M%S).csv"

# Create results file header
cat > $RESULTS_FILE << EOL
# Dziwani Chatbot UI Test Results
Test run on: $(date)

| ID | UI Interaction | Query/Action | Expected Result | Actual Result | Status | Notes |
|----|---------------|--------------|-----------------|---------------|--------|-------|
EOL

# Create CSV results file header
echo "ID,UI Interaction,Query/Action,Expected Result,Actual Result,Status,Notes,Category" > $CSV_RESULTS_FILE

# Function to record a UI test result
record_test() {
  local id=$1
  local interaction=$2
  local query=$3
  local expected=$4
  
  echo "Recording test $id: $interaction"
  echo "Query/Action: $query"
  echo "Expected Result: $expected"
  
  # Prompt for actual result
  echo -n "Enter actual result: "
  read actual
  
  # Prompt for status
  echo -n "Status (PASS/FAIL): "
  read status
  
  # Prompt for additional notes
  echo -n "Additional notes (optional): "
  read notes
  
  # Add result to the markdown file
  echo "| $id | $interaction | $query | $expected | $actual | $status | $notes |" >> $RESULTS_FILE
  
  # Escape quotes and commas for CSV
  csv_interaction=$(echo "$interaction" | sed 's/"/""/g')
  csv_query=$(echo "$query" | sed 's/"/""/g')
  csv_expected=$(echo "$expected" | sed 's/"/""/g')
  csv_actual=$(echo "$actual" | sed 's/"/""/g')
  csv_notes=$(echo "$notes" | sed 's/"/""/g')
  
  # Add result to the CSV file
  echo "\"$id\",\"$csv_interaction\",\"$csv_query\",\"$csv_expected\",\"$csv_actual\",\"$status\",\"$csv_notes\",\"UI\"" >> $CSV_RESULTS_FILE
  
  echo "Test recorded!"
  echo "-----------------------------------"
}

# UI Tests from the test plan
echo "Starting UI Test Recording..."

record_test "UI01" "Click on \"Find project by sector\" tile and see the results of what gets loaded" "Which projects are there in the health sector?" "Total number of health projects in the database, e.g. 219"

record_test "UI02" "Click on \"Find projects by district\" tile and see the response that is generated" "Show me All projects in Zomba District" "Return a list of all projects in Zomba district with info like budget, etc"

record_test "UI03" "Click on \"Find a specific project\" tile and see the response generated" "Tell me about the Nyandule Classroom Block project" "Return specific details about the Nyandule Classroom Block project"

record_test "UI04" "Use the chat input field directly" "What is the total budget for education projects in Lilongwe?" "Return aggregated budget information for education projects in Lilongwe"

record_test "UI05" "Test responsive design on mobile device" "Same queries as above" "Interface should adapt to screen size while maintaining functionality"

record_test "UI06" "Test loading indicators" "Submit a complex query requiring processing time" "User should see appropriate loading indicators while waiting for response"

record_test "UI07" "Test error handling" "Submit an intentionally malformed query" "System should provide a helpful error message"

record_test "UI08" "Test chat history functionality" "Submit multiple queries and check history" "Previous queries and responses should be accessible"

record_test "UI09" "Test UI filters/dropdowns if available" "Use any available UI filters" "Results should be filtered according to selection"

record_test "UI10" "Test UI reset/clear functionality" "Use clear/reset button if available" "Chat history should be cleared"

# Calculate statistics
total=$(grep -c "^\"UI" $CSV_RESULTS_FILE)
passed=$(grep "^\"UI" $CSV_RESULTS_FILE | grep -c "\"PASS\"")
failed=$((total - passed))
pass_rate=$(echo "scale=2; $passed / $total * 100" | bc)

# Append summary to results file
cat >> $RESULTS_FILE << EOL

## UI Test Summary
- Total UI Tests: $total
- Passed: $passed
- Failed: $failed
- Pass Rate: ${pass_rate}%

## UI Test Observations
- [Add manual observations here]

## Screenshots
- [Add links to screenshot files here if applicable]
EOL

echo "UI Testing complete! Results saved to $RESULTS_FILE and $CSV_RESULTS_FILE"
echo "Summary statistics:"
echo "- Total UI Tests: $total"
echo "- Passed: $passed"
echo "- Failed: $failed"
echo "- Pass Rate: ${pass_rate}%"

# Make the script executable
chmod +x "$0"
