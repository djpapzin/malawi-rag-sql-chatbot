#!/bin/bash

# Stop any existing server
pkill -f "gunicorn app.main:app" || true
echo "Stopping existing server..."
sleep 2

# Change to the project directory
cd /home/dj/malawi-rag-sql-chatbot

# Activate conda environment
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Start the server with nohup and increased timeout
nohup gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --access-logfile server_access.log --error-logfile server_error.log --log-level info --timeout 120 > nohup.out 2>&1 &

# Get the process ID
PID=$!

# Print confirmation
echo "Server started on port 5000"
echo "Process ID: $PID" 