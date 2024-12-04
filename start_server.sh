#!/bin/bash

# Activate virtual environment
source .venv/Scripts/activate

# Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
