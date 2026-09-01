# Quickstart: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## Prerequisites

- Python 3.11+ installed
- `pipenv` installed (`pip install pipenv`)
- Google Maps Platform API key with Places API enabled
- Internet connection

## Setup

```bash
pipenv install
# Ensure .env file exists in project root with:
# GOOGLE_MAPS_API_KEY=your-api-key-here
```

## Validation Scenarios

### Scenario 1: Basic search

```bash
python scripts/find_grocery_stores.py \
  --center "45.5155,-122.6789" \
  --radius 5.0 \
  --output test_stores.geojson
```

**Expected**: A GeoJSON file `test_stores.geojson` is created
containing a FeatureCollection with Point features for each
grocery store within 5 miles of downtown Portland, OR.

### Scenario 2: Verify GeoJSON structure

```bash
python -c "import json; d=json.load(open('test_stores.geojson')); print(d['type'], len(d['features']), 'features')"
```

**Expected**: `FeatureCollection N features` (N > 0)

### Scenario 3: Empty results

```bash
python scripts/find_grocery_stores.py \
  --center "-33.8688,151.2093" \
  --radius 0.5 \
  --output empty.geojson
```

**Expected**: GeoJSON file created with empty FeatureCollection
(or message indicating zero stores found).

### Scenario 4: Missing API key

Remove or rename `.env` temporarily, or remove the
`GOOGLE_MAPS_API_KEY` line from it:

```bash
python scripts/find_grocery_stores.py \
  --center "45.5155,-122.6789" \
  --radius 5.0 \
  --output test.geojson
```

**Expected**: Error message explaining `GOOGLE_MAPS_API_KEY`
is not set in `.env`, with exit code 2.

### Scenario 5: Deduplication verification

```bash
python scripts/find_grocery_stores.py \
  --center "40.7128,-74.0060" \
  --radius 2.0 \
  --output nyc.geojson
python -c "
import json
d = json.load(open('nyc.geojson'))
ids = [f['properties']['place_id'] for f in d['features']]
print(f'Total: {len(ids)}, Unique: {len(set(ids))}')
assert len(ids) == len(set(ids)), 'Duplicates found!'
"
```

**Expected**: Total equals Unique — no duplicates.

### Scenario 6: Missing arguments

```bash
python scripts/find_grocery_stores.py --center "45.5155,-122.6789"
```

**Expected**: Error message indicating missing required
arguments (`--radius` and `--output`).
