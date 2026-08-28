#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
DATA_DIR="$ROOT_DIR/data"
SITE_DIR="$ROOT_DIR/site/walkability-top3"

echo "================================================"
echo "  Fairfax County Walkability Hotspots - Builder"
echo "================================================"

# Step 1: Ensure virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual environment exists"
fi

# Step 2: Install dependencies
echo "[2/4] Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet geopandas pyproj requests geojson

# Step 3: Run the analysis
echo "[3/4] Running spatial analysis..."
"$PYTHON" "$SCRIPT_DIR/analyze.py" \
    --data-dir "$DATA_DIR" \
    --out-dir "$SITE_DIR"

# Step 4: Copy map files
echo "[4/4] Copying map files..."
mkdir -p "$SITE_DIR"
for file in "$SCRIPT_DIR/map"/*; do
    if [ -f "$file" ]; then
        cp "$file" "$SITE_DIR/"
        echo "  Copied $(basename "$file")"
    fi
done

echo ""
echo "================================================"
echo "  Build complete!"
echo "================================================"
echo ""
echo "Output: $SITE_DIR"
echo ""
echo "To preview locally:"
echo "  cd $SITE_DIR && python -m http.server 8000"
echo ""
