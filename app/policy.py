import time
from sqlalchemy.orm import Session
from app.models import AttendancePolicy

_CACHE = {"policy": None, "built_at": 0.0}
_TTL = 5.0

def get_policy(db: Session) -> AttendancePolicy:
    now = time.time()
    if _CACHE["policy"] is not None and (now - _CACHE["built_at"]) < _TTL:
        return _CACHE["policy"]

    policy = db.query(AttendancePolicy).filter(AttendancePolicy.id == 1).one_or_none()
    if policy is None:
        policy = AttendancePolicy(id=1)
        db.add(policy)
        db.commit()
        db.refresh(policy)

    _CACHE["policy"] = policy
    _CACHE["built_at"] = now
    return policy

def invalidate_policy_cache():
    _CACHE["policy"] = None
    _CACHE["built_at"] = 0.0