#!/bin/bash

# Activate conda environment
source ~/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Set API key directly
export TOGETHER_API_KEY="f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101"

# Load other environment variables from .env
set -a
source .env
set +a

# Override API_PREFIX and PORT settings
export API_PREFIX="/api"
export PORT=5000

# Start the FastAPI application with Gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:5000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
