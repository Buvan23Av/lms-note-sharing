@echo off
echo ==========================================
echo Ingesting XML Data into MongoDB and Neo4j
echo ==========================================
cd /d "%~dp0backend"

echo Checking Python dependencies...
python -m pip install -r requirements.txt

echo.
echo Running XML Importer...
python -m scripts.init_mongodb
pause
