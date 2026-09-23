@echo off
title CIBUS-AI React Frontend Server
echo ===================================================
echo Starting CIBUS-AI React/Vite Frontend (port 5173)...
echo ===================================================
cd /d "%~dp0frontend"
npm run dev
pause
