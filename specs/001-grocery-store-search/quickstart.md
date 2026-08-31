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
cd projects/grocery-store-search
pipenv install
export GOOGLE_MAPS_API_KEY="your-api-key-here"
```

## Validation Scenarios

### Scenario 1: Basic search by coordinates

```bash
python main.py 45.5155 -122.6789 5.0
```

**Expected**: A numbered list of grocery stores within 5
miles of downtown Portland, OR, printed to stdout. Each entry
shows name, distance, and address.

### Scenario 2: GeoJSON output

```bash
python main.py 45.5155 -122.6789 5.0 --output test_stores.geojson
```

**Expected**: Same stdout output as Scenario 1, plus a file
`test_stores.geojson` is created. Validate with:

```bash
python -c "import json; d=json.load(open('test_stores.geojson')); print(d['type'], len(d['features']), 'features')"
# Expected: FeatureCollection N features (N > 0)
```

### Scenario 3: Search by place name

```bash
python main.py 0 0 1 --place "Pearl District, Portland, OR"
```

**Expected**: Script geocodes the place name and returns
grocery stores near that location.

### Scenario 4: Empty results

```bash
python main.py -33.8688 151.2093 0.5
```

**Expected**: Message indicating zero grocery stores found
in the specified radius (if testing in a very remote area).

### Scenario 5: Missing API key

```bash
unset GOOGLE_MAPS_API_KEY
python main.py 45.5155 -122.6789 5.0
```

**Expected**: Error message explaining the API key is not
set, with exit code 2.

### Scenario 6: Deduplication verification

Run a search in a dense area and check for duplicate place_ids:

```bash
python main.py 40.7128 -74.0060 2.0 --output nyc.geojson
python -c "
import json
d = json.load(open('nyc.geojson'))
ids = [f['properties']['place_id'] for f in d['features']]
print(f'Total: {len(ids)}, Unique: {len(set(ids))}')
assert len(ids) == len(set(ids)), 'Duplicates found!'
"
```

**Expected**: Total equals Unique — no duplicates.
