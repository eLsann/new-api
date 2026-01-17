import os
import sys
import shutil
import pymysql

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(API_ROOT)

from app.database import engine, Base, SessionLocal
from app.models import AdminUser # Ensure models are loaded
from app.security import hash_password

DESKTOP_DIR = os.path.abspath(os.path.join(API_ROOT, "..", "Absensi Desktop"))

def clean_directory(path):
    if not os.path.exists(path):
        return
    print(f"Cleaning {path}...")
    for item in os.listdir(path):
        if item == ".gitkeep": continue
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")

def reset_db_mysql():
    print("Resetting MySQL Database 'absensi'...")
    try:
        conn = pymysql.connect(host='localhost', user='root', password='')
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS absensi")
        cursor.execute("CREATE DATABASE absensi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
        print("Database recreated.")
    except Exception as e:
        print(f"Error resetting MySQL: {e}")
        return False
    return True

def init_tables_and_admin():
    print("Initializing tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Creating default admin (admin/admin)...")
    db = SessionLocal()
    try:
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin"),
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created.")
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()

def main():
    print("STARTING FULL SYSTEM RESET")
    print("=" * 40)
    
    # 1. Reset Database
    if not reset_db_mysql():
        print("Aborting due to DB error.")
        return

    # 2. Clean API Files
    clean_directory(os.path.join(API_ROOT, "data", "snapshots"))
    clean_directory(os.path.join(API_ROOT, "logs"))
    
    sqlite_path = os.path.join(API_ROOT, "absensi.db")
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
        print("Deleted absensi.db")

    # 3. Clean Desktop Files
    clean_directory(os.path.join(DESKTOP_DIR, "logs"))
    clean_directory(os.path.join(DESKTOP_DIR, "offline_queue"))
    clean_directory(os.path.join(DESKTOP_DIR, "tts_cache"))
    
    # 4. Init Data
    init_tables_and_admin()
    
    print("=" * 40)
    print("SYSTEM RESET COMPLETE")
    print("Default Admin: admin / admin")

if __name__ == "__main__":
    main()
