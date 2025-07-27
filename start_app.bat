@echo off
echo Starting Automated Review Engine v1.0.0...
cd /d "c:\Users\AU000NK6\OneDrive - WSA\Documents\Python\AutomatedReviewEngine"
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo.
echo Starting Streamlit application...
echo Open your browser to: http://localhost:8501
echo.
streamlit run app.py
pause
