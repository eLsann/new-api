import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Person, Embedding
from app.recog import embed_face, rebuild_cache
from app.admin_auth import get_current_admin  # JWT dependency

router = APIRouter(prefix="/admin", tags=["admin"])


def _vec_to_csv(v: np.ndarray) -> str:
    return ",".join(f"{x:.6f}" for x in v.tolist())


@router.get("/persons")
def list_persons(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    persons = db.query(Person).order_by(Person.name.asc()).all()
    return [{"id": p.id, "name": p.name} for p in persons]


@router.post("/persons")
def create_person(
    payload: dict,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    exists = db.query(Person).filter(Person.name == name).one_or_none()
    if exists:
        return {"id": exists.id, "name": exists.name, "created": False}

    p = Person(name=name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name, "created": True}


def augment_image(bgr: np.ndarray) -> list:
    """Generate augmented versions of an image for stronger embeddings"""
    augmented = [bgr]  # Original
    
    # 1. Horizontal flip
    flipped = cv2.flip(bgr, 1)
    augmented.append(flipped)
    
    # 2. Brightness variations (+20%, -20%)
    bright = cv2.convertScaleAbs(bgr, alpha=1.2, beta=10)
    dark = cv2.convertScaleAbs(bgr, alpha=0.8, beta=-10)
    augmented.append(bright)
    augmented.append(dark)
    
    # 3. Slight rotation (+5°, -5°)
    h, w = bgr.shape[:2]
    center = (w // 2, h // 2)
    for angle in [5, -5]:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        augmented.append(rotated)
    
    return augmented  # Returns 6 images total


@router.post("/persons/{person_id}/enroll")
async def enroll_person(
    person_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    person = db.query(Person).filter(Person.id == person_id).one_or_none()
    if person is None:
        raise HTTPException(status_code=404, detail="person not found")

    if not files:
        raise HTTPException(status_code=400, detail="no files uploaded")

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024

    added = 0
    skipped = 0
    augmented_count = 0

    for f in files:
        if f.filename:
            import os
            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                skipped += 1
                continue

        img_bytes = await f.read()
        
        if not img_bytes or len(img_bytes) > MAX_FILE_SIZE:
            skipped += 1
            continue

        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            skipped += 1
            continue

        h, w = bgr.shape[:2]
        if max(h, w) > 1000:
            scale = 1000 / max(h, w)
            bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)))

        # Generate augmented images
        aug_images = augment_image(bgr)
        
        for aug_img in aug_images:
            try:
                emb = embed_face(aug_img)
                db.add(Embedding(person_id=person.id, vec_csv=_vec_to_csv(emb)))
                augmented_count += 1
            except Exception:
                continue
        
        added += 1

    db.commit()
    rebuild_cache(db)

    return {
        "ok": True,
        "person_id": person.id,
        "name": person.name,
        "images_processed": added,
        "embeddings_added": augmented_count,
        "skipped": skipped,
    }



@router.delete("/persons/{person_id}")
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    person = db.query(Person).filter(Person.id == person_id).one_or_none()
    if person is None:
        raise HTTPException(status_code=404, detail="person not found")

    db.query(Embedding).filter(Embedding.person_id == person_id).delete()
    db.delete(person)
    db.commit()

    rebuild_cache(db)
    return {"ok": True, "deleted_person_id": person_id}

@router.post("/rebuild_cache")
def rebuild_cache_endpoint(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    rebuild_cache(db)
    return {"ok": True}