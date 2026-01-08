import os
import re

HHMM_RE = re.compile(r"^\d{2}:\d{2}$")

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def is_valid_hhmm(value: str) -> bool:
    if not value or not HHMM_RE.match(value):
        return False
    hh, mm = value.split(":")
    h, m = int(hh), int(mm)
    return 0 <= h <= 23 and 0 <= m <= 59