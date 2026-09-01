# Tasks: Grocery Store Radius Search

**Input**: Design documents from `/specs/001-grocery-store-search/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Tests**: No automated tests (per constitution — manual verification only)

**Organization**: US1 and US2 are a single workflow (search → write GeoJSON). Implemented as one continuous task sequence.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add missing dependency to root Pipfile

- [x] T001 Add `python-dotenv` to root Pipfile packages in Pipfile

---

## Phase 2: Core Script — Argument Parsing & Config (FR-001, FR-002, FR-003, FR-011)

**Purpose**: CLI skeleton that parses `--center`, `--radius`, `--output` and loads API key from `.env`

- [x] T002 [US1] Create `scripts/find_grocery_stores.py` with module docstring explaining usage, parameters, and examples per FR-011
- [x] T003 [US1] Implement argument parsing for `--center "lat,lon"`, `--radius`, `--output` using `argparse` in `scripts/find_grocery_stores.py` per FR-001, FR-002, FR-003
- [x] T004 [US1] Implement `.env` loading via `python-dotenv` and `GOOGLE_MAPS_API_KEY` validation in `scripts/find_grocery_stores.py` — exit code 2 if missing
- [x] T005 [US1] Implement input validation in `scripts/find_grocery_stores.py`: parse lat/lon from `--center`, validate ranges (-90/90, -180/180), validate radius > 0 — exit code 1 on failure

---

## Phase 3: Google Maps Places API Integration (FR-004, FR-005, FR-006, FR-007, FR-009, FR-010)

**Purpose**: Query the API, handle pagination, deduplicate results

- [x] T006 [US1] Implement `search_nearby(api_key, lat, lon, radius_miles)` in `scripts/find_grocery_stores.py` — single-page Google Places Nearby Search request with `type=grocery_store`, convert miles to metres, return parsed results per FR-004, FR-005
- [x] T007 [US1] Implement pagination loop in `scripts/find_grocery_stores.py` — follow `next_page_token` with 3-second delay until exhausted, collect all results per FR-006
- [x] T008 [US1] Implement deduplication by `place_id` using a `set` in `scripts/find_grocery_stores.py` — skip duplicates during collection per FR-007
- [x] T009 [US1] Filter out non-`OPERATIONAL` businesses in `scripts/find_grocery_stores.py` — skip `business_status` != `OPERATIONAL`
- [x] T010 [US1] Implement API call counter in `scripts/find_grocery_stores.py` — log total calls made at end of run per FR-010
- [x] T011 [US1] Implement error handling for API failures in `scripts/find_grocery_stores.py` — HTTP errors, network issues, quota exhaustion — exit code 3 with descriptive message per FR-009

---

## Phase 4: GeoJSON Output (US2 — FR-008)

**Purpose**: Write valid GeoJSON FeatureCollection to the output path

- [x] T012 [US2] Implement `write_geojson(stores, output_path)` in `scripts/find_grocery_stores.py` — build FeatureCollection with Point features, properties: name, address, place_id per FR-008
- [x] T013 [US2] Handle empty results in `scripts/find_grocery_stores.py` — write valid FeatureCollection with empty features array, print message to stderr

---

## Phase 5: Main Orchestration & Edge Cases

**Purpose**: Wire everything together, handle edge cases from spec

- [x] T014 [US1] Implement `main()` function in `scripts/find_grocery_stores.py` — parse args → validate → load key → search → paginate → deduplicate → filter → write GeoJSON → log API count
- [x] T015 [US1] Add `if __name__ == "__main__": main()` entry point in `scripts/find_grocery_stores.py`
- [x] T016 [US1] Add warning for large radius (> 100 miles) in `scripts/find_grocery_stores.py` — results may be slow or incomplete per edge case spec

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** (Setup): No dependencies — can start immediately
- **Phase 2** (Argument Parsing): Depends on Phase 1 (python-dotenv in Pipfile)
- **Phase 3** (API Integration): Depends on Phase 2 (script skeleton exists)
- **Phase 4** (GeoJSON Output): Depends on Phase 3 (store data available)
- **Phase 5** (Orchestration): Depends on Phases 2-4 (all components exist)

### Parallel Opportunities

**No parallel opportunities** — single-file script with linear dependency chain.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Add python-dotenv to Pipfile
2. Complete Phase 2: Script parses args, loads API key
3. Complete Phase 3: Script queries API and returns stores
4. **STOP and VALIDATE**: Run script with real coordinates, verify stores returned
5. Complete Phase 4: GeoJSON written to file
6. **STOP and VALIDATE**: Load GeoJSON in GIS tool
7. Complete Phase 5: Edge cases handled

### Incremental Delivery

1. Phase 1 → Dependencies ready
2. Phase 2 → Script accepts arguments (test with `--help`)
3. Phase 3 → API query works (test with real coordinates)
4. Phase 4 → GeoJSON output works (test with GIS tool)
5. Phase 5 → Edge cases handled (test error paths)

---

## Notes

- All tasks target a single file: `scripts/find_grocery_stores.py`
- No automated tests — verify manually using quickstart.md scenarios
- `research.md` sections 4 (geocoding) and 5 (stdout output) are stale — removed from scope per clarifications
- API key loaded from `.env` file, not environment variable
- `--output` is required, not optional
- Distance not calculated client-side — API handles radius filtering
