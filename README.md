# Absensi System API

Backend server untuk sistem absensi wajah berbasis kiosk. Dibangun dengan **FastAPI** dan **facenet-pytorch**.

## ✨ Fitur Utama

- **🎯 MTCNN Face Detection** - Deteksi wajah akurat dengan alignment otomatis
- **🧠 FaceNet Recognition** - Deep learning model untuk pengenalan wajah
- **📊 Attendance Logic** - Jam masuk, jam pulang, keterlambatan, dan cooldown
- **🔐 Admin Dashboard API** - CRUD karyawan, event log, dan laporan
- **📸 Snapshot Storage** - Simpan foto saat absensi (opsional)
- **🗄️ MySQL/SQLite** - Support dual database

## 📁 Struktur Folder

```
newApi/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Environment config
│   ├── recog.py         # MTCNN + FaceNet recognition
│   ├── models.py        # SQLAlchemy models
│   ├── admin_*.py       # Admin API endpoints
│   └── ...
├── scripts/             # Utilities (create_admin, full_reset)
├── data/snapshots/      # Attendance photos
├── logs/                # API logs
├── run_api.bat          # 1-click launcher
├── requirements.txt     # Dependencies
└── .env                 # Environment config (create from .env.example)
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
copy .env.example .env
# Edit .env - set SECRET_KEY and database
```

### 3. Run Server
```bash
# Option A: Double-click run_api.bat
# Option B: Manual
.\.venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Create Admin Account
```bash
python scripts/create_admin.py
```

## ⚙️ Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite or MySQL connection | sqlite:///./absensi.db |
| `SECRET_KEY` | JWT signing key (REQUIRED) | - |
| `MAX_DISTANCE` | Face match threshold | 0.85 |
| `MIN_FACE_PX` | Minimum face size | 80 |
| `COOLDOWN_SECONDS` | Between same-person scans | 45 |

## 🔧 Scripts

| Script | Description |
|--------|-------------|
| `scripts/create_admin.py` | Create admin account |
| `scripts/full_reset.py` | Factory reset (wipe all data) |
| `scripts/cleanup.py` | Remove old snapshots/logs |

---
*Backend for Absensi Desktop Kiosk Project*
