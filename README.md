# Absensi API

Face attendance system using FastAPI and Facenet-PyTorch.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Run API
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Create admin account
python create_admin.py
```

## Database

Uses SQLite by default (no installation required).

## API Documentation

Swagger UI: http://localhost:8000/docs

## Authentication

```
POST /admin/login {"username", "password"} -> token
Header: Authorization: Bearer <token>
```