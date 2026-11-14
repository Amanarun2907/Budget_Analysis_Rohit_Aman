@echo off
cd /d "%~dp0"
echo ==========================================================
echo   Budget Intelligence Platform - AI Budget Analysis
echo ==========================================================
echo.

echo [1/2] Starting FastAPI Backend (AI Analysis Engine) on port 8000...
start "Budget Backend - Port 8000" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo [2/2] Starting React + Vite Frontend on port 3000...
start "Budget Frontend - Port 3000" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ==========================================================
echo   Both servers launched successfully!
echo ==========================================================
echo.
echo   Frontend:    http://localhost:3000
echo   Backend API: http://127.0.0.1:8000
echo   API Docs:    http://127.0.0.1:8000/docs
echo   Health:      http://127.0.0.1:8000/api/health
echo.
echo   >> IMPORTANT: Keep BOTH terminal windows open!
echo   >> Open http://localhost:3000 in your browser.
echo.
timeout /t 5 /nobreak >nul
start "" "http://localhost:3000"
