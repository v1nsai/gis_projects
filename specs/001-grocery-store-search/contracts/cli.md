# CLI Interface Contract: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## Usage

```
python scripts/find_grocery_stores.py --center "lat,lon" --radius <miles> --output <path.geojson>
```

## Required Arguments

| Flag | Type | Description |
|------|------|-------------|
| `--center` | string | Centre point as `"lat,lon"` (decimal degrees) |
| `--radius` | float | Search radius in miles (> 0) |
| `--output` | string | Path to write GeoJSON output file |

## Configuration

| File | Variable | Required | Description |
|------|----------|----------|-------------|
| `.env` | `GOOGLE_MAPS_API_KEY` | yes | Google Maps Platform API key |

The script loads `GOOGLE_MAPS_API_KEY` from a `.env` file in
the project root using `python-dotenv`.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments or validation error |
| 2 | API key missing or invalid |
| 3 | API request failed (network, quota, etc.) |

## GeoJSON Output

Writes a valid GeoJSON FeatureCollection to the path specified
by `--output`:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-122.6789, 45.5155]
      },
      "properties": {
        "name": "Trader Joe's",
        "address": "1234 NW Marshall St, Portland, OR 97209",
        "place_id": "ChIJ..."
      }
    }
  ]
}
```

## Examples

```bash
# Search 5-mile radius around downtown Portland
python scripts/find_grocery_stores.py \
  --center "45.5155,-122.6789" \
  --radius 5.0 \
  --output stores.geojson

# Search 2-mile radius around a point in NYC
python scripts/find_grocery_stores.py \
  --center "40.7128,-74.0060" \
  --radius 2.0 \
  --output nyc_stores.geojson
```
