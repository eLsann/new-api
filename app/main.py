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
from app.recog import identify, rebuild_cache
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


app = FastAPI(
    title=settings.app_name, 
    version="2.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True, 
        "clientId": "fastapi-demo"
    }
)

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




@app.post("/v1/recognize")
async def v1_recognize(
    file: UploadFile = File(...),
    x_device_id: str = Header(default=""),
    x_device_token: str = Header(default=""),
    db: Session = Depends(get_db),
):
    logger.info(f"Recognition request from device: {x_device_id}")
    
    if not verify_device(x_device_id, x_device_token):
        logger.warning(f"Unauthorized device access attempt: {x_device_id}")
        raise HTTPException(status_code=401, detail="Unauthorized device")

    img_bytes = await file.read()

    try:
        ident = identify(img_bytes=img_bytes, db=db)
    except ValueError as e:
        logger.error(f"Image processing error from device {x_device_id}: {str(e)}")
        return JSONResponse(
            {
                "status": "reject",
                "device_id": x_device_id,
                "name": None,
                "distance": None,
                "event_type": None,
                "late": False,
                "audio_text": "Gagal memproses gambar.",
                "reason": str(e),
            },
            status_code=400,
        )

    status = ident["status"]
    dist = ident["distance"]

    # Snapshot logic
    snapshot_path = None
    if settings.save_snapshots:
        if settings.snapshot_on_unknown and status == "unknown":
            snapshot_path = save_snapshot_bytes(img_bytes, reason="unknown", device_id=x_device_id)
        if settings.snapshot_on_low_conf and status == "ok" and dist is not None and dist > settings.low_conf_distance:
            snapshot_path = save_snapshot_bytes(img_bytes, reason="lowconf", device_id=x_device_id)

    # unknown/reject/error -> log as event (so admin can review)
    if status != "ok":
        # store as event without daily update
        policy = get_policy(db)
        out = decide_and_record(
            db,
            person_name="",
            device_id=x_device_id,
            distance=dist,
            status=status,
            policy_timezone=policy.timezone,
            in_start_time=policy.in_start_time,
            late_after_time=policy.late_after_time,
            out_start_time=policy.out_start_time,
            snapshot_path=snapshot_path,
        )
        audio_text = "Wajah tidak dikenali." if status == "unknown" else "Gagal memproses gambar."
        return JSONResponse(
            {
                "status": out["status"],
                "device_id": x_device_id,
                "name": None,
                "distance": dist,
                "event_type": None,
                "late": False,
                "audio_text": audio_text,
                "reason": ident.get("reason"),
            }
        )

    policy = get_policy(db)

    out = decide_and_record(
        db,
        person_name=ident["name"],
        device_id=x_device_id,
        distance=dist,
        status="ok",
        policy_timezone=policy.timezone,
        in_start_time=policy.in_start_time,
        late_after_time=policy.late_after_time,
        out_start_time=policy.out_start_time,
        snapshot_path=snapshot_path,
    )

    return JSONResponse(
        {
            "status": out["status"],
            "device_id": x_device_id,
            "name": ident["name"],
            "distance": dist,
            "event_type": out["event_type"],
            "late": bool(out["is_late"]) if out["event_type"] == "IN" else False,
            "audio_text": out["audio_text"],
            "reason": None,
        }
    )

@app.post("/admin/rebuild_cache")
def admin_rebuild_cache(
    db: Session = Depends(get_db), 
    _admin=Depends(get_current_admin)
):
    from app.admin_auth import get_current_admin
    logger.info("Rebuilding face recognition cache via admin request")
    rebuild_cache(db)
    return {"ok": True}
