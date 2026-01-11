@echo off
REM Deploy to Laragon
REM ========================================

echo.
echo --- Absensi API Deployment ---
echo.

if not exist "C:\laragon" (
    echo ERROR: Laragon not found at C:\laragon
    pause
    exit /b 1
)

echo Laragon detected.

set PROJECT_DIR=C:\laragon\www\newApi
if not exist "%PROJECT_DIR%" (
    echo Creating project dir...
    mkdir "%PROJECT_DIR%"
) else (
    echo Project dir exists.
)

echo Copying files...
xcopy "%~dp0..\app" "%PROJECT_DIR%\app\" /E /I /Y /Q > nul
xcopy "%~dp0..\tests" "%PROJECT_DIR%\tests\" /E /I /Y /Q > nul
copy "%~dp0..\requirements.txt" "%PROJECT_DIR%\" /Y > nul
copy "%~dp0..\.env" "%PROJECT_DIR%\" /Y > nul
copy "%~dp0..\README.md" "%PROJECT_DIR%\" /Y > nul
echo Done.

echo Setting up virtualenv...
cd /d "%PROJECT_DIR%"
if not exist "venv" (
    python -m venv venv
)

echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

if not exist "logs" mkdir logs

echo.
echo --- Deployment Complete ---
echo Target: %PROJECT_DIR%
echo.
echo To run:
echo cd %PROJECT_DIR%
echo venv\Scripts\activate
echo python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause
