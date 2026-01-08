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

    added = 0
    skipped = 0

    for f in files:
        img_bytes = await f.read()
        if not img_bytes:
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

        try:
            emb = embed_face(bgr)
        except Exception:
            skipped += 1
            continue

        db.add(Embedding(person_id=person.id, vec_csv=_vec_to_csv(emb)))
        added += 1

    db.commit()
    rebuild_cache(db)

    return {
        "ok": True,
        "person_id": person.id,
        "name": person.name,
        "embeddings_added": added,
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