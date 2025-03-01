#!/bin/bash

# Production start script for Malawi RAG SQL Chatbot
# This script ensures the app runs on port 5000 with nohup

# Change to the application directory
cd /home/dj/malawi-rag-sql-chatbot

# Activate conda environment
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Stop any existing instances
pkill -f "gunicorn app.main:app"

# Start the server with nohup on port 5000
nohup gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile production_access.log \
    --error-logfile production_error.log \
    --log-level info > nohup.out 2>&1 &

# Display a message
echo "Production server started on port 5000"
echo "Check logs with: tail -f nohup.out"
echo "Test with: curl -v http://154.0.164.254:5000/"

# Display process info
echo "Server process information:"
ps -ef | grep gunicorn | grep -v grep 