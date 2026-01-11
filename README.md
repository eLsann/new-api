# Project Absensi API

## Setup
Python 3.11
- buat venv
- install requirements
- copy .env.example -> .env

## Absensi API (FastAPI + MySQL)

Sistem Absensi Wajah Berbasis API dengan FastAPI, Facenet-PyTorch, dan MySQL.

## Struktur Project 
```
newApi/
├── app/                  # Source Code API
│   ├── main.py           # Entry point
│   ├── models.py         # Database Models
│   └── ...
├── data/                 # Folder data (Snapshots wajah)
├── deploy/               # Script Deployment
│   └── deploy_to_laragon.bat
├── logs/                 # File Log Aplikasi
├── tests/                # Unit Tests
└── _archive/             # File lama/backup (tidak dipakai)
```

## Deployment (Laragon) 
1. Pastikan **Laragon** sudah terinstall dengan **MySQL 8.0+** dan **Python 3.10+**.
2. Jalankan script deployment otomatis:
   ```cmd
   deploy\deploy_to_laragon.bat
   ```
3. Script akan otomatis:
   - Membuat folder di `C:\laragon\www\newApi`
   - Copy file project
   - Setup Virtual Environment & Install Dependencies
4. Setelah selesai, buka terminal di folder tujuan:
   ```cmd
   cd C:\laragon\www\newApi
   venv\Scripts\activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Fitur 
- **Rekognisi Wajah**: Menggunakan Facenet (InceptionResnetV1).
- **Anti-Spoofing**: (Basic) Threshold distance check.
- **Reporting**: API untuk log absensi harian dan event.
- **Security**: JWT Authentication untuk Admin.

## Dokumentasi API 
Akses Swagger UI di: **http://localhost:8000/docs**

## Auth admin (baru)
- POST /admin/login {username,password} -> token
- Gunakan header:
  Authorization: Bearer <token>
