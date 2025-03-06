#!/bin/bash

# This script deploys changes to production
# It creates a production-ready version of the application
# and updates the production server

# Exit on error
set -e

echo "=== Starting deployment to production ==="

# 1. Define paths
REPO_DIR="/home/dj/malawi-rag-sql-chatbot"
PROD_DIR="/var/www/dziwani.kwantu.support"

# 2. Check if we have sudo access to create production directory
if [ ! -d "$PROD_DIR" ]; then
  echo "Production directory doesn't exist. Checking if we can create it..."
  if sudo -n true 2>/dev/null; then
    echo "Creating production directory..."
    sudo mkdir -p "$PROD_DIR"
    sudo chown $(whoami):$(whoami) "$PROD_DIR"
  else
    # Alternative approach if we don't have sudo access
    echo "No sudo access. Using alternative production directory..."
    PROD_DIR="/home/dj/production/dziwani.kwantu.support"
    mkdir -p "$PROD_DIR"
  fi
fi

# 3. Copy files to production directory
echo "Copying files to production directory..."
rsync -av --exclude '.git' --exclude '.env' --exclude '__pycache__' \
  --exclude '*.pyc' --exclude 'logs' --exclude 'app.log' \
  --exclude 'server.log' --exclude 'server_access.log' \
  --exclude 'server_error.log' --exclude 'nohup.out' \
  "$REPO_DIR/" "$PROD_DIR/"

# 4. Copy environment file with production settings
echo "Setting up production environment..."
cp "$REPO_DIR/.env" "$PROD_DIR/.env"

# 5. Update Nginx configuration if needed and if we have access
if command -v nginx >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  echo "Checking Nginx configuration..."
  NGINX_CONF="/etc/nginx/sites-available/dziwani.kwantu.support.conf"
  
  if [ -f "$NGINX_CONF" ]; then
    if ! diff -q "$REPO_DIR/production_nginx.conf" "$NGINX_CONF" > /dev/null; then
      echo "Updating Nginx configuration..."
      sudo cp "$REPO_DIR/production_nginx.conf" "$NGINX_CONF"
      sudo nginx -t && sudo systemctl reload nginx
    fi
  else
    echo "Nginx configuration file doesn't exist at $NGINX_CONF"
    echo "You may need to manually set up the Nginx configuration."
  fi
else
  echo "Skipping Nginx configuration update (no nginx command or sudo access)"
fi

# 6. Restart the production service
echo "Restarting production service..."
cd "$PROD_DIR"
bash ./production_start_server.sh

echo "=== Deployment to production completed ==="
echo "Your changes are now live at https://dziwani.kwantu.support/"
echo "You can verify with: curl -X GET https://dziwani.kwantu.support/api/rag-sql-chatbot/health"
