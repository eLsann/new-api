# 🚀 Deploy API Absensi ke Render

## 📋 Persyaratan
- Akun GitHub (gratis)
- Akun Render (gratis)

## 🔧 Langkah Deploy

### 1. Push ke GitHub
```bash
git init
git add .
git commit -m "Initial commit - Absensi API"
git branch -M main
git remote add origin https://github.com/username/absensi-api.git
git push -u origin main
```

### 2. Setup di Render
1. Login ke [render.com](https://render.com)
2. Klik **"New +"** → **"Web Service"**
3. Connect ke GitHub repository
4. Konfigurasi:
   - **Name**: `absensi-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 3. Environment Variables
Tambahkan environment variables di Render dashboard:
```
DATABASE_URL=sqlite:///./absensi.db
DEVICE_TOKENS=stb-01:ISI_TOKEN_DEVICE_KAMU
SECRET_KEY=ini_kunci_rahasia_panjang_minimal_32_karakter_ubah_sendiri_123456
MAX_DISTANCE=0.95
MIN_FACE_PX=90
COOLDOWN_SECONDS=45
SAVE_SNAPSHOTS=true
SNAPSHOT_DIR=./data/snapshots
SNAPSHOT_ON_UNKNOWN=true
SNAPSHOT_ON_LOW_CONF=true
LOW_CONF_DISTANCE=0.85
ADMIN_TOKEN_EXPIRE_HOURS=12
```

### 4. Deploy
- Klik **"Create Web Service"**
- Tunggu proses build dan deploy (5-10 menit)
- API akan tersedia di: `https://absensi-api.onrender.com`

## 🔄 Update Desktop App
Update file `.env` di desktop app:
```bash
API_BASE=https://absensi-api.onrender.com
```

## ⚠️ Catatan Penting
- **Free tier** sleep setelah 15 menit tidak aktif
- **Cold start** 30-60 detik saat pertama kali request
- **SQLite database** akan reset setiap deploy (gunakan PostgreSQL untuk production)
- **File storage** bersifat sementara

## 🌟 Alternatif Hosting Gratis
- **Railway** - $5 kredit gratis per bulan
- **Fly.io** - Free tier dengan shared CPU
- **Vercel** - Tidak support Python backend
- **Netlify** - Tidak support Python backend
