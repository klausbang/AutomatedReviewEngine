@echo off
echo Starting Minimal Automated Review Engine v1.0.0...
cd /d "c:\Users\AU000NK6\OneDrive - WSA\Documents\Python\AutomatedReviewEngine"
echo.
echo Starting minimal application for testing...
echo Open your browser to: http://localhost:8502
echo.
"C:\Users\AU000NK6\OneDrive - WSA\Documents\Python\AutomatedReviewEngine\.venv\Scripts\python.exe" -m streamlit run app_minimal.py --server.port 8502
pause
