@echo off
title Launch CIBUS-AI Application
echo ===================================================
echo Launching CIBUS-AI Full System...
echo ===================================================
start "CIBUS-AI Backend (FastAPI)" cmd /c "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "CIBUS-AI Frontend (Vite)" cmd /c "%~dp0start_frontend.bat"
echo.
echo ===================================================
echo CIBUS-AI services launched successfully!
echo   Frontend : http://localhost:5173
echo   Backend  : http://127.0.0.1:8000
echo   API Docs : http://127.0.0.1:8000/docs
echo   Health   : http://127.0.0.1:8000/health
echo ===================================================
echo.
