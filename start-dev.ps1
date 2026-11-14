# Startup Script for Budget Intelligence Platform (Windows PowerShell)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting Budget Intelligence Platform" -ForegroundColor Cyan
Write-Host "  Location: $ScriptDir" -ForegroundColor DarkGray
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Backend in separate window with correct working directory
Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "$ScriptDir\backend" -ArgumentList "-NoExit", "-Command", "Write-Host '=========================================' -ForegroundColor Cyan; Write-Host '  FastAPI Budget Backend Server' -ForegroundColor Cyan; Write-Host '  API Docs: http://localhost:8000/docs' -ForegroundColor Cyan; Write-Host '=========================================' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start Frontend in separate window with correct working directory
Write-Host "`n[2/2] Starting React + Vite Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory "$ScriptDir\frontend" -ArgumentList "-NoExit", "-Command", "Write-Host '=========================================' -ForegroundColor Cyan; Write-Host '  Vite React Frontend Server' -ForegroundColor Cyan; Write-Host '  App URL: http://localhost:3000' -ForegroundColor Cyan; Write-Host '=========================================' -ForegroundColor Cyan; npm run dev"

Write-Host "`nBoth servers have been launched in separate terminal windows!" -ForegroundColor Green
Write-Host "• Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "• Backend API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "• Keep both windows open while using the platform." -ForegroundColor DarkGray
