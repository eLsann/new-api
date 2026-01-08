import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.database import SessionLocal
from app.models import AdminUser

def main():
    db = SessionLocal()
    try:
        total = db.query(AdminUser).count()
        if total == 0:
            print("Tidak ada admin di database.")
            return

        db.query(AdminUser).delete()
        db.commit()
        print(f"OK. {total} admin berhasil dihapus.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
