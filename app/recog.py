import numpy as np
import cv2
import torch
from PIL import Image
from sqlalchemy.orm import Session
from facenet_pytorch import InceptionResnetV1

from app.config import settings
from app.models import Person
from app.logging_config import get_logger

logger = get_logger(__name__)

_DEVICE = "cpu"
_MODEL = InceptionResnetV1(pretrained="vggface2").eval().to(_DEVICE)
logger.info(f"Face recognition model loaded on device: {_DEVICE}")

_CACHE = {"names": None, "vectors": None}

def _csv_to_vec(s: str) -> np.ndarray:
    # Use np.loadtxt for better NumPy compatibility
    from io import StringIO
    return np.loadtxt(StringIO(s), delimiter=',', dtype=np.float32)

def rebuild_cache(db: Session):
    logger.info("Rebuilding face recognition cache...")
    persons = db.query(Person).all()
    names, vecs = [], []
    for p in persons:
        if not p.embeddings:
            continue
        mats = [_csv_to_vec(e.vec_csv) for e in p.embeddings]
        mean = np.vstack(mats).mean(axis=0)
        names.append(p.name)
        vecs.append(mean)
    _CACHE["names"] = names
    _CACHE["vectors"] = np.vstack(vecs).astype(np.float32) if vecs else np.zeros((0, 512), dtype=np.float32)
    logger.info(f"Cache rebuilt with {len(names)} persons")

def _bytes_to_bgr(img_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("invalid_image")
    return bgr

def _preprocess(face_bgr: np.ndarray) -> torch.Tensor:
    rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb).resize((160, 160))
    x = np.asarray(pil).astype(np.float32)
    x = (x - 127.5) / 128.0
    return torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).to(_DEVICE)

@torch.inference_mode()
def embed_face(face_bgr: np.ndarray) -> np.ndarray:
    t = _preprocess(face_bgr)
    return _MODEL(t).cpu().numpy().astype(np.float32)[0]

def identify(img_bytes: bytes, db: Session) -> dict:
    try:
        logger.debug(f"Starting face identification, image size: {len(img_bytes)} bytes")
        
        bgr = _bytes_to_bgr(img_bytes)
        h, w = bgr.shape[:2]
        logger.debug(f"Image dimensions: {w}x{h}")
        
        if min(h, w) < settings.min_face_px:
            logger.warning(f"Face crop too small: {min(h, w)} < {settings.min_face_px}")
            return {"status": "reject", "reason": "face_crop_too_small", "name": None, "distance": None}

        if _CACHE["names"] is None:
            logger.info("Cache not initialized, rebuilding...")
            rebuild_cache(db)

        names = _CACHE["names"] or []
        vectors = _CACHE["vectors"]
        if vectors is None or vectors.shape[0] == 0:
            logger.error("No enrolled faces in cache")
            return {"status": "error", "reason": "no_enrolled_faces", "name": None, "distance": None}

        logger.debug(f"Processing against {len(names)} enrolled faces")
        emb = embed_face(bgr)
        
        dists = np.linalg.norm(vectors - emb[None, :], axis=1)
        logger.debug(f"Computed distances: min={dists.min():.4f}, max={dists.max():.4f}")

        best_idx = int(np.argmin(dists))
        dist = float(dists[best_idx])
        name = names[best_idx]
        
        if dist > settings.max_distance:
            logger.info(f"Unknown face detected, distance {dist:.4f} > threshold {settings.max_distance}")
            return {"status": "unknown", "reason": None, "name": None, "distance": dist}

        logger.info(f"Face identified: {name} with distance {dist:.4f}")
        return {"status": "ok", "reason": None, "name": name, "distance": dist}
        
    except Exception as e:
        logger.error(f"Face identification error: {str(e)}", exc_info=True)
        return {"status": "error", "reason": f"identification_error: {str(e)}", "name": None, "distance": None}
