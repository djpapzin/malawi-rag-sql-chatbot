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

3. Production startup:
```bash
./run_production.sh  # Uses gunicorn with 4 workers
```

4. Nginx configuration:
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
```bash
# Update process
git pull origin main
pkill -f "gunicorn app.main:app"
./run_production.sh

# Log monitoring
tail -f app.log
