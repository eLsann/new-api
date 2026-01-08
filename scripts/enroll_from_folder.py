import os
import sys
import cv2
import numpy as np

sys.path.append(os.path.abspath("."))

from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import Person, Embedding
from app.recog import embed_face, rebuild_cache

Base.metadata.create_all(bind=engine)

def vec_to_csv(v: np.ndarray) -> str:
    return ",".join(f"{x:.6f}" for x in v.tolist())

def iter_image_files(folder: str):
    for fn in os.listdir(folder):
        path = os.path.join(folder, fn)
        if not os.path.isfile(path):
            continue
        lower = fn.lower()
        if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
            yield path

def main(dataset_dir: str):
    db: Session = SessionLocal()
    enrolled_people = 0
    total_images = 0
    try:
        for name in sorted(os.listdir(dataset_dir)):
            person_dir = os.path.join(dataset_dir, name)
            if not os.path.isdir(person_dir):
                continue

            img_paths = list(iter_image_files(person_dir))
            if not img_paths:
                print(f"[SKIP] {name}: no images")
                continue

            person = db.query(Person).filter(Person.name == name).one_or_none()
            if person is None:
                person = Person(name=name)
                db.add(person)
                db.commit()
                db.refresh(person)

            added = 0
            for path in img_paths:
                bgr = cv2.imread(path)
                if bgr is None:
                    print(f"  [BAD] {name}: cannot read {path}")
                    continue

                h, w = bgr.shape[:2]
                if max(h, w) > 1000:
                    scale = 1000 / max(h, w)
                    bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)))

                emb = embed_face(bgr)
                row = Embedding(person_id=person.id, vec_csv=vec_to_csv(emb))
                db.add(row)
                added += 1
                total_images += 1

            db.commit()
            if added > 0:
                enrolled_people += 1
                print(f"[OK] {name}: added {added} embeddings")

        rebuild_cache(db)
        print(f"\nDone. people_updated={enrolled_people}, total_images={total_images}")
        print("Cache rebuilt.")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/enroll_from_folder.py <dataset_dir>")
        raise SystemExit(1)
    main(sys.argv[1])