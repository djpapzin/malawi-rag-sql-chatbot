# Deployment Workflow

This document outlines the deployment workflow for the Malawi RAG SQL Chatbot application.

## Development Workflow

1. Make changes to the codebase in your development environment
2. Test changes on the development server at http://154.0.164.254:5000
3. When you're ready to deploy to production, use the deployment script

## Development Environment

The development environment runs on the same server but doesn't affect the production URL.

### Starting the Development Server

```bash
# Start the development server
./restart.sh
```

### Testing Your Changes

```bash
# Test the health endpoint
curl -X GET http://154.0.164.254:5000/api/rag-sql-chatbot/health -H "Content-Type: application/json" | jq
```

## Production Deployment

When you're satisfied with your changes and want to deploy to production:

```bash
# Deploy to production
./deploy_to_production.sh
```

This script will:
1. Copy your code to the production directory
2. Update the production environment settings
3. Restart the production service
4. Your changes will be available at https://dziwani.kwantu.support/

## Deployment Architecture

- Development URL: http://154.0.164.254:5000
  - Points directly to your development code
  - Changes take effect immediately after restart

- Production URL: https://dziwani.kwantu.support
  - Served through Nginx
  - Only updated when you explicitly deploy changes
  - Protected from development changes

## Checking Deployment Status

```bash
# Check if the production server is running
curl -X GET https://dziwani.kwantu.support/api/rag-sql-chatbot/health
```
