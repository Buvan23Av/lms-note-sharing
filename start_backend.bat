@echo off
echo ==========================================
echo Starting LMS FastAPI Backend Server
echo ==========================================
cd /d "%~dp0backend"
echo Server will run on: http://localhost:8000
echo Swagger UI docs at: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --port 8000
pause
