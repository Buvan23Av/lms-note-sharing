@echo off
echo ==========================================
echo Starting LMS FastAPI Backend Server
echo ==========================================
cd /d "%~dp0backend"
echo Server will run on: http://127.0.0.1:8000
echo Swagger UI docs at: http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
