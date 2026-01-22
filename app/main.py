from dotenv import load_dotenv
load_dotenv()

from app.logging_config import setup_logging, get_logger
setup_logging(app_name="absensi_api", log_level="INFO")
logger = get_logger(__name__)

from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.policy import get_policy
from app.recog import identify_multiple, rebuild_cache
from app.attendance import decide_and_record
from app.snapshots import save_snapshot_bytes

from app.admin_people import router as admin_people_router
from app.admin_logs import router as admin_logs_router
from app.admin_corrections import router as admin_corrections_router
from app.admin_reports import router as admin_reports_router
from app.admin_auth import router as admin_auth_router, get_current_admin

Base.metadata.create_all(bind=engine)

from fastapi.security import HTTPBearer
from pathlib import Path
import os


app = FastAPI(
    title=settings.app_name, 
    version="2.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True, 
        "clientId": "fastapi-demo"
    }
)

@app.on_event("startup")
async def startup_event():
    # Check DB Connection
    logger.info(f"Starting up in {settings.env} mode")
    if "mysql" in settings.database_url:
        logger.info("Using MySQL Database (Laragon compatible)")
    else:
        logger.info("Using SQLite Database")
    
    # Ensure data dirs exist
    os.makedirs(settings.snapshot_dir, exist_ok=True)
    os.makedirs("./logs", exist_ok=True)


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway/monitoring"""
    return {"status": "healthy", "version": "2.0.0"}

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_tokens(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    raw = (raw or "").strip()
    if not raw:
        return out
    for item in raw.split(","):
        item = item.strip()
        if not item or ":" not in item:
            continue
        device_id, token = item.split(":", 1)
        out[device_id.strip()] = token.strip()
    return out

DEVICE_TOKEN_MAP = _parse_tokens(settings.device_tokens)

def verify_device(device_id: str, token: str) -> bool:
    if not device_id or not token:
        return False
    return DEVICE_TOKEN_MAP.get(device_id) == token

app.include_router(admin_people_router)
app.include_router(admin_logs_router)
app.include_router(admin_corrections_router)
app.include_router(admin_reports_router)
app.include_router(admin_auth_router)


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok", "service": "Absensi API"}


@app.post("/v1/recognize_multi")
async def v1_recognize_multi(
    file: UploadFile = File(...),
    x_device_id: str = Header(default=""),
    x_device_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    """Recognize multiple faces (max 5) in a single image"""
    from app.recog import identify_multiple
    
    logger.info(f"Multi-face recognition request from device: {x_device_id}")
    
    if not verify_device(x_device_id, x_device_token):
        logger.warning(f"Unauthorized device access attempt: {x_device_id}")
        raise HTTPException(status_code=401, detail="Unauthorized device")

    img_bytes = await file.read()
    
    # Detect and identify all faces
    result = identify_multiple(img_bytes, db, max_faces=5)
    
    if result["status"] == "no_face":
        return JSONResponse({
            "status": "no_face",
            "device_id": x_device_id,
            "faces": [],
            "recognized_names": [],
            "combined_audio": None
        })
    
    # Process attendance for each recognized face
    policy = get_policy(db)
    processed_faces = []
    attendance_results = []
    
    for face in result["faces"]:
        if face["status"] == "ok" and face["name"]:
            # Record attendance for this person
            out = decide_and_record(
                db,
                person_name=face["name"],
                device_id=x_device_id,
                distance=face["distance"],
                status="ok",
                policy_timezone=policy.timezone,
                in_start_time=policy.in_start_time,
                late_after_time=policy.late_after_time,
                out_start_time=policy.out_start_time,
                out_end_time=policy.out_end_time,  # NEW: pass out_end_time from policy
                snapshot_path=None,
            )
            
            processed_faces.append({
                "queue_id": face["queue_id"],
                "bbox": face["bbox"],
                "name": face["name"],
                "status": out["status"],
                "event_type": out["event_type"],
                "late": bool(out.get("is_late", False))
            })
            
            if out["status"] == "ok":
                attendance_results.append({
                    "name": face["name"],
                    "event_type": out["event_type"],
                    "late": bool(out.get("is_late", False))
                })
        else:
            processed_faces.append({
                "queue_id": face["queue_id"],
                "bbox": face["bbox"],
                "name": None,
                "status": face["status"],
                "event_type": None,
                "late": False
            })
    
    # Combined audio generation is handled by the Desktop Client now
    # We just return the structured data
    
    recognized_names = [res["name"] for res in attendance_results]
    
    logger.info(f"Multi-face: {len(processed_faces)} faces, {len(recognized_names)} recorded")
    
    return JSONResponse({
        "status": "ok",
        "device_id": x_device_id,
        "faces": processed_faces,
        "recognized_names": recognized_names,
        "combined_audio": None
    })




@app.post("/admin/rebuild_cache")
def admin_rebuild_cache(
    db: Session = Depends(get_db), 
    _admin=Depends(get_current_admin)
):
    from app.admin_auth import get_current_admin
    logger.info("Rebuilding face recognition cache via admin request")
    rebuild_cache(db)
    return {"ok": True}

@app.post("/admin/cleanup")
def admin_cleanup(
    days: int = 30,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    """Trigger cleanup of old data (snapshots & logs)"""
    import subprocess
    import sys
    
    script_path = Path(__file__).parent.parent / "scripts" / "cleanup.py"
    
    logger.info(f"Triggering cleanup for files older than {days} days")
    
    # Run script as subprocess to ensure clean execution context
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), "--days", str(days)],
            capture_output=True,
            text=True
        )
        return {
            "ok": True,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"ok": False, "error": str(e)}

@app.post("/admin/reset_attendance")
def admin_reset_attendance(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    """Reset all attendance data (for demo purposes)"""
    from app.models import AttendanceEvent, DailyAttendance
    
    logger.info("Resetting all attendance data (demo)")
    
    # Delete all attendance events
    events_deleted = db.query(AttendanceEvent).delete()
    
    # Delete all daily attendance records
    daily_deleted = db.query(DailyAttendance).delete()
    
    db.commit()
    
    logger.info(f"Reset complete: {events_deleted} events, {daily_deleted} daily records deleted")
    
    return {
        "ok": True,
        "events_deleted": events_deleted,
        "daily_deleted": daily_deleted
    }
