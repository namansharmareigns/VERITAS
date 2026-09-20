#!/usr/bin/env pwsh
# VERITAS development startup script (Windows PowerShell)

Write-Host "VERITAS Development Setup" -ForegroundColor Cyan

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"

# Backend
Write-Host "`nStarting backend..." -ForegroundColor Yellow
Push-Location $backendDir
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating Python venv..." -ForegroundColor Gray
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
}
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}
Write-Host "Creating indexes and seeding data..." -ForegroundColor Gray
python scripts/indexes.py
python scripts/seed.py
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000"
Pop-Location

# Frontend
Write-Host "`nStarting frontend..." -ForegroundColor Yellow
Push-Location $frontendDir
if (-not (Test-Path "node_modules")) { npm install }
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev"
Pop-Location

Write-Host "`nVERITAS running:" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173"
Write-Host "  Backend:  http://localhost:8000/docs"
Write-Host "  Health:   http://localhost:8000/api/health"
