#!/usr/bin/env python3
"""
Build the walkability top3 map.

Runs the spatial analysis to find hotspots, then copies map files
to the site directory for GitHub Pages deployment.

Usage:
    python build_map.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
ROOT_DIR = PROJECT_DIR.parent.parent
DATA_DIR = ROOT_DIR / "data"
MAP_DIR = PROJECT_DIR / "map"
SITE_DIR = ROOT_DIR / "site" / "walkability-top3"


def main():
    print("=" * 60)
    print("Building walkability-top3 map")
    print("=" * 60)

    # Step 1: Run the analysis
    print("\n[1/2] Running spatial analysis...")
    result = subprocess.run(
        [
            sys.executable, str(PROJECT_DIR / "analyze.py"),
            "--data-dir", str(DATA_DIR),
            "--out-dir", str(SITE_DIR),
        ],
        cwd=str(ROOT_DIR),
    )
    if result.returncode != 0:
        print("Analysis failed!")
        sys.exit(1)

    # Step 2: Copy map files
    print("\n[2/2] Copying map files...")
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    for src_file in MAP_DIR.glob("*"):
        if src_file.is_file():
            dst = SITE_DIR / src_file.name
            shutil.copy2(src_file, dst)
            print(f"  Copied {src_file.name}")

    # Summary
    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Output: {SITE_DIR}")
    print("\nTo preview locally:")
    print(f"  cd {SITE_DIR} && python -m http.server 8000")
    print("=" * 60)


if __name__ == "__main__":
    main()
