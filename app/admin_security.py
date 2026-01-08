import secrets
import bcrypt
from datetime import datetime, timedelta
from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from app.models import AdminUser, AdminSession

SESSION_HOURS = 12

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_session(db: Session, user_id: int) -> str:
    token = secrets.token_hex(24)  # 48 chars
    expires = datetime.utcnow() + timedelta(hours=SESSION_HOURS)
    s = AdminSession(token=token, user_id=user_id, expires_at=expires)
    db.add(s)
    db.commit()
    return token

def require_admin_session(db: Session, authorization: str = Header(default="")) -> AdminUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.replace("Bearer ", "", 1).strip()

    sess = db.query(AdminSession).filter(AdminSession.token == token).one_or_none()
    if not sess or sess.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid/expired token")

    user = db.query(AdminUser).filter(AdminUser.id == sess.user_id, AdminUser.is_active == True).one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user