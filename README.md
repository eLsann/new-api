<p align="center">
  <h1 align="center">Absensi API</h1>
  <p align="center">
    <strong>Backend API untuk Sistem Absensi Berbasis Pengenalan Wajah</strong>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square" alt="Status">
</p>

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **MTCNN Detection** | Deteksi wajah akurat dengan face alignment otomatis |
| **FaceNet Recognition** | Deep learning model untuk pengenalan wajah (InceptionResnetV1) |
| **Attendance Logic** | Jam masuk, pulang, keterlambatan, cooldown |
| **JWT Authentication** | Endpoint admin aman dengan token |
| **Snapshot Storage** | Simpan foto absensi (opsional) |
| **Dual Database** | Support MySQL dan SQLite |

---

## Tech Stack

<table>
<tr>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"/><br>Python</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40"/><br>FastAPI</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg" width="40"/><br>PyTorch</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" width="40"/><br>MySQL</td>
<td align="center"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/opencv/opencv-original.svg" width="40"/><br>OpenCV</td>
</tr>
</table>

### Libraries

```
facenet-pytorch    # MTCNN + FaceNet untuk face recognition
fastapi            # Web framework API
uvicorn            # ASGI server
sqlalchemy         # ORM database
pymysql            # MySQL connector
python-jose        # JWT authentication
bcrypt             # Password hashing
```

---

## Quick Start

### Clone & Setup
```bash
git clone https://github.com/your-username/new-api.git
cd new-api
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment
```bash
copy .env.example .env
# Edit .env - wajib isi SECRET_KEY dan database
```

### Run Server
```bash
# Windows (1-click)
.\run_api.bat

# Manual
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Create Admin
```bash
python scripts/create_admin.py
```

---

##Struktur Project

```
newApi/
├── 📂 app/
│   ├── main.py           # FastAPI entry point
│   ├── recog.py          # MTCNN + FaceNet recognition
│   ├── config.py         # Environment config
│   ├── models.py         # SQLAlchemy models
│   └── admin_*.py        # Admin endpoints
├── 📂 scripts/
│   ├── create_admin.py   # Create admin account
│   ├── full_reset.py     # Factory reset
│   └── cleanup.py        # Clean old data
├── 📂 data/snapshots/    # Attendance photos
├── 📄 .env.example       # Environment template
├── 📄 requirements.txt   # Dependencies
└── 📄 run_api.bat        # 1-click launcher
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL/SQLite connection string | sqlite:///./absensi.db |
| `SECRET_KEY` | JWT signing key (**REQUIRED**) | - |
| `MAX_DISTANCE` | Face match threshold | 0.85 |
| `MIN_FACE_PX` | Minimum face size | 80 |
| `COOLDOWN_SECONDS` | Between same-person scans | 45 |

---

## API Documentation

Setelah server running, buka:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Scripts Utility

| Script | Fungsi |
|--------|--------|
| `scripts/create_admin.py` | Buat akun admin baru |
| `scripts/full_reset.py` | Factory reset (hapus semua data) |
| `scripts/cleanup.py` | Bersihkan snapshot & log lama |
| `scripts/generate_key.py` | Generate SECRET_KEY baru |

---

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <sub>elsann</sub>
</p>
