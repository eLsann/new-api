from app.database import SessionLocal
from app.models import AdminUser
from app.security import hash_password
import sys

def create_admin(username, password):
    db = SessionLocal()
    print(f"Connecting to database to manage user '{username}'...")
    try:
        # Cek apakah user ada
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"User '{username}' found (ID: {existing.id}). Updating password...")
            existing.password_hash = hash_password(password)
            existing.is_active = True
        else:
            print(f"User '{username}' not found. Creating new...")
            new_admin = AdminUser(username=username, password_hash=hash_password(password), is_active=True)
            db.add(new_admin)
        
        db.commit()
        print("="*40)
        print(f"SUCCESS: Admin '{username}' is ready!")
        print("="*40)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Default user if not provided
        create_admin("admin", "admin123")
    else:
        create_admin(sys.argv[1], sys.argv[2])
