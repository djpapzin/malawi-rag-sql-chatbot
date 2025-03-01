#!/bin/bash

# Script to test production deployment of Malawi RAG SQL Chatbot

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Testing Production Deployment ===${NC}"

# Define the production URL - update this with your actual domain
PRODUCTION_URL="http://154.0.164.254:5000"
# Test URL to compare against
TEST_URL="http://154.0.164.254:5000"

echo -e "\n${YELLOW}Testing basic connectivity to production:${NC}"
if curl -s --head --request GET $PRODUCTION_URL | grep "200 OK" > /dev/null; then 
    echo -e "${GREEN}✓ Production server is responding${NC}"
else
    echo -e "${RED}✗ Production server is not responding${NC}"
fi

# Test a simple query
echo -e "\n${YELLOW}Testing simple query:${NC}"
QUERY='{"message": "What is the total population of Malawi?"}'
RESPONSE=$(curl -s -X POST $PRODUCTION_URL -H "Content-Type: application/json" -d "$QUERY")

if [[ $RESPONSE == *"population"* ]]; then
    echo -e "${GREEN}✓ Query returned expected results${NC}"
    echo "Response preview: ${RESPONSE:0:100}..."
else
    echo -e "${RED}✗ Query did not return expected results${NC}"
    echo "Response: $RESPONSE"
fi

# Check server load
echo -e "\n${YELLOW}Testing server load handling:${NC}"
for i in {1..5}; do
    curl -s -o /dev/null -w "%{http_code}" -X POST $PRODUCTION_URL -H "Content-Type: application/json" -d "$QUERY"
    echo -n " "
    sleep 1
done
echo -e "\n${GREEN}✓ Completed load test${NC}"

# Compare with test server
echo -e "\n${YELLOW}Comparing response times with test server:${NC}"
echo "Production server response time:"
time curl -s -o /dev/null $PRODUCTION_URL

echo "Test server response time:"
time curl -s -o /dev/null $TEST_URL

echo -e "\n${YELLOW}=== Testing Complete ===${NC}"
echo "For more comprehensive testing, consider running the full test suite." 