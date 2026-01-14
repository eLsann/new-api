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

<<<<<<< HEAD
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
=======
## Struktur Project 
>>>>>>> da24b9da029b10b44bb76a5bcf3832fab7db7845

## Struktur Database

- `persons` - Data karyawan
- `embeddings` - Vektor wajah
- `attendance_events` - Log absensi
- `daily_attendance` - Rekap harian
- `admins` - Admin users

## Teknologi

<<<<<<< HEAD
- FastAPI
- SQLite/SQLAlchemy
- DeepFace (ArcFace)
- JWT Authentication
- bcrypt
=======
Untuk MySQL, ubah `DATABASE_URL` di `.env`:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/absensi_db
```

## Fitur 

- **Rekognisi Wajah**: Menggunakan Facenet (InceptionResnetV1)
- **Anti-Spam**: Cooldown mechanism
- **Reporting**: API untuk log absensi harian
- **Security**: JWT Authentication untuk Admin

## Dokumentasi API 

Akses Swagger UI di: **http://localhost:8000/docs**

## Auth Admin

```
POST /admin/login {"username", "password"} -> token
Header: Authorization: Bearer <token>
```
>>>>>>> da24b9da029b10b44bb76a5bcf3832fab7db7845
