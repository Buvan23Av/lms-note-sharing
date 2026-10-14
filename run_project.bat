@echo off
echo ===================================================
echo Starting LMS Multi-Database System (Backend + UI)
echo ===================================================
cd /d "%~dp0"

echo [1/3] Ensuring Database Containers are running...
docker compose up -d

echo [2/3] Starting FastAPI Backend on Port 8000...
start "LMS Backend (Port 8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Waiting for Backend to initialize...
timeout /t 4 /nobreak >nul

echo [3/3] Starting React Frontend on Port 5173...
start "LMS Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm.cmd run dev"

echo Waiting for Frontend to start...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ===================================================
echo   PROJECT LAUNCHED SUCCESSFULLY!
echo ===================================================
echo   - Frontend UI:     http://localhost:5173
echo   - Backend Swagger: http://127.0.0.1:8000/docs
echo   - Neo4j Visualizer: http://localhost:7474
echo.
echo   NOTE: Keep the two popup terminal windows open!
echo   (Closing a window stops that server).
echo ===================================================
pause
