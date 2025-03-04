#!/bin/bash

# Load environment variables
source ~/miniconda/etc/profile.d/conda.sh

# Activate conda environment
conda activate malawi-rag-sql-chatbot

# Kill any existing process
pkill -f "gunicorn app.main:app"

# Start the application
cd /home/dj/malawi-rag-sql-chatbot
PYTHON_PATH=$(which python)
nohup $PYTHON_PATH -m gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000 \
    --access-logfile server_access.log \
    --error-logfile server_error.log \
    --log-level info \
    --timeout 120 \
    > nohup.out 2>&1 &

# Print process information
echo "Started application on port 5000"
echo "Process ID: $!"
echo "Using Python: $PYTHON_PATH" 