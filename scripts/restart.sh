#!/bin/bash

# Stop any running instances
echo "Stopping any running instances of the application..."
pkill -f "python.*app/main.py" || true

# Wait for processes to terminate
echo "Waiting for processes to terminate..."
sleep 2

# Start the application
echo "Starting application..."
echo "Using Python: $CONDA_PREFIX/bin/python"

# Check SSL certificates
CERT_PATH="/etc/letsencrypt/live/dziwani.kwantu.support/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/dziwani.kwantu.support/privkey.pem"

if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
    echo "SSL certificates not found. Running without SSL..."
    nohup $CONDA_PREFIX/bin/python app/main.py > /dev/null 2>&1 &
else
    echo "SSL certificates found. Running with HTTPS..."
    nohup $CONDA_PREFIX/bin/python app/main.py > /dev/null 2>&1 &
fi

# Get the process ID
PID=$!
echo "Started application on port 5000"
echo "Process ID: $PID"
echo "Using Python: $CONDA_PREFIX/bin/python"
echo "Application restart completed!" 