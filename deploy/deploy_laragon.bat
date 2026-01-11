@echo off
REM Laragon Deployment Script for Absensi API
REM Run this script in the project folder inside C:\laragon\www\absensi-api

echo ========================================
echo   ABSENSI API - LARAGON DEPLOYMENT
echo ========================================
echo.

REM Change to script directory
cd /d %~dp0

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/6] Creating virtual environment...
    python -m venv venv
    echo   ✓ Virtual environment created
) else (
    echo [1/6] Virtual environment already exists
)

echo.
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo   ✓ Virtual environment activated

echo.
echo [3/6] Installing dependencies...
pip install -r requirements.txt --quiet
echo   ✓ Dependencies installed

echo.
echo [4/6] Checking .env configuration...
if not exist ".env" (
    echo   WARNING: .env file not found!
    echo   Please create .env from .env.example and configure it
    pause
    exit /b 1
)
echo   ✓ .env file exists

echo.
echo [5/6] Creating MySQL database tables...
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('  ✓ Tables created successfully')"
if errorlevel 1 (
    echo   ✗ Failed to create tables
    echo   Please check your DATABASE_URL in .env
    pause
    exit /b 1
)

echo.
echo [6/6] Testing API health...
start /b python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > nul 2>&1
timeout /t 3 /nobreak > nul
curl -s http://localhost:8000/health > nul
if errorlevel 1 (
    echo   WARNING: Could not verify API health
    echo   The API might still work, check manually
) else (
    echo   ✓ API is running
)

echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo API is running at: http://localhost:8000
echo Health check: http://localhost:8000/health
echo.
echo To access via domain, configure Nginx/Apache
echo.
echo Press any key to keep API running or Ctrl+C to stop...
pause > nul

REM Keep the API running
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
