# Research: Grocery Store Radius Search

**Date**: 2026-08-31
**Feature**: 001-grocery-store-search

## Decisions

### 1. Data Source: Google Maps Places API (Nearby Search)

**Decision**: Use Google Maps Places API Nearby Search
endpoint with `type=grocery_store`.

**Rationale**: User explicitly requested Google Maps Places
API. Provides structured, reliable data with place_ids for
deduplication. Supports radius-based search natively.

**Alternatives considered**:
- OpenStreetMap / Overpass API: Free, but data quality varies
  and query syntax is complex. User rejected this.
- Yelp Fusion API: Requires business account for production
  use; less straightforward radius search.

### 2. Pagination Strategy

**Decision**: Follow `next_page_token` until exhausted.
Google returns max 20 results per page; the token expires
after ~60 seconds and requires a 3-second delay before use.

**Rationale**: Google Places API caps at 20 results per
response. Dense urban areas frequently have more than 20
grocery stores within a reasonable radius. Pagination ensures
complete coverage.

**Alternatives considered**:
- Splitting radius into smaller sub-queries: More complex,
  still requires dedup, and may miss edge-boundary stores.
  Not worth the added complexity.

### 3. Deduplication Strategy

**Decision**: Deduplicate by `place_id` (Google's unique
identifier per place). Maintain a `set` of seen IDs; skip
duplicates during collection.

**Rationale**: `place_id` is the canonical unique key for
Google Places results. Pagination may return overlapping
results for边界 areas.

**Alternatives considered**:
- Name + address fuzzy matching: Error-prone, slower, and
  unnecessary when `place_id` is available.

### 4. Geocoding for Place Name Input

**Decision**: Use Google Maps Geocoding API (same API key)
when `--place` argument is provided.

**Rationale**: Already using Google Maps Platform; geocoding
uses the same key and billing account. Keeps dependencies
minimal.

**Alternatives considered**:
- Nominatim (OSM) geocoding: Free, but adds a second API
  dependency and inconsistent availability.

### 5. Output Format

**Decision**: Human-readable list to stdout (default) plus
optional GeoJSON file via `--output` flag.

**Rationale**: Matches spec FR-005 and FR-006. GeoJSON is the
project's standard interchange format.

**Alternatives considered**:
- CSV output: Less useful for GIS workflows.
- JSON output: Possible future addition; GeoJSON is a
  superset of JSON with coordinate semantics.

### 6. API Key Management

**Decision**: Read from `GOOGLE_MAPS_API_KEY` environment
variable. Fail with clear message if unset.

**Rationale**: Avoids hardcoding secrets. Standard practice
for CLI tools. Constitution prohibits committing secrets.

**Alternatives considered**:
- Config file: Adds complexity for a single key.
- CLI argument: Clutters the interface; key is long-lived,
  not per-run.
