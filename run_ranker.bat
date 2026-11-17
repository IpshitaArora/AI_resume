@echo off
:: This navigates to the folder where the .bat file is located
cd /d "%~dp0"

echo ==========================================
echo   AI RESUME RANKER - SYSTEM STARTING
echo ==========================================
echo Training on 2500 resumes (if not cached)...
echo.

:: Runs streamlit as a python module (most stable way on Windows)
python -m streamlit run app.py

:: If something goes wrong, the window stays open so you can see why
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The app failed to start. 
    echo Please check if Streamlit is installed.
    pause
)