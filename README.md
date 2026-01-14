# Absensi API

Backend API untuk sistem absensi berbasis pengenalan wajah.

## Fitur

- Pengenalan wajah dengan DeepFace (ArcFace)
- Absensi masuk/pulang otomatis
- Deteksi keterlambatan (jam masuk > 08:00)
- Jam pulang terbatas (14:00 - 16:00)
- Admin dashboard dengan JWT authentication
- Export laporan CSV

## Instalasi

```bash
# Clone repository
git clone <repo-url>
cd newApi

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env sesuai kebutuhan
```

## Konfigurasi (.env)

```env
APP_NAME=Absensi API
DATABASE_URL=sqlite:///./absensi.db
SECRET_KEY=your-secret-key-here
DEVICE_TOKENS=stb-01:token123,stb-02:token456
```

## Menjalankan

```bash
# Development
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Device (Kiosk)
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/v1/recognize` | Pengenalan wajah |

### Admin
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/admin/login` | Login admin |
| GET | `/admin/persons` | Daftar karyawan |
| POST | `/admin/persons` | Tambah karyawan |
| DELETE | `/admin/persons/{id}` | Hapus karyawan |
| POST | `/admin/persons/{id}/enroll` | Upload foto wajah |
| GET | `/admin/events` | Log absensi |
| POST | `/admin/rebuild_cache` | Rebuild cache wajah |
| POST | `/admin/reset_attendance` | Reset data absensi |
| GET | `/admin/reports/monthly` | Laporan bulanan |
| GET | `/admin/reports/export/csv` | Export CSV |

## Struktur Database

- `persons` - Data karyawan
- `embeddings` - Vektor wajah
- `attendance_events` - Log absensi
- `daily_attendance` - Rekap harian
- `admins` - Admin users

## Teknologi

- FastAPI
- SQLite/SQLAlchemy
- DeepFace (ArcFace)
- JWT Authentication
- bcrypt