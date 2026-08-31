# Data Model: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## Entities

### SearchRequest

Represents the user's query parameters.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| latitude | float | yes | Centre point latitude (-90 to 90) |
| longitude | float | yes | Centre point longitude (-180 to 180) |
| radius_miles | float | yes | Search radius in miles (> 0) |
| place_name | string | no | Optional place name to geocode |
| output_path | string | no | Path for GeoJSON file output |

### GroceryStore

Represents a single store result from the API.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| place_id | string | yes | Google Places unique identifier |
| name | string | yes | Store name |
| address | string | no | Street address (if available) |
| latitude | float | yes | Store latitude |
| longitude | float | yes | Store longitude |
| distance_miles | float | yes | Distance from centre point |

### SearchResult

Aggregated results returned to the user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| stores | list[GroceryStore] | yes | Deduplicated list of stores |
| total_count | int | yes | Number of stores found |
| api_calls | int | yes | Number of API requests made |
| search_request | SearchRequest | yes | The original query |

## Relationships

```
SearchRequest  1 ──── 1  SearchResult
SearchResult   1 ──── *  GroceryStore
```

## Validation Rules

- `latitude` must be between -90 and 90
- `longitude` must be between -180 and 180
- `radius_miles` must be greater than 0
- `place_id` must be non-empty string
- `name` must be non-empty string
- `distance_miles` must be non-negative
- If `place_name` is provided, `latitude`/`longitude` are
  derived from geocoding (user does not provide both)

## State Transitions

```
[User Input] ──geocode──▶ [Coordinates] ──search──▶ [Raw Results]
  │                                                    │
  │                                                    ├──paginate──▶ [All Pages]
  │                                                    │
  │◀──────────── output ◀────── deduplicate ◀──────────┘
```
