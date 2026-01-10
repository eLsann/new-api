from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.database import get_db
from app.config import settings
from app.models import AdminUser  # pastikan model ini ada


router = APIRouter(prefix="/admin", tags=["admin-auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def _create_access_token(sub: str, expire_hours: int) -> str:
    exp = datetime.utcnow() + timedelta(hours=expire_hours)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


@router.post("/login")
def admin_login(payload: dict, db: Session = Depends(get_db)):
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="username & password required")

    user = db.query(AdminUser).filter(AdminUser.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_access_token(username, settings.admin_token_expire_hours)
    return {"access_token": token, "token_type": "bearer"}


def get_current_admin(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    # ✅ KUNCI: BACA Authorization HEADER
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(AdminUser).filter(AdminUser.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
