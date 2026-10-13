@echo off
echo ==========================================
echo Pushing LMS Project to GitHub...
echo ==========================================
cd /d "%~dp0"
echo Current Directory: %CD%
echo Remote URL:
git remote -v
echo.
echo Pushing to branch 'main'...
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo SUCCESS! Your code is now live on GitHub:
    echo https://github.com/Buvan23Av/lms-note-sharing
    echo ==========================================
) else (
    echo.
    echo If a browser window opened, complete your GitHub sign-in.
    echo If this failed, check your internet connection or GitHub permissions.
)
pause
