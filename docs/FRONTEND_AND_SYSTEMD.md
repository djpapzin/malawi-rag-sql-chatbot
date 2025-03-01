# Frontend Build and Systemd Configuration

This document supplements the main Production Migration Plan with specific instructions for frontend build processes and systemd service configuration.

## Frontend Build Process

If your application includes a frontend component (React, Vue, Angular, etc.), follow these steps to prepare it for production:

### 1. Identify Frontend Technology

Determine which frontend framework/library your application uses:
- React: Look for `react`, `react-dom` in package.json
- Vue: Look for `vue` in package.json
- Angular: Look for `@angular/core` in package.json

### 2. Install Dependencies

```bash
# Navigate to the frontend directory (may vary based on project structure)
cd /home/dj/malawi-rag-sql-chatbot/frontend  # or appropriate path

# Install production dependencies
npm ci  # preferred for production over npm install
```

### 3. Build for Production

```bash
# For React/Vue projects (typical command)
npm run build

# For Angular projects
ng build --prod
```

### 4. Verify Build Output

The build process typically produces optimized static files in a directory like:
- `build/` (React)
- `dist/` (Vue, Angular)

```bash
# Check the generated files
ls -la build/  # or dist/
```

### 5. Configure Backend to Serve Frontend

Update your FastAPI or Flask application to serve the static files:

For FastAPI:
```python
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

app = FastAPI()

# Mount the static files directory
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")
```

For Flask:
```python
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

## Systemd Service Configuration

Systemd provides robust service management for Linux production environments.

### 1. Create Systemd Service File

```bash
sudo nano /etc/systemd/system/malawi-rag-sql-chatbot.service
```

Add the following configuration:

```ini
[Unit]
Description=Malawi RAG SQL Chatbot
After=network.target

[Service]
User=dj
Group=dj
WorkingDirectory=/home/dj/malawi-rag-sql-chatbot
ExecStart=/bin/bash -c "source /home/dj/miniconda/etc/profile.d/conda.sh && conda activate malawi-rag-sql-chatbot && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --timeout 120 --access-logfile /home/dj/malawi-rag-sql-chatbot/production_access.log --error-logfile /home/dj/malawi-rag-sql-chatbot/production_error.log --log-level info"
Restart=always
RestartSec=5
StandardOutput=append:/home/dj/malawi-rag-sql-chatbot/systemd_stdout.log
StandardError=append:/home/dj/malawi-rag-sql-chatbot/systemd_stderr.log
SyslogIdentifier=malawi-rag-sql-chatbot
Environment="PATH=/home/dj/miniconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable malawi-rag-sql-chatbot

# Start the service
sudo systemctl start malawi-rag-sql-chatbot

# Check status
sudo systemctl status malawi-rag-sql-chatbot
```

### 3. Managing the Service

Common commands for service management:

```bash
# Stop the service
sudo systemctl stop malawi-rag-sql-chatbot

# Restart the service
sudo systemctl restart malawi-rag-sql-chatbot

# View logs
sudo journalctl -u malawi-rag-sql-chatbot -f
```

### 4. Testing After Service Setup

Verify the application is running through systemd:

```bash
# Check if the port is in use
sudo lsof -i :5000

# Test the endpoint
curl -v http://localhost:5000/
```

## Integration with Nginx

When using systemd, update your Nginx configuration to proxy to the service:

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

## Modified Deployment Checklist

Add these steps to your main deployment plan:

1. Build frontend assets before deployment
2. Create and configure systemd service instead of using nohup
3. Test the application through the systemd service
4. If using both systemd and Nginx, ensure they work together properly 