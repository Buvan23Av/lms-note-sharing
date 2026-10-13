@echo off
echo ==========================================
echo Starting LMS React Vite Frontend Server
echo ==========================================
cd /d "%~dp0frontend"
echo Frontend will run on: http://localhost:5173
echo Backend API proxy:    http://localhost:8000
echo.
call npm.cmd run dev
pause
