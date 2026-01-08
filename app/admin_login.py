from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminUser
from app.admin_security import verify_password, create_session

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="username/password required")

    user = db.query(AdminUser).filter(AdminUser.username == username, AdminUser.is_active == True).one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_session(db, user.id)
    return {"token": token, "token_type": "Bearer"}