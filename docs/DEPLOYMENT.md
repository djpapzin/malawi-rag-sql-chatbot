# Production Deployment Guide

## Server Requirements
- Ubuntu 22.04 LTS
- Python 3.11
- Node.js 18.x
- Nginx
- SSL Certificate (Let's Encrypt)

## Deployment Steps

1. Clone repository:
```bash
git clone https://github.com/your-repo/malawi-rag-sql-chatbot.git
cd malawi-rag-sql-chatbot
```

2. Configure environment:
```ini
# .env
PORT=5000
NODE_ENV=production
DATABASE_URL=sqlite:///app/database/projects.db
CORS_ORIGINS='["https://dziwani.kwantu.support"]'
```

3. Create start_server.sh script:
```bash
# Create the startup script
cat > start_server.sh << 'EOF'
#!/bin/bash

# Change to the project directory
cd /home/dj/malawi-rag-sql-chatbot

# Stop any existing gunicorn processes
pkill -f "gunicorn app.main:app"

# Activate conda environment
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Start the server with nohup
nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --access-logfile server_access.log --error-logfile server_error.log --log-level info > nohup.out 2>&1 &

echo "Server started on port 5000"
echo "Process ID: $!"
EOF

# Make it executable
chmod +x start_server.sh
```

4. Set up automatic restart on reboot:
```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot /home/dj/malawi-rag-sql-chatbot/start_server.sh") | crontab -
```

5. Start the server:
```bash
./start_server.sh
```

6. Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name dziwani.kwantu.support;

    ssl_certificate /etc/letsencrypt/live/dziwani.kwantu.support/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dziwani.kwantu.support/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }
    
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
}
```

## Maintenance

### Updating the Application
```bash
# Update code
git pull origin main

# Restart the server
./start_server.sh
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
```bash
# If the server fails to start, check for syntax errors
cd /home/dj/malawi-rag-sql-chatbot
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot
python -m uvicorn app.main:app --reload --host localhost --port 8000

# This will show any syntax errors immediately
```
