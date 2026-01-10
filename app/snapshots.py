import os
from datetime import datetime, timezone
from app.config import settings
from app.utils import ensure_dir

def save_snapshot_bytes(img_bytes: bytes, *, reason: str, device_id: str) -> str:
    ensure_dir(settings.snapshot_dir)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    fn = f"{ts}_{device_id}_{reason}.jpg"
    path = os.path.join(settings.snapshot_dir, fn)
    with open(path, "wb") as f:
        f.write(img_bytes)
    return path