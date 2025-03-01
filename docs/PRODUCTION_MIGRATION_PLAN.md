# Production Migration Plan for Malawi RAG SQL Chatbot

This document outlines the step-by-step process for migrating the Malawi RAG SQL Chatbot from the testing environment (http://154.0.164.254:5000/) to the production environment.

## Pre-Migration Checklist

- [ ] Confirm all features are working correctly in the testing environment
- [ ] Backup the entire application and database
- [ ] Document current configuration settings
- [ ] Notify stakeholders of planned migration and expected downtime

## Domain and DNS Setup

- [ ] Register a production domain (if not already done)
- [ ] Configure DNS records to point to the production server
- [ ] Set up SSL certificates for the production domain
- [ ] Configure DNS A records for the new domain pointing to the production server IP
- [ ] Set up HTTPS with Let's Encrypt or similar service

## Server Preparation

- [ ] Provision production server with adequate resources
- [ ] Set up firewall rules (allow ports 80, 443, 5000)
- [ ] Install required system packages:
  ```bash
  sudo apt update
  sudo apt install -y build-essential python3-dev nginx supervisor
  ```
- [ ] Install and configure Miniconda (if not already installed)
- [ ] Create and activate the conda environment:
  ```bash
  source /home/dj/miniconda/etc/profile.d/conda.sh
  conda create -n malawi-rag-sql-chatbot python=3.10
  conda activate malawi-rag-sql-chatbot
  ```

## Application Deployment

- [ ] Clone the repository to the production server:
  ```bash
  git clone [repository_url] /path/to/production/malawi-rag-sql-chatbot
  ```
- [ ] Install dependencies:
  ```bash
  cd /path/to/production/malawi-rag-sql-chatbot
  conda activate malawi-rag-sql-chatbot
  pip install -r requirements.txt
  ```
- [ ] Copy or configure environment variables (.env file)
- [ ] Test the application locally on the production server
- [ ] Update the start_server.sh script with production settings

## Production Configuration

- [ ] Set up Nginx as a reverse proxy:
  ```bash
  sudo nano /etc/nginx/sites-available/malawi-rag-sql-chatbot
  ```
  
  Add the following configuration:
  ```nginx
  server {
      listen 80;
      server_name your-production-domain.com;
      
      location / {
          proxy_pass http://127.0.0.1:5000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```
  
  Enable the site:
  ```bash
  sudo ln -s /etc/nginx/sites-available/malawi-rag-sql-chatbot /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

- [ ] Set up SSL with Certbot:
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d your-production-domain.com
  ```
  
- [ ] Configure supervisor for process management:
  ```bash
  sudo nano /etc/supervisor/conf.d/malawi-rag-sql-chatbot.conf
  ```
  
  Add the following configuration:
  ```ini
  [program:malawi-rag-sql-chatbot]
  directory=/path/to/production/malawi-rag-sql-chatbot
  command=/bin/bash -c "source /home/dj/miniconda/etc/profile.d/conda.sh && conda activate malawi-rag-sql-chatbot && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --timeout 120 --access-logfile server_access.log --error-logfile server_error.log --log-level info"
  autostart=true
  autorestart=true
  stopasgroup=true
  killasgroup=true
  user=[your_system_user]
  stdout_logfile=/path/to/production/malawi-rag-sql-chatbot/supervisor_stdout.log
  stderr_logfile=/path/to/production/malawi-rag-sql-chatbot/supervisor_stderr.log
  ```
  
  Apply the configuration:
  ```bash
  sudo supervisorctl reread
  sudo supervisorctl update
  ```

## Security Enhancements

- [ ] Set up rate limiting in Nginx:
  ```nginx
  # Add to the server block in Nginx configuration
  limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
  
  location / {
      limit_req zone=api_limit burst=20 nodelay;
      # ... existing configuration
  }
  ```

- [ ] Configure firewall to only allow necessary ports:
  ```bash
  sudo ufw allow 22
  sudo ufw allow 80
  sudo ufw allow 443
  sudo ufw enable
  ```

- [ ] Set up fail2ban to prevent brute force attacks:
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable fail2ban
  sudo systemctl start fail2ban
  ```

## Launch Procedure

- [ ] Stop the test server:
  ```bash
  pkill -f "gunicorn app.main:app"
  ```

- [ ] Start the production server using supervisor:
  ```bash
  sudo supervisorctl start malawi-rag-sql-chatbot
  ```

- [ ] Alternative: Start with nohup (as per request):
  ```bash
  cd /path/to/production/malawi-rag-sql-chatbot
  source /home/dj/miniconda/etc/profile.d/conda.sh
  conda activate malawi-rag-sql-chatbot
  nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --timeout 120 --access-logfile server_access.log --error-logfile server_error.log --log-level info > nohup.out 2>&1 &
  ```

## Testing and Verification

- [ ] Test the production URL with basic health check:
  ```bash
  curl -v https://your-production-domain.com/
  ```

- [ ] Test critical API endpoints:
  ```bash
  curl -X POST https://your-production-domain.com/ -H "Content-Type: application/json" -d '{"message": "test query"}'
  ```

- [ ] Verify logs for any errors:
  ```bash
  tail -n 100 server_error.log
  tail -n 100 server_access.log
  ```

- [ ] Perform load testing (if applicable)

## Monitoring and Maintenance

- [ ] Set up application monitoring (Prometheus, Grafana, etc.)
- [ ] Configure log rotation:
  ```bash
  sudo nano /etc/logrotate.d/malawi-rag-sql-chatbot
  ```
  
  Add the following configuration:
  ```
  /path/to/production/malawi-rag-sql-chatbot/*.log {
      daily
      rotate 7
      compress
      delaycompress
      missingok
      notifempty
      create 640 [user] [group]
  }
  ```

- [ ] Create automated backup script for database and configuration

## Rollback Plan

In case of issues in production:

- [ ] Stop the production services:
  ```bash
  sudo supervisorctl stop malawi-rag-sql-chatbot
  # or if using nohup
  pkill -f "gunicorn app.main:app"
  ```

- [ ] Restore from backup if needed
- [ ] Redirect DNS temporarily back to testing server
- [ ] Restart the testing server:
  ```bash
  cd /home/dj/malawi-rag-sql-chatbot
  ./start_server.sh
  ```

## Post-Migration Checklist

- [ ] Confirm all features are working in production
- [ ] Monitor error logs for new issues
- [ ] Update documentation with new production URL
- [ ] Notify stakeholders of completed migration
- [ ] Schedule regular maintenance and backup procedures

## PowerShell Commands (Windows Admin)

For Windows administrators, here are PowerShell equivalents for some of the commands:

```powershell
# Check if the server is running
Get-Process | Where-Object {$_.ProcessName -like "*gunicorn*"}

# Test the API endpoint
Invoke-RestMethod -Uri "https://your-production-domain.com/" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"message": "test query"}'

# Monitor logs
Get-Content -Path "server_error.log" -Tail 100 -Wait
``` 