"""
Attendance Logic with Time Rules
- IN: anytime, but late if after 08:00
- OUT: only allowed 14:00 - 16:00
- Only record successful events (status ok)
"""
from datetime import datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DailyAttendance, AttendanceEvent

# Time configuration
LATE_AFTER = dtime(8, 0)    # Late if check-in after 08:00
OUT_START = dtime(14, 0)    # OUT allowed from 14:00
OUT_END = dtime(16, 0)      # OUT allowed until 16:00


def decide_and_record(
    db: Session,
    *,
    person_name: str,
    device_id: str,
    distance: float | None,
    status: str,
    policy_timezone: str,
    in_start_time: str,
    late_after_time: str,
    out_start_time: str,
    snapshot_path: str | None = None,
) -> dict:
    """
    Attendance logic with time rules:
    - IN: always allowed, late label if after 08:00
    - OUT: only allowed 14:00 - 16:00
    """
    tz = ZoneInfo(policy_timezone)
    now_local = datetime.now(tz=tz)
    day_str = now_local.date().isoformat()
    now_utc_naive = now_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    current_time = now_local.timetz().replace(tzinfo=None)

    # Skip recording for non-ok status
    if status != "ok":
        return {"status": status, "event_type": None, "is_late": False, "audio_text": None}

    # Check cooldown
    last = (
        db.query(AttendanceEvent)
        .filter(
            AttendanceEvent.day == day_str,
            AttendanceEvent.final_name == person_name,
            AttendanceEvent.status == "ok",
        )
        .order_by(AttendanceEvent.ts.desc())
        .first()
    )
    if last and (now_utc_naive - last.ts) < timedelta(seconds=settings.cooldown_seconds):
        return {
            "status": "cooldown",
            "event_type": None,
            "is_late": False,
            "audio_text": f"Halo {person_name}, mohon tunggu sebentar.",
        }

    # Get or create daily attendance
    daily = (
        db.query(DailyAttendance)
        .filter(DailyAttendance.day == day_str, DailyAttendance.person_name == person_name)
        .one_or_none()
    )
    if daily is None:
        daily = DailyAttendance(day=day_str, person_name=person_name)
        db.add(daily)
        db.commit()
        db.refresh(daily)

    event_type = None
    is_late = False
    audio_text = None
    final_status = "ok"

    if daily.in_time is None:
        # IN - check if late
        event_type = "IN"
        is_late = (current_time > LATE_AFTER)
        daily.in_time = now_utc_naive
        daily.in_is_late = is_late
        
        if is_late:
            audio_text = f"Halo {person_name}, absensi masuk tercatat. Anda terlambat."
        else:
            audio_text = f"Halo {person_name}, absensi masuk berhasil."

    elif daily.out_time is None:
        # OUT - check time window (14:00 - 16:00)
        if current_time < OUT_START:
            return {
                "status": "reject_out_early",
                "event_type": None,
                "is_late": False,
                "audio_text": f"Halo {person_name}, absensi pulang belum dibuka. Buka jam 14:00.",
            }
        elif current_time > OUT_END:
            return {
                "status": "reject_out_late",
                "event_type": None,
                "is_late": False,
                "audio_text": f"Halo {person_name}, absensi pulang sudah ditutup.",
            }
        else:
            event_type = "OUT"
            daily.out_time = now_utc_naive
            audio_text = f"Terima kasih {person_name}, absensi pulang berhasil."

    else:
        # Already complete
        return {
            "status": "duplicate",
            "event_type": None,
            "is_late": False,
            "audio_text": f"Halo {person_name}, absensi hari ini sudah lengkap.",
        }

    daily.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(daily)

    # Record successful event
    ev = AttendanceEvent(
        day=day_str,
        ts=now_utc_naive,
        device_id=device_id,
        predicted_name=person_name,
        final_name=person_name,
        event_type=event_type,
        is_late=is_late,
        status=final_status,
        distance=distance,
        snapshot_path=snapshot_path,
    )
    db.add(ev)
    db.commit()

    return {
        "status": final_status,
        "event_type": event_type,
        "is_late": is_late,
        "audio_text": audio_text
    }