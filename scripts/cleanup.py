import os
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_files(directory: str, days: int, pattern: str = "*"):
    """Delete files in directory older than 'days'"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Skipping {directory} (not found)")
        return 0

    cutoff = time.time() - (days * 86400)
    count = 0
    deleted_size = 0

    print(f"Scanning {directory} for files older than {days} days...")

    for file_path in dir_path.glob(pattern):
        if not file_path.is_file():
            continue

        try:
            mtime = file_path.stat().st_mtime
            if mtime < cutoff:
                size = file_path.stat().st_size
                file_path.unlink()
                count += 1
                deleted_size += size
                print(f"  Deleted: {file_path.name}")
        except Exception as e:
            print(f"  Error deleting {file_path.name}: {e}")

    mb = deleted_size / (1024 * 1024)
    print(f"Cleaned {count} files ({mb:.2f} MB)")
    return count

def main():
    parser = argparse.ArgumentParser(description="Cleanup old snapshots and logs")
    parser.add_argument("--days", type=int, default=30, help="Delete files older than N days (default: 30)")
    parser.add_argument("--snapshots", action="store_true", default=True, help="Clean snapshots")
    parser.add_argument("--logs", action="store_true", default=True, help="Clean logs")
    
    args = parser.parse_args()
    
    # Paths (relative to script location)
    # script is in newApi/scripts/, so root is ../
    root_dir = Path(__file__).parent.parent
    snapshot_dir = root_dir / "data" / "snapshots"
    log_dir = root_dir / "logs"

    total = 0
    if args.snapshots:
        total += cleanup_files(str(snapshot_dir), args.days, "*.jpg")
    
    if args.logs:
        total += cleanup_files(str(log_dir), args.days, "*.log")
        # Also clean rotated logs
        total += cleanup_files(str(log_dir), args.days, "*.log.*")

    print("="*40)
    print(f"Total files removed: {total}")
    print("="*40)

if __name__ == "__main__":
    main()
