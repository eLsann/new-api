from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DailyAttendance
from app.admin_auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/reports/monthly")
def report_monthly(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):


    rows = db.query(DailyAttendance).filter(DailyAttendance.day.startswith(month)).all()

    summary: dict[str, dict] = {}
    for r in rows:
        s = summary.setdefault(
            r.person_name,
            {"person_name": r.person_name, "days_present": 0, "late_count": 0, "missing_out": 0},
        )
        if r.in_time is not None:
            s["days_present"] += 1
            if r.in_is_late:
                s["late_count"] += 1
        if r.in_time is not None and r.out_time is None:
            s["missing_out"] += 1

    return {"month": month, "total_records": len(rows), "summary": [summary[k] for k in sorted(summary.keys())]}