# Project Absensi API

## Setup

**Requirements:** Python 3.10+

```bash
# 1. Buat virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy dan edit konfigurasi
copy .env.example .env
# Edit SECRET_KEY di file .env

# 4. Jalankan API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Buat akun admin
python create_admin.py
```

## Absensi API (FastAPI + SQLite)

Sistem Absensi Wajah Berbasis API dengan FastAPI, Facenet-PyTorch, dan SQLite.

## Struktur Project 📂

```
newApi/
├── app/                  # Source Code API
│   ├── main.py           # Entry point
│   ├── models.py         # Database Models
│   └── ...
├── data/                 # Folder data (Snapshots wajah)
├── tests/                # Unit Tests
└── _archive/             # File lama/backup
```

## Database

Menggunakan **SQLite** (default). Database otomatis dibuat di `absensi.db`.

Untuk MySQL, ubah `DATABASE_URL` di `.env`:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/absensi_db
```

## Fitur ✨

- **Rekognisi Wajah**: Menggunakan Facenet (InceptionResnetV1)
- **Anti-Spam**: Cooldown mechanism
- **Reporting**: API untuk log absensi harian
- **Security**: JWT Authentication untuk Admin

## Dokumentasi API 📖

Akses Swagger UI di: **http://localhost:8000/docs**

## Auth Admin

```
POST /admin/login {"username", "password"} -> token
Header: Authorization: Bearer <token>
```