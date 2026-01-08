import numpy as np
import cv2
import torch
from PIL import Image
from sqlalchemy.orm import Session
from facenet_pytorch import InceptionResnetV1

from app.config import settings
from app.models import Person

_DEVICE = "cpu"
_MODEL = InceptionResnetV1(pretrained="vggface2").eval().to(_DEVICE)

_CACHE = {"names": None, "vectors": None}

def _csv_to_vec(s: str) -> np.ndarray:
    return np.fromstring(s, sep=",", dtype=np.float32)

def rebuild_cache(db: Session):
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
    bgr = _bytes_to_bgr(img_bytes)
    h, w = bgr.shape[:2]
    if min(h, w) < settings.min_face_px:
        return {"status": "reject", "reason": "face_crop_too_small", "name": None, "distance": None}

    if _CACHE["names"] is None:
        rebuild_cache(db)

    names = _CACHE["names"] or []
    vectors = _CACHE["vectors"]
    if vectors is None or vectors.shape[0] == 0:
        return {"status": "error", "reason": "no_enrolled_faces", "name": None, "distance": None}

    emb = embed_face(bgr)
    dists = np.linalg.norm(vectors - emb[None, :], axis=1)

    best_idx = int(np.argmin(dists))
    dist = float(dists[best_idx])
    name = names[best_idx]

    if dist > settings.max_distance:
        return {"status": "unknown", "reason": None, "name": None, "distance": dist}

    return {"status": "ok", "reason": None, "name": name, "distance": dist}