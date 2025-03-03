#!/bin/bash

echo "Stopping any running instances of the application..."
pkill -f "gunicorn app.main:app" || echo "No running instances found"

echo "Waiting for processes to terminate..."
sleep 3

echo "Starting application..."
bash ./start_production.sh

echo "Application restart completed!" 