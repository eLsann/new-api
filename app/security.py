from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(data: dict, secret_key: str, expires_minutes: int = 60) -> str:
    to_encode = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": exp})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

def decode_token(token: str, secret_key: str) -> dict:
    return jwt.decode(token, secret_key, algorithms=["HS256"])
