#!/usr/bin/env python3
"""
SCOF Dataset Bootstrap & Integrity Utility
Manages Tier-2 heavy database bootstrap, compression, and local compilation.

Usage:
    python scripts/bootstrap_dataset.py --status     # Check current dataset and DB status
    python scripts/bootstrap_dataset.py --build      # Compile scof_relational.db from tracked CSVs/Parquets
    python scripts/bootstrap_dataset.py --compress   # Create scof_relational.db.zip for GitHub Release
    python scripts/bootstrap_dataset.py --download   # Download prebuilt DB from GitHub Release (if URL set)
"""

import os
import sys
import argparse
import sqlite3
import zipfile
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
DB_PATH = DATASETS_DIR / "scof_relational.db"
ZIP_PATH = DATASETS_DIR / "scof_relational.db.zip"

DEFAULT_RELEASE_URL = "https://github.com/Gowshick-sapien/SCOF_V1/releases/download/v2.0.0-data/scof_relational.db.zip"

def get_db_status():
    print("=== SCOF DATASET & DATABASE STATUS ===")
    if DB_PATH.exists():
        size_mb = DB_PATH.stat().st_size / (1024 * 1024)
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            conn.close()
            print(f"Status: READY")
            print(f"Database Path: {DB_PATH}")
            print(f"Size: {size_mb:.2f} MB")
            print(f"Total Tables: {len(tables)}")
            return True
        except Exception as e:
            print(f"Status: CORRUPTED ({e})")
            return False
    else:
        print(f"Status: NOT FOUND")
        print(f"Database Path: {DB_PATH}")
        print("Run `python scripts/bootstrap_dataset.py --build` to compile from local masters.")
        return False

def build_database():
    print(f"Building {DB_PATH.name} from tracked CSVs and Parquets...")
    loader_script = BASE_DIR / "scripts" / "load_postgresql_data.py"
    if not loader_script.exists():
        print(f"Error: Loader script not found at {loader_script}")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(loader_script)], cwd=str(BASE_DIR))
    if result.returncode == 0:
        print(f"Successfully compiled {DB_PATH.name}.")
        get_db_status()
    else:
        print(f"Compilation failed with exit code {result.returncode}.")
        sys.exit(result.returncode)

def compress_database():
    if not DB_PATH.exists():
        print(f"Error: {DB_PATH} does not exist. Run --build first.")
        sys.exit(1)

    print(f"Compressing {DB_PATH} ({DB_PATH.stat().st_size / (1024*1024):.2f} MB)...")
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(DB_PATH, arcname=DB_PATH.name)

    zip_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Created {ZIP_PATH} ({zip_mb:.2f} MB).")
    print(f"Compression Ratio: {(1 - zip_mb / (DB_PATH.stat().st_size / (1024*1024))) * 100:.1f}% reduction.")
    print("This file can be uploaded as a GitHub Release asset (well within GitHub's 2.0 GB release limit).")

def download_database(url: str = DEFAULT_RELEASE_URL):
    import urllib.request
    print(f"Downloading prebuilt database from: {url}")
    print(f"Target: {ZIP_PATH}")
    try:
        urllib.request.urlretrieve(url, ZIP_PATH)
        print("Download complete. Extracting...")
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            zf.extractall(DATASETS_DIR)
        ZIP_PATH.unlink()
        print("Extraction complete.")
        get_db_status()
    except Exception as e:
        print(f"Download failed: {e}")
        print("Fallback: Use `python scripts/bootstrap_dataset.py --build` to compile locally.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SCOF Dataset Bootstrap Utility")
    parser.add_argument("--status", action="store_true", help="Check database and dataset readiness")
    parser.add_argument("--build", action="store_true", help="Compile SQLite database from local files")
    parser.add_argument("--compress", action="store_true", help="Compress SQLite database for release upload")
    parser.add_argument("--download", type=str, nargs="?", const=DEFAULT_RELEASE_URL, help="Download prebuilt database from release URL")
    
    args = parser.parse_args()

    if args.compress:
        compress_database()
    elif args.build:
        build_database()
    elif args.download:
        download_database(args.download)
    else:
        get_db_status()

if __name__ == "__main__":
    main()
