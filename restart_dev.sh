#!/bin/bash

echo "Stopping any running development instances of the application..."
pkill -f "uvicorn app.main:app --host localhost --port 5001" || echo "No running development instances found"

echo "Waiting for processes to terminate..."
sleep 3

echo "Starting development application on port 5001..."
bash ./run_development.sh &

echo "Development application restart completed!"
echo "You can access the development server at: http://localhost:5001"
