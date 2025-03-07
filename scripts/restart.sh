#!/bin/bash

# Stop any running instances
echo "Stopping any running instances of the application..."
pkill -f "gunicorn app.main:app"

# Wait for processes to terminate
echo "Waiting for processes to terminate..."
sleep 2

# Start the application
echo "Starting application..."
PORT=5000
PYTHON_PATH=/home/dj/miniconda/envs/malawi-rag-sql-chatbot/bin/python
echo "Using Python: $PYTHON_PATH"

# Start gunicorn with the new port
$PYTHON_PATH -m gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000 \
    --access-logfile server_access.log \
    --error-logfile server_error.log \
    --log-level info \
    --timeout 120 &

# Get the process ID
PID=$!
echo "Started application on port 5000"
echo "Process ID: $PID"
echo "Using Python: $PYTHON_PATH"
echo "Application restart completed!" 