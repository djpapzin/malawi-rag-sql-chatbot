# Dziwani Chatbot Testing Guide

This guide explains how to use the testing tools for the Dziwani Chatbot to evaluate both API functionality and UI experience.

## Overview

The testing framework consists of two main components:

1. **API Testing Script** - Automated tests for the backend API functionality
2. **UI Testing Recorder** - Tool for documenting manual UI tests

Both tools generate standardized output files that can be combined for comprehensive test reporting.

## 1. API Testing

The API testing script automatically sends queries to the chatbot API and evaluates the responses against expected results.

### Running API Tests

```bash
# Make sure the server is running before executing tests
# Check server health
curl -X GET http://154.0.164.254:5000/api/rag-sql-chatbot/health -H "Content-Type: application/json" | jq

# Run the tests
cd /home/dj/malawi-rag-sql-chatbot
./scripts/run_query_tests.sh
```

### Test Output

The script generates two output files:
- `test_results_YYYYMMDD_HHMMSS.md` - Markdown report with human-readable results
- `test_results_YYYYMMDD_HHMMSS.csv` - CSV file with detailed results for analysis

### Customizing API Tests

To add or modify test cases, edit the `run_query_tests.sh` script. Each test follows this pattern:

```bash
run_test "ID" "Query text" "Expected result text" "Category"
```

## 2. UI Testing

UI testing is performed manually using the UI test recorder script to document the results.

### Running UI Tests

```bash
# Start the UI test recorder
cd /home/dj/malawi-rag-sql-chatbot
./scripts/ui_test_recorder.sh
```

The script will guide you through each test case, prompting for:
- Actual result observed
- Test status (PASS/FAIL)
- Additional notes

### Test Output

The UI test recorder generates:
- `ui_test_results_YYYYMMDD_HHMMSS.md` - Markdown report with UI test results
- `ui_test_results_YYYYMMDD_HHMMSS.csv` - CSV file with UI test data

### Customizing UI Tests

To modify the UI test cases, edit both:
1. The `ui_test_recorder.sh` script
2. The UI testing section in `docs/query_variations_test_plan.md`

## 3. Combining Test Results

To get a comprehensive view of both API and UI test results, you can combine the CSV files:

```bash
# Combine the most recent API and UI test results
cd /home/dj/malawi-rag-sql-chatbot
API_CSV=$(ls -t test_results_*.csv | head -1)
UI_CSV=$(ls -t ui_test_results_*.csv | head -1)
HEADER=$(head -1 $API_CSV)
COMBINED_CSV="combined_results_$(date +%Y%m%d_%H%M%S).csv"

echo $HEADER > $COMBINED_CSV
tail -n +2 $API_CSV >> $COMBINED_CSV
tail -n +2 $UI_CSV >> $COMBINED_CSV

echo "Combined results saved to $COMBINED_CSV"
```

## 4. Test Plan Reference

The complete test plan is documented in `docs/query_variations_test_plan.md`, which includes:

- District-Based Queries
- Project-Specific Queries
- Sector-Based Queries
- Combined Queries
- Budget-Related Queries
- Status-Based Queries
- Time-Based Queries
- Edge Cases
- UI-Based Testing

## 5. Recommended Testing Workflow

1. **Preparation**:
   - Ensure the server is running
   - Verify server health with the health check endpoint

2. **API Testing**:
   - Run the automated API tests
   - Review the results and identify failing categories

3. **UI Testing**:
   - Perform manual UI tests using the recorder script
   - Document any UI-specific issues

4. **Analysis**:
   - Combine test results if needed
   - Identify patterns in failures
   - Prioritize improvements based on failure categories

5. **Documentation**:
   - Update test plans with new test cases as needed
   - Document any workarounds or known issues

## 6. Screenshot Documentation

For UI testing, it's recommended to capture screenshots of key interactions and results. Store these in a dedicated folder:

```bash
mkdir -p /home/dj/malawi-rag-sql-chatbot/test_screenshots/$(date +%Y%m%d)
```

Reference these screenshots in your UI test notes for visual documentation of issues or successes.
