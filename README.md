# Project Absensi API (Final)

## Setup
Python 3.11
- buat venv
- install requirements
- copy .env.example -> .env

## Reset DB (dev recommended)
Hapus absensi.db jika ada perubahan skema besar.

## Create admin
python scripts/create_admin.py

## Enroll dataset awal
python scripts/enroll_from_folder.py dataset

## Run server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

## Auth admin (baru)
- POST /admin/login {username,password} -> token
- Gunakan header:
  Authorization: Bearer <token>