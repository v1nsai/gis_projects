# Data Model: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## API Response Fields (Google Places Nearby Search)

These are the fields returned by the Google Places API
Nearby Search endpoint. The script reads these directly.

| API Field | Type | Required | Description |
|-----------|------|----------|-------------|
| `place_id` | string | yes | Unique identifier for the place |
| `name` | string | yes | Display name of the store |
| `vicinity` | string | no | Short address (street + area) |
| `formatted_address` | string | no | Full address (if available) |
| `geometry.location.lat` | float | yes | Store latitude |
| `geometry.location.lng` | float | yes | Store longitude |
| `business_status` | string | no | e.g. `OPERATIONAL`, `CLOSED_TEMPORARILY` |
| `types` | list[string] | yes | e.g. `["grocery_store","supermarket","food","store"]` |
| `rating` | float | no | Average rating (0-5) |
| `opening_hours.open_now` | bool | no | Whether currently open |

**Note**: There is no `distance` field in the API response.
Distance from centre must be calculated client-side using
the Haversine formula.

## Script Input/Output Entities

### SearchInput

Parsed from CLI arguments.

| Field | Type | Required | Source |
|-------|------|----------|--------|
| center_lat | float | yes | `--center` (first half of "lat,lon") |
| center_lon | float | yes | `--center` (second half of "lat,lon") |
| radius_miles | float | yes | `--radius` |
| output_path | string | yes | `--output` |

### StoreResult

Internal representation after API call + client-side
distance calculation. Used to build GeoJSON output.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| place_id | string | yes | From API `place_id` |
| name | string | yes | From API `name` |
| address | string | no | From API `vicinity` or `formatted_address` |
| lat | float | yes | From API `geometry.location.lat` |
| lon | float | yes | From API `geometry.location.lng` |
| distance_miles | float | yes | Calculated client-side (Haversine) |

### GeoJSON Output

The output file follows the GeoJSON FeatureCollection spec.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [lon, lat]
      },
      "properties": {
        "name": "Store Name",
        "address": "123 Main St",
        "place_id": "ChIJ...",
        "distance_miles": 1.2
      }
    }
  ]
}
```

## Validation Rules

- `center_lat` must be between -90 and 90
- `center_lon` must be between -180 and 180
- `radius_miles` must be greater than 0
- `place_id` must be non-empty string
- `name` must be non-empty string
- `distance_miles` must be non-negative
- Only `OPERATIONAL` businesses are included in output
  (skip `CLOSED_TEMPORARILY` / `CLOSED_PERMANENTLY`)
