# 💳 Setup Payment Method Fly.io

## 🎯 Mengapa Perlu Payment Method?
Fly.io memerlukan payment method untuk:
- Verifikasi identitas
- Mencegah abuse
- Auto-charge jika melebihi free credit

## 💰 Biaya & Credit:
- **$5 free credit** per bulan (otomatis)
- **Estimasi usage**: ~$2-3/bulan untuk API Anda
- **Tidak akan dikenakan biaya** jika di bawah $5

## 🔗 Langkah Setup:

### 1. Buka Fly.io Dashboard
- Login ke [fly.io/dashboard](https://fly.io/dashboard)
- Klik **Account** → **Billing**

### 2. Add Payment Method
- Klik **"Add Payment Method"**
- Pilih **Credit Card** atau **PayPal**
- Isi detail pembayaran

### 3. Verifikasi
- Tunggu proses verifikasi (1-2 menit)
- Payment method akan muncul di dashboard

## 🚀 Setelah Payment Method Terdaftar:

### Deploy Command:
```bash
# Gunakan full path untuk flyctl
C:\Users\Sanzz\.fly\bin\flyctl.exe launch

# Atau tambahkan ke PATH
# Buka System Properties → Environment Variables → PATH
# Tambahkan: C:\Users\Sanzz\.fly\bin\
```

### Deploy Steps:
1. **Run launch command**
2. **Confirm configuration** (Yes)
3. **Choose region** (Singapore)
4. **Deploy** (otomatis)

## 🌐 Expected URL:
```
https://absensi-api.fly.dev
```

## 📊 Monitoring Biaya:
```bash
# Cek usage dan billing
C:\Users\Sanzz\.fly\bin\flyctl.exe org billing

# Monitoring real-time
C:\Users\Sanzz\.fly\bin\flyctl.exe monitor
```

## ⚠️ Catatan Penting:
- **Free credit refresh** setiap bulan
- **Auto-stop** jika melebihi limit
- **Alert email** sebelum charge
- **Bisa cancel** kapan saja

## 🔧 Alternative Jika Tidak Mau Payment:

### Option 1: Railway (dengan Docker)
```bash
# Railway sudah support Docker
# Sign up di railway.app
# Connect GitHub repo
# Auto-deploy
```

### Option 2: Oracle Cloud Free
- **2 VMs gratis** selamanya
- **Docker pre-installed**
- **No credit card required**

### Option 3: Local Docker
```bash
# Jalankan di local/server sendiri
docker-compose up -d
# Port forward dengan ngrok
```

## 📱 Langkah Selanjutnya:
1. **Setup payment method** di Fly.io
2. **Run deploy command**
3. **Test production API**
4. **Update desktop app**

## 🎉 Setelah Deploy Berhasil:
- API always online
- Global CDN
- Auto HTTPS
- Persistent storage
- Real-time monitoring

Silakan setup payment method terlebih dahulu, kemudian jalankan deploy command! 🚀
