@echo off
set BASE_DIR=C:\Users\lfana\Documents\Kwantu\rag-sql-chatbot
cd /d %BASE_DIR%

:: Activate virtual environment
call %BASE_DIR%\.venv\Scripts\activate.bat

:: Set environment variables
set PYTHONPATH=%BASE_DIR%
set PYTHONUNBUFFERED=1

:: Start the server with hot reloading
%BASE_DIR%\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app --workers 1