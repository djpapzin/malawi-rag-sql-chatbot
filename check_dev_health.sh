#!/bin/bash

# Simple script to check the health of the development server

echo "Checking development server health..."
curl -X GET http://154.0.164.254:5000/api/rag-sql-chatbot/health -H "Content-Type: application/json" | jq

echo ""
echo "To deploy changes to production, run:"
echo "./deploy_to_production.sh"
