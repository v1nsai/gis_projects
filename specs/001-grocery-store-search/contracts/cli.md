# CLI Interface Contract: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## Usage

```
python main.py <latitude> <longitude> <radius_miles> [OPTIONS]
```

## Positional Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| latitude | float | yes | Centre point latitude (-90 to 90) |
| longitude | float | yes | Centre point longitude (-180 to 180) |
| radius_miles | float | yes | Search radius in miles (> 0) |

## Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--output`, `-o` | string | none | Path to write GeoJSON file |
| `--place`, `-p` | string | none | Place name to geocode (overrides lat/long) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | yes | Google Maps Platform API key |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments or validation error |
| 2 | API key missing or invalid |
| 3 | API request failed (network, quota, etc.) |

## Stdout Format

Human-readable list, one store per line:

```
Found 47 grocery stores within 5.0 miles of (45.5155, -122.6789):

 1. Trader Joe's (0.3 mi)
    1234 NW Marshall St, Portland, OR 97209

 2. New Seasons Market (0.7 mi)
    5320 NE 33rd Ave, Portland, OR 97211

 ...
```

## Stderr Format

Error messages prefixed with `Error:` or `Warning:`:

```
Error: GOOGLE_MAPS_API_KEY environment variable not set.
Warning: Large radius (200.0 mi) — results may be slow or incomplete.
```

## GeoJSON Output

When `--output` is provided, writes a valid GeoJSON
FeatureCollection:

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
        "place_id": "ChIJ...",
        "distance_miles": 0.3
      }
    }
  ]
}
```

## Examples

```bash
# Search by coordinates
python main.py 45.5155 -122.6789 5.0

# Search with GeoJSON output
python main.py 45.5155 -122.6789 5.0 --output stores.geojson

# Search by place name
python main.py 0 0 1 --place "Downtown Portland, OR"
```
