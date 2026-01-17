import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import AdminUser
from app.security import hash_password
import getpass

def create_admin():
    print("=" * 40)
    print("    Admin Account Setup")
    print("=" * 40)
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("Error: Password cannot be empty")
        return
    
    confirm = getpass.getpass("Confirm Password: ")
    if password != confirm:
        print("Error: Passwords do not match")
        return
    
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            existing.password_hash = hash_password(password)
            existing.is_active = True
            print(f"Updated existing user '{username}'")
        else:
            new_admin = AdminUser(
                username=username, 
                password_hash=hash_password(password), 
                is_active=True
            )
            db.add(new_admin)
            print(f"Created new admin '{username}'")
        
        db.commit()
        print("=" * 40)
        print("SUCCESS!")
        print("=" * 40)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
