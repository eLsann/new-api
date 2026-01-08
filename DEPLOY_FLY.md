# 🚀 Deploy ke Fly.io

## 📋 Persyaratan
- Akun Fly.io (gratis $5 credit/bulan)
- Fly CLI terinstall
- Akun GitHub

## 🔧 Langkah 1: Install Fly CLI

### Windows:
```bash
# Menggunakan PowerShell
iwr https://fly.io/install.ps1 -useb | iex

# Atau download manual dari https://fly.io/docs/hands-on/install-flyctl/
```

### Verifikasi Install:
```bash
flyctl version
```

## 🔐 Langkah 2: Login ke Fly.io
```bash
flyctl auth login
# Akan membuka browser untuk login
```

## 🚀 Langkah 3: Deploy

### Option A: Deploy dari GitHub (Recommended)
```bash
# 1. Push code ke GitHub (sudah dilakukan)
git add .
git commit -m "Add Fly.io configuration"
git push origin main

# 2. Launch dari GitHub
flyctl launch --from-git https://github.com/eLsann/new-api.git
```

### Option B: Deploy Local
```bash
# 1. Launch aplikasi baru
flyctl launch

# 2. Konfirmasi settings:
# - App name: absensi-api (atau custom)
# - Region: singapore (atau terdekat)
# - Deploy: Yes

# 3. Deploy
flyctl deploy
```

## ⚙️ Konfigurasi Otomatis
File `fly.toml` sudah disetup dengan:
- **Port**: 8080 (internal) → 80/443 (external)
- **Health Check**: `/health` endpoint
- **Persistent Storage**: 1GB untuk database & snapshots
- **Environment Variables**: Semua config API
- **Auto-restart**: Pada failure

## 🌐 URL Production
Setelah deploy, API akan tersedia di:
```
https://absensi-api.fly.dev
```

## 💰 Biaya
- **$5 free credit** per bulan
- **Estimasi usage**: ~$2-3/bulan untuk API dengan ML
- **Shared CPU**: 256MB RAM, 1 CPU share
- **Storage**: 1GB included (untuk SQLite + snapshots)

## 📊 Monitoring
```bash
# Lihat logs real-time
flyctl logs

# Monitoring status
flyctl status

# Lihat metrics
flyctl monitor
```

## 🔄 Update Desktop App
Update file `.env` di desktop app:
```bash
API_BASE=https://absensi-api.fly.dev
```

## 🛠️ Commands Penting

### Deploy Update:
```bash
flyctl deploy
```

### Scale Resources:
```bash
# Upgrade ke dedicated CPU
flyctl scale vm shared-cpu-1x

# Add more RAM
flyctl scale memory 512
```

### Database Management:
```bash
# Connect ke machine untuk database access
flyctl ssh console

# Backup database
flyctl ssh console -C "cp /app/data/absensi.db /app/data/backup.db"
```

### Custom Domain:
```bash
# Add custom domain
flyctl certs add yourdomain.com

# Point DNS ke CNAME: your-app.fly.dev
```

## ⚡ Keunggulan Fly.io
- ✅ **Always online** (tidak seperti Render yang sleep)
- ✅ **Global CDN** untuk fast response
- ✅ **Auto HTTPS** dan SSL certificates
- ✅ **Persistent storage** untuk SQLite
- ✅ **Built-in monitoring** dan alerting
- ✅ **Easy scaling** dengan perintah sederhana
- ✅ **GitHub integration** untuk CI/CD

## 🐛 Troubleshooting

### Jika Deploy Gagal:
```bash
# Cek logs
flyctl logs --app absensi-api

# Rebuild dan redeploy
flyctl deploy --strategy=immediate
```

### Jika Health Check Gagal:
```bash
# Test health endpoint
curl https://absensi-api.fly.dev/health

# Cek configuration
flyctl status
```

### Jika Database Error:
```bash
# Connect ke machine
flyctl ssh console

# Cek database file
ls -la /app/data/

# Create database manual
python -c "from app.models import Base; from app.config import engine; Base.metadata.create_all(bind=engine)"
```

## 📱 Testing Production
```bash
# Test health check
curl https://absensi-api.fly.dev/health

# Test API documentation
# Buka: https://absensi-api.fly.dev/docs

# Test face recognition endpoint
curl -X POST https://absensi-api.fly.dev/v1/recognize \
  -H "Authorization: Bearer stb-01:ISI_TOKEN_DEVICE_KAMU" \
  -F "image=@test_photo.jpg"
```

## 🎯 Next Steps
1. **Deploy ke Fly.io** menggunakan commands di atas
2. **Test API** di production URL
3. **Update desktop app** dengan production URL
4. **Monitor performance** menggunakan Fly.io dashboard
5. **Setup alerts** untuk monitoring

API Anda siap untuk production di Fly.io! 🚀
