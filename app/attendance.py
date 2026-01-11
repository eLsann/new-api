from datetime import datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DailyAttendance, AttendanceEvent

def _parse_hhmm(hhmm: str) -> dtime:
    h, m = hhmm.split(":")
    return dtime(hour=int(h), minute=int(m))

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
    tz = ZoneInfo(policy_timezone)
    now_local = datetime.now(tz=tz)
    day_str = now_local.date().isoformat()
    now_utc_naive = now_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

    # log non-ok
    if status != "ok":
        ev = AttendanceEvent(
            day=day_str,
            ts=now_utc_naive,
            device_id=device_id,
            predicted_name=None,
            final_name=None,
            event_type=None,
            is_late=False,
            status=status,
            distance=distance,
            snapshot_path=snapshot_path,
        )
        db.add(ev)
        db.commit()
        return {"status": status, "event_type": None, "is_late": False, "audio_text": None}

    # Daily cooldown check
    last = (
        db.query(AttendanceEvent)
        .filter(
            AttendanceEvent.day == day_str,
            AttendanceEvent.final_name == person_name,
            AttendanceEvent.status.in_(("ok", "duplicate", "cooldown", "reject_out_too_early")),
        )
        .order_by(AttendanceEvent.ts.desc())
        .first()
    )
    if last and (now_utc_naive - last.ts) < timedelta(seconds=settings.cooldown_seconds):
        ev = AttendanceEvent(
            day=day_str,
            ts=now_utc_naive,
            device_id=device_id,
            predicted_name=person_name,
            final_name=person_name,
            event_type=None,
            is_late=False,
            status="cooldown",
            distance=distance,
            snapshot_path=snapshot_path,
        )
        db.add(ev)
        db.commit()
        return {
            "status": "cooldown",
            "event_type": None,
            "is_late": False,
            "audio_text": f"Halo {person_name}, mohon tunggu sebentar.",
        }

    late_after = _parse_hhmm(late_after_time)
    out_start = _parse_hhmm(out_start_time)

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

    t = now_local.timetz().replace(tzinfo=None)

    event_type = None
    is_late = False
    audio_text = None
    final_status = "ok"

    if daily.in_time is None:
        # IN
        event_type = "IN"
        is_late = (t > late_after)
        daily.in_time = now_utc_naive
        daily.in_is_late = is_late
        audio_text = (
            f"Halo {person_name}, absensi masuk tercatat. Anda terlambat."
            if is_late else
            f"Halo {person_name}, absensi masuk berhasil."
        )

    elif daily.out_time is None:
        # OUT only after out_start_time
        if t < out_start:
            final_status = "reject_out_too_early"
            event_type = None
            audio_text = f"Halo {person_name}, belum waktunya absensi pulang."
        else:
            event_type = "OUT"
            daily.out_time = now_utc_naive
            audio_text = f"Terima kasih {person_name}, absensi pulang berhasil."

    else:
        final_status = "duplicate"
        audio_text = f"Halo {person_name}, absensi hari ini sudah lengkap."

    daily.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(daily)

    ev = AttendanceEvent(
        day=day_str,
        ts=now_utc_naive,
        device_id=device_id,
        predicted_name=person_name,
        final_name=person_name,
        event_type=event_type,
        is_late=is_late if event_type == "IN" else False,
        status=final_status,
        distance=distance,
        snapshot_path=snapshot_path,
    )
    db.add(ev)
    db.commit()

    return {"status": final_status, 
            "event_type": event_type, 
            "is_late": is_late, 
            "audio_text": audio_text}