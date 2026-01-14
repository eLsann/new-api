# Absensi API

REST API untuk sistem absensi berbasis pengenalan wajah.

## Persyaratan

- Python 3.10+
- SQLite (default) atau MySQL

## Instalasi

```bash
# Clone dan masuk direktori
git clone <repo-url>
cd newApi

# Buat virtual environment
python -m venv .venv

# Aktivasi (Windows)
.venv\Scripts\activate

# Aktivasi (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Konfigurasi

Salin file `.env.example` ke `.env` dan sesuaikan:

```bash
cp .env.example .env
```

Parameter yang perlu dikonfigurasi:
- `SECRET_KEY` - Kunci rahasia untuk JWT
- `DATABASE_URL` - Koneksi database
- `DEVICE_TOKENS` - Token autentikasi perangkat kiosk

## Menjalankan Server

```bash
# Development
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Dokumentasi API

Setelah server berjalan, akses dokumentasi interaktif di:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Struktur Project

```
newApi/
├── app/
│   ├── main.py           # Entry point
│   ├── config.py         # Konfigurasi
│   ├── models.py         # Model database
│   ├── database.py       # Koneksi database
│   ├── recog.py          # Pengenalan wajah
│   ├── attendance.py     # Logika absensi
│   ├── admin_auth.py     # Autentikasi admin
│   ├── admin_people.py   # CRUD karyawan
│   ├── admin_logs.py     # Log absensi
│   └── admin_reports.py  # Laporan
├── data/                 # Direktori data
├── logs/                 # Log aplikasi
├── .env.example          # Template konfigurasi
└── requirements.txt      # Dependencies
```

## Membuat Admin

```bash
python create_admin.py
```

Ikuti instruksi untuk membuat akun admin pertama.

## Teknologi

- FastAPI
- SQLAlchemy
- DeepFace
- PyJWT
- bcrypt
