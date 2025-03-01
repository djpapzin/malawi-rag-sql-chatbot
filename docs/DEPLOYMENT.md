# Production Deployment Guide

## Server Requirements
- Ubuntu 22.04 LTS
- Python 3.11
- Miniconda (with malawi-rag-sql-chatbot environment)
- Nginx
- SSL Certificate (Let's Encrypt)

## Deployment Steps

1. Clone repository:
```bash
git clone https://github.com/your-repo/malawi-rag-sql-chatbot.git
cd malawi-rag-sql-chatbot
```

2. Configure environment:
```bash
# Create a conda environment
conda create -n malawi-rag-sql-chatbot python=3.11
conda activate malawi-rag-sql-chatbot

# Install dependencies
pip install -r requirements.txt
```

3. Create start_production.sh script:
```bash
#!/bin/bash

# Load conda environment
source ~/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Kill any existing processes
pkill -f "gunicorn app.main:app"

# Change to project directory
cd /home/dj/malawi-rag-sql-chatbot

# Start the server with gunicorn
nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --timeout 120 --access-logfile server_access.log --error-logfile server_error.log --log-level info > nohup.out 2>&1 &

echo "Server started on port 5000"
echo "Process ID: $!"
```

4. Make the script executable:
```bash
chmod +x start_production.sh
```

5. Set up automatic restart on reboot:
```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot /home/dj/malawi-rag-sql-chatbot/start_production.sh") | crontab -
```

6. Configure Nginx:
```nginx
server {
    listen 80;
    server_name dziwani.kwantu.support;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name dziwani.kwantu.support;

    ssl_certificate /etc/letsencrypt/live/dziwani.kwantu.support/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dziwani.kwantu.support/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin";

    # Proxy requests to the FastAPI application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

7. Apply and test Nginx configuration:
```bash
sudo cp your-nginx-config.conf /etc/nginx/conf.d/dziwani.kwantu.support.conf
sudo nginx -t
sudo systemctl reload nginx
```

8. Start the application:
```bash
./start_production.sh
```

## SSL Certificate Setup

1. Install Certbot:
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

2. Obtain SSL certificate:
```bash
sudo certbot --nginx -d dziwani.kwantu.support
```

3. Follow the prompts to complete the certificate issuance.

## Frontend Updates

If you need to update the frontend:

1. Modify the files in the `frontend/` directory
2. Ensure relative URLs are used in JavaScript files for API calls:
```javascript
// In frontend/static/js/main.js
// Use relative URLs for API endpoints
const API_BASE_URL = ''; // Empty string for relative URLs
// Then use: fetch(`${API_BASE_URL}/api/rag-sql-chatbot/chat`, ...)
```

## Maintenance

### Updating the Application
```bash
# Update code
git pull origin main

# Update the frontend if needed
# Edit frontend/static/js/main.js and other files

# Restart the server
./start_production.sh
```

### Monitoring
```bash
# Check if the server is running
ps -ef | grep gunicorn | grep -v grep

# Check logs
tail -f server_access.log
tail -f server_error.log
tail -f nohup.out
```

### Troubleshooting
If you encounter issues, refer to the [Troubleshooting Guide](TROUBLESHOOTING.md).
