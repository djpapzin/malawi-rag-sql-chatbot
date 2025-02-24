# Deployment Guide: Dwizani Chatbot

## Server Requirements
- CentOS 7/8
- Python 3.9+
- Git
- Nginx
- Conda/Miniconda installed

## Deployment Steps

### 1. Server Access
```bash
ssh username@154.0.164.254
cd /var/www/dziwani/
```

### 2. Update Codebase
```bash
# If first deployment
git clone https://github.com/your-repo/rag-sql-chatbot.git

# For subsequent updates
cd rag-sql-chatbot
git pull origin main
```

### 3. Environment Setup
```bash
conda activate rag-sql-bot
pip install -r requirements.txt

# Create production .env
cp .env.example .env
nano .env  # Update with production values
```

### 4. Process Management (Systemd Service)
Create `/etc/systemd/system/dziwani.service`:
```ini
[Unit]
Description=Dwizani Chatbot Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dziwani/rag-sql-chatbot
EnvironmentFile=/var/www/dziwani/rag-sql-chatbot/.env
ExecStart=/opt/conda/envs/rag-sql-bot/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration
Create `/etc/nginx/conf.d/dziwani.conf`:
```nginx
server {
    listen 80;
    server_name dziwani.kwantu.support;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/dziwani/rag-sql-chatbot/frontend/static;
    }
}
```

### 6. SSL Setup
```bash
sudo certbot --nginx -d dziwani.kwantu.support
```

### 7. Service Management
```bash
sudo systemctl daemon-reload
sudo systemctl start dziwani
sudo systemctl enable dziwani
sudo systemctl restart nginx
```

## Testing Procedure
1. Verify service status:
```bash
systemctl status dziwani
curl http://localhost:5000/health
```

2. Test public access:
```bash
curl https://dziwani.kwantu.support/api/rag-sql-chatbot/health
```

## Update Workflow
```bash
ssh username@154.0.164.254
cd /var/www/dziwani/rag-sql-chatbot
git pull origin main
sudo systemctl restart dziwani
```
