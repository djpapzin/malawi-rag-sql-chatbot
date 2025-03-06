#!/bin/bash

# Activate conda environment
source ~/miniconda/bin/activate malawi-rag-sql-chatbot

# Load environment variables from .env
set -a
source .env
set +a

# Start the FastAPI application with Uvicorn in development mode
LOG_LEVEL=DEBUG uvicorn app.main:app \
    --host localhost \
    --port 5001 \
    --reload
