@echo off
setlocal EnableDelayedExpansion

echo Testing RAG SQL Chatbot API
echo ===========================

:: Set base URL
set "BASE_URL=http://localhost:8000"

echo.
echo Test 1: Multiple Projects Query
echo ------------------------------
curl -X POST ^
  "%BASE_URL%/query" ^
  -H "Content-Type: application/json" ^
  -H "Accept: application/json" ^
  -d "{\"message\": \"Show me all infrastructure projects in Malawi\"}" ^
  -w "\nStatus: %%{http_code}\n"

timeout /t 2 > nul

echo.
echo Test 2: Education Projects Query
echo ------------------------------
curl -X POST ^
  "%BASE_URL%/query" ^
  -H "Content-Type: application/json" ^
  -H "Accept: application/json" ^
  -d "{\"message\": \"List all education projects\"}" ^
  -w "\nStatus: %%{http_code}\n"

timeout /t 2 > nul

echo.
echo Test 3: Specific Project Details
echo ------------------------------
curl -X POST ^
  "%BASE_URL%/query" ^
  -H "Content-Type: application/json" ^
  -H "Accept: application/json" ^
  -d "{\"message\": \"Tell me about the Staff House project\"}" ^
  -w "\nStatus: %%{http_code}\n"

timeout /t 2 > nul

echo.
echo Test 4: Russian Language Support
echo ------------------------------
curl -X POST ^
  "%BASE_URL%/query" ^
  -H "Content-Type: application/json" ^
  -H "Accept: application/json" ^
  -d "{\"message\": \"Покажите инфраструктурные проекты в Малави\", \"language\": \"ru\"}" ^
  -w "\nStatus: %%{http_code}\n"

echo.
echo Tests completed
echo ===========================
