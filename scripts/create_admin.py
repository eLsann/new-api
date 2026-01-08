import os, sys
sys.path.append(os.path.abspath("."))

import getpass
from app.database import SessionLocal
from app.models import AdminUser
from app.security import hash_password

def main():
    db = SessionLocal()
    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ").strip()

    exist = db.query(AdminUser).filter(AdminUser.username == username).first()
    if exist:
        print("Admin sudah ada.")
        return

    u = AdminUser(username=username, password_hash=hash_password(password), is_active=True)
    db.add(u)
    db.commit()
    print("OK admin dibuat.")

if __name__ == "__main__":
    main()
