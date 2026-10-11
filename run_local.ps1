# SipSense AI - Local Development Runner
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting SipSense AI Development Environment" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$VENV_PY = "D:\Development\AI_Projects\SipSenseAI\.venv\Scripts\python.exe"
$INSTANCE = "sipsense-ai-demo:asia-south1:sipsense-pg"
$SA_KEY = "D:\Development\AI_Projects\SipSenseAI\sa-key.json"

# Check if proxy is already running on port 5432
$portActive = Get-NetTCPConnection -LocalPort 5432 -ErrorAction SilentlyContinue
if (-not $portActive) {
    Write-Host "[1/2] Starting Cloud SQL Auth Proxy..." -ForegroundColor Yellow
    Start-Process -FilePath ".\cloud-sql-proxy.exe" -ArgumentList "--credentials-file `"$SA_KEY`" $INSTANCE --port 5432" -NoNewWindow
    Start-Sleep -Seconds 3
} else {
    Write-Host "[1/2] Cloud SQL Auth Proxy already listening on 127.0.0.1:5432." -ForegroundColor Green
}

Write-Host "[2/2] Launching FastAPI Web Application..." -ForegroundColor Yellow
Write-Host "Access UI at:   http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Swagger Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green

& $VENV_PY -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
