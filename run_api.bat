@echo off
title Absensi API Server
cls

echo ==================================================
echo   ABSENSI API SERVER - LAUNCHER
echo ==================================================
echo.

if not exist ".venv" (
    echo [ERROR] Virtual environment '.venv' tidak ditemukan!
    echo Silakan install dulu dengan: python -m venv .venv
    pause
    exit /b
)

echo [INFO] Mengaktifkan virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Menjalankan server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
