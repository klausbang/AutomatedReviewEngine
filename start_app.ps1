# PowerShell Startup Script for Automated Review Engine v1.0.0

Write-Host "=== Starting Automated Review Engine v1.0.0 ===" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location "c:\Users\AU000NK6\OneDrive - WSA\Documents\Python\AutomatedReviewEngine"

Write-Host "Project Directory: $(Get-Location)" -ForegroundColor Yellow

# Set execution policy for current session
Write-Host "Setting execution policy..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Write-Host ""
Write-Host "Starting Streamlit application..." -ForegroundColor Yellow
Write-Host "Open your browser to: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

# Run using the virtual environment Python
try {
    & ".\.venv\Scripts\python.exe" -m streamlit run app.py
} catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running manually:" -ForegroundColor Yellow
    Write-Host ".\.venv\Scripts\python.exe -m streamlit run app.py" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
