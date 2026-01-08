# 🐳 Docker Deployment Guide

## 📋 Keunggulan Docker untuk Absensi API

### ✅ Benefits
1. **Consistency**: Environment sama di local & production
2. **Portability**: Jalan di mana saja (Windows, Linux, Mac)
3. **Scalability**: Mudah scaling dengan load balancer
4. **Isolation**: Tidak conflict dengan dependencies lain
5. **Version Control**: Docker image versioning
6. **Resource Management**: Memory & CPU limits yang jelas

### 🎯 Impact untuk Project Anda

#### Positive Impacts:
- **Face Recognition**: OpenCV & PyTorch yang terisolasi
- **Database**: SQLite yang persistent dengan volumes
- **Security**: Container isolation untuk data pribadi
- **Performance**: Optimized layers untuk faster startup
- **Monitoring**: Health checks otomatis
- **Backup**: Volume mounting untuk data persistence

#### Considerations:
- **Learning Curve**: Perlu belajar Docker commands
- **Image Size**: PyTorch & OpenCV membuat image besar (~2GB)
- **Resource Usage**: Memory usage lebih tinggi
- **Debugging**: Lebih sulit debug di container

## 🚀 Docker Deployment Options

### 1. Local Development
```bash
# Build dan run
docker-compose up --build

# Background mode
docker-compose up -d

# Stop
docker-compose down
```

### 2. Cloud Hosting dengan Docker

#### A. Fly.io (Gratis $5/month)
```bash
# Install fly CLI
fly launch

# Deploy
fly deploy
```

#### B. DigitalOcean (Gratis $200 credit)
```bash
# Create droplet dengan Docker
# Deploy docker-compose
```

#### C. AWS Lightsail (Gratis tier)
```bash
# Container service
# Push ke AWS ECR
```

#### D. Heroku (Free tier)
```bash
# Container registry
heroku container:push web
heroku container:release web
```

### 3. Self-Hosting
```bash
# VPS dengan Docker installed
# Git clone & docker-compose up
```

## 📦 Build Commands

### Local Development
```bash
# Build image
docker build -t absensi-api .

# Run container
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./absensi.db absensi-api
```

### Production
```bash
# Build optimized image
docker build -t absensi-api:prod .

# Run with volumes
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/absensi.db:/app/absensi.db \
  absensi-api:prod
```

## 🔧 Optimization Tips

### 1. Multi-stage Build
```dockerfile
# Build stage
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

### 2. .dockerignore
```
__pycache__/
*.pyc
.venv/
.git/
.vscode/
*.log
```

### 3. Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

## 🌐 Free Hosting Options dengan Docker

### 1. Fly.io ⭐ Recommended
- **$5 free credit** per bulan
- **Always online** (no sleep)
- **Global CDN**
- **Custom domain**
- **Docker native**

### 2. Railway (dengan Docker)
- **Docker deployment** support
- **Auto HTTPS**
- **Persistent storage**

### 3. Heroku
- **Container registry**
- **Free dyno hours**
- **Add-ons available**

### 4. Oracle Cloud Free
- **2 VMs gratis**
- **Docker support**
- **Always online**

## 🔄 Update Desktop App
```bash
# Update .env untuk production
API_BASE=https://your-docker-app.fly.dev
```

## 📊 Monitoring & Logging
```bash
# View logs
docker-compose logs -f

# Resource usage
docker stats

# Health check
curl http://localhost:8000/health
```
