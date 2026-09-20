# Start VERITAS locally (MongoDB + backend + frontend)
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host "=== VERITAS Local Start ===" -ForegroundColor Cyan

# MongoDB via Docker Compose
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Starting MongoDB (docker compose)..." -ForegroundColor Yellow
    docker compose up -d mongodb 2>&1 | Out-Host
    Start-Sleep -Seconds 4
} else {
    Write-Host "Docker not found. Ensure MongoDB runs on localhost:27017 or set MONGODB_URI." -ForegroundColor Yellow
}

$py = Join-Path $Root "backend\venv\Scripts\python.exe"
if (Test-Path $py) {
    Write-Host "Indexing and seeding..." -ForegroundColor Yellow
    Push-Location (Join-Path $Root "backend")
    & $py scripts\indexes.py
    & $py scripts\seed.py
    Pop-Location
}

Write-Host "`nStart these in separate terminals if not already running:" -ForegroundColor Green
Write-Host "  Backend:  cd backend; .\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"
Write-Host "  Frontend: cd frontend; npm run dev"
Write-Host "`nURLs:"
Write-Host "  App:     http://127.0.0.1:5173"
Write-Host "  API:     http://127.0.0.1:8000/docs"
Write-Host "  Health:  http://127.0.0.1:8000/api/health"
