import os, sys
from datetime import datetime, timedelta

sys.path.append(os.path.abspath("."))

from app.database import SessionLocal, Base, engine
from app.policy import get_policy
from app.models import AttendanceEvent

Base.metadata.create_all(bind=engine)

def main():
    db = SessionLocal()
    try:
        policy = get_policy(db)
        cutoff = datetime.utcnow() - timedelta(days=int(policy.retention_days))
        q = db.query(AttendanceEvent).filter(AttendanceEvent.ts < cutoff)
        count = q.count()
        q.delete(synchronize_session=False)
        db.commit()
        print(f"[OK] deleted {count} attendance_events older than {policy.retention_days} days")
    finally:
        db.close()

if __name__ == "__main__":
    main()