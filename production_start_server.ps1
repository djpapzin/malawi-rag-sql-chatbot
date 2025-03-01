# Production start script for Malawi RAG SQL Chatbot (PowerShell version)
# This script ensures the app runs on port 5000

# Navigate to the application directory
cd C:\path\to\malawi-rag-sql-chatbot

# Activate conda environment 
# Note: Assuming conda is available in PATH
conda activate malawi-rag-sql-chatbot

# Stop any existing processes (if running on Windows)
Get-Process | Where-Object {$_.ProcessName -like "*gunicorn*"} | Stop-Process -Force

# Start the server
# For Windows, we typically use a different approach than nohup
# Using Start-Process to run in background
$env:PYTHONPATH = "C:\path\to\malawi-rag-sql-chatbot"

Start-Process -FilePath "gunicorn" -ArgumentList @(
    "app.main:app",
    "--workers", "4",
    "--worker-class", "uvicorn.workers.UvicornWorker",
    "--bind", "0.0.0.0:5000",
    "--timeout", "120",
    "--access-logfile", "production_access.log",
    "--error-logfile", "production_error.log",
    "--log-level", "info"
) -NoNewWindow

# Display a message
Write-Host "Production server started on port 5000"
Write-Host "Check logs in production_access.log and production_error.log"
Write-Host "Test with: Invoke-RestMethod -Uri 'http://154.0.164.254:5000/'"

# Display running processes
Get-Process | Where-Object {$_.ProcessName -like "*gunicorn*"} 