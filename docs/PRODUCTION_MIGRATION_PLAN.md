# Production Migration Plan

This document outlines the steps that were taken to migrate the application to production and the fixes that were applied to ensure proper functioning.

## Deployment Steps Completed

### 1. Server Setup
- Installed required dependencies: Python, Nginx, Certbot
- Configured conda environment with required packages
- Configured Nginx as a reverse proxy

### 2. SSL Certificate Setup
- Installed Certbot for SSL certificate management
- Obtained SSL certificate for dziwani.kwantu.support
- Configured Nginx to use the SSL certificate
- Set up automatic renewal

### 3. Application Deployment
- Created start_production.sh script for starting the application
- Configured Gunicorn with multiple workers
- Set up error logging and access logging
- Configured automatic startup on reboot

### 4. Frontend Configuration
- Updated main.js to use relative URLs for API requests
- Fixed static file handling
- Ensured proper error handling

### 5. Nginx Configuration
- Set up Nginx to proxy all requests to the FastAPI application
- Configured SSL termination
- Added security headers
- Set up HTTP to HTTPS redirection

## Issues Fixed

### 1. Static Files Not Loading
- Problem: Static files (CSS and JS) were not being served correctly
- Solution: Updated Nginx configuration to proxy all requests to FastAPI
- Verification: Tested with curl commands to ensure files are accessible

### 2. API URL Configuration
- Problem: Frontend was using hardcoded API URLs
- Solution: Updated main.js to use relative URLs (`API_BASE_URL = ''`)
- Verification: Tested API calls to ensure they work correctly

### 3. Nginx Configuration Conflicts
- Problem: Conflicting server_name directives for dziwani.kwantu.support
- Solution: Removed references to dziwani.kwantu.support from ai.kwantu.support.conf
- Verification: Tested Nginx configuration with nginx -t

### 4. Worker Timeout Issues
- Problem: Worker processes timing out on complex queries
- Solution: Increased timeout parameter in Gunicorn configuration
- Verification: Tested with complex queries to ensure they complete successfully

### 5. Server Startup Reliability
- Problem: Server not starting reliably after reboot
- Solution: Created comprehensive start_production.sh script
- Verification: Tested with manual restart and reboot simulation

## Current Configuration

### 1. Server Details
- Domain: dziwani.kwantu.support
- Server IP: 154.0.164.254
- Application Port: 5000
- Web Server: Nginx
- Application Server: Gunicorn with Uvicorn workers

### 2. File Locations
- Application Directory: /home/dj/malawi-rag-sql-chatbot
- Nginx Configuration: /etc/nginx/conf.d/dziwani.kwantu.support.conf
- SSL Certificates: /etc/letsencrypt/live/dziwani.kwantu.support/
- Logs: /home/dj/malawi-rag-sql-chatbot/server_access.log, server_error.log

### 3. Startup Process
- Startup Script: /home/dj/malawi-rag-sql-chatbot/start_production.sh
- Automatic Startup: Configured via crontab (@reboot)

## Verification Steps

The following verification steps were completed to ensure the application is working correctly:

### 1. Static Files Accessibility
```bash
# Verify CSS file is accessible
curl -s -I https://dziwani.kwantu.support/static/css/loading.css

# Verify JS file is accessible
curl -s -I https://dziwani.kwantu.support/static/js/main.js
```

### 2. API Functionality
```bash
# Test API health endpoint
curl -s https://dziwani.kwantu.support/health

# Test chat endpoint
curl -s -X POST https://dziwani.kwantu.support/api/rag-sql-chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### 3. Website Functionality
- Accessed https://dziwani.kwantu.support in browser
- Verified that the website loads correctly
- Verified that the chat functionality works
- Verified that loading indicators display correctly
- Tested with various queries to ensure correct responses

## Maintenance Procedures

### 1. Monitoring
```bash
# Check if the server is running
ps -ef | grep gunicorn | grep -v grep

# Check logs
tail -f server_access.log
tail -f server_error.log
```

### 2. Updates
```bash
# Pull latest changes
git pull origin main

# Restart the server
./start_production.sh
```

### 3. Troubleshooting
For detailed troubleshooting steps, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md). 