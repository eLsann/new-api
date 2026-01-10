from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Truncates password to 72 characters (bcrypt limit).
    """
    truncated_password = password[:72] if len(password) > 72 else password
    return pwd_context.hash(truncated_password)

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    Truncates password to 72 characters (bcrypt limit).
    """
    truncated_password = password[:72] if len(password) > 72 else password
    return pwd_context.verify(truncated_password, password_hash)

