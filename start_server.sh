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