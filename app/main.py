from dotenv import load_dotenv
load_dotenv()

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

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For desktop app - adjust in production
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

# --- routers ---
app.include_router(admin_people_router)
app.include_router(admin_logs_router)
app.include_router(admin_corrections_router)
app.include_router(admin_reports_router)
app.include_router(admin_auth_router)

from fastapi.responses import JSONResponse, HTMLResponse



@app.get("/test-upload", response_class=HTMLResponse)
def test_upload_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Absensi API Tester (Direct)</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .card { border: 1px solid #ccc; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        input[type="text"] { width: 100%; padding: 0.5rem; }
        button { background: #007bff; color: white; border: none; padding: 0.5rem 1rem; cursor: pointer; border-radius: 4px; }
        button:hover { background: #0056b3; }
        #result { background: #f8f9fa; padding: 1rem; border-radius: 4px; white-space: pre-wrap; font-family: monospace; border: 1px solid #ddd; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <h1>📸 Absensi API Tester (Direct Route)</h1>
    
    <div class="card">
        <h2>1. Konfigurasi Device</h2>
        <div class="form-group">
            <label>API URL:</label>
            <input type="text" id="apiUrl" value="/v1/recognize">
        </div>
        <div class="form-group">
            <label>Device Token (X-Device-Token):</label>
            <input type="text" id="deviceToken" value="87654321">
        </div>
        <div class="form-group">
            <label>Device ID (Optional, X-Device-Id):</label>
            <input type="text" id="deviceId" value="stb-01">
        </div>
    </div>

    <div class="card">
        <h2>2. Test Recognize</h2>
        <div class="form-group">
            <label>Pilih Foto Wajah:</label>
            <input type="file" id="fileInput" accept="image/*">
        </div>
        <button onclick="uploadImage()">🚀 Kirim Absensi</button>
    </div>

    <div id="resultCard" class="card hidden">
        <h3>Hasil Response:</h3>
        <pre id="result">Waiting...</pre>
    </div>

    <script>
        async function uploadImage() {
            const fileInput = document.getElementById('fileInput');
            const resultDiv = document.getElementById('result');
            const resultCard = document.getElementById('resultCard');

            if (!fileInput.files[0]) {
                alert("Pilih file dulu boss!");
                return;
            }

            resultCard.classList.remove('hidden');
            resultDiv.textContent = "Mengirim data...";

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const headers = {
                'X-Device-Token': document.getElementById('deviceToken').value,
                'X-Device-Id': document.getElementById('deviceId').value
            };

            try {
                const response = await fetch(document.getElementById('apiUrl').value, {
                    method: 'POST',
                    headers: headers,
                    body: formData
                });

                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
                
                if (!response.ok) {
                    resultDiv.style.color = "red";
                } else {
                    resultDiv.style.color = "green";
                }

            } catch (error) {
                resultDiv.textContent = "Error: " + error.message;
                resultDiv.style.color = "red";
            }
        }
    </script>
</body>
</html>
    """


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
