@echo off
title Skill Gap Navigator
echo ========================================
echo   Skill Gap Navigator - Starting...
echo ========================================
echo.

echo [1/2] Starting Backend (port 8000)...
start "Backend" cmd /c "cd /d D:\KAI-LLM\java project\backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo [2/2] Starting Frontend (port 5174)...
start "Frontend" cmd /c "cd /d D:\KAI-LLM\java project\frontend && python serve_dist.py"

echo.
echo Waiting for servers to start...
timeout /t 4 /nobreak > nul

echo.
echo ========================================
echo   Both servers starting!
echo.
echo   Frontend: http://localhost:5174
echo   Backend:  http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to open the app in your browser...
pause > nul

start http://localhost:5174
