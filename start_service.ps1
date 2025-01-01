cd "C:\Users\lfana\Documents\Kwantu\rag-sql-chatbot"
Write-Host "Activating virtual environment..."
try {
    .\.venv\Scripts\activate
} catch {
    Write-Host "Error activating virtual environment: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Upgrading pip..."
try {
    python -m pip install --upgrade pip
} catch {
    Write-Host "Error upgrading pip: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Installing requirements..."
try {
    pip install -r requirements.txt
} catch {
    Write-Host "Error installing requirements: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Starting service..."
try {
    uvicorn app:app --host 127.0.0.1 --port 8001 --reload
} catch {
    Write-Host "Error starting service: $_" -ForegroundColor Red
    exit 1
}
