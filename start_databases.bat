@echo off
echo ==========================================
echo Starting MongoDB and Neo4j Containers...
echo ==========================================
cd /d "%~dp0"
docker compose up -d
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Containers started successfully!
    echo Neo4j Browser: http://localhost:7474
    echo Neo4j Username: neo4j
    echo Neo4j Password: password123
    echo MongoDB Port: 27017
) else (
    echo.
    echo Docker compose failed or Docker is not running.
    echo If you have local MongoDB/Neo4j services installed, ensure they are started.
)
pause
