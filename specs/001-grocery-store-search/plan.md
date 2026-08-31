# Implementation Plan: Grocery Store Radius Search

**Branch**: `001-grocery-store-search` | **Date**: 2026-08-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-grocery-store-search/spec.md`

## Summary

A Python CLI script that queries the Google Maps Places API
(Nearby Search) for grocery stores within a user-specified
mile radius of a centre point. Handles pagination via
`next_page_token` and deduplication by `place_id` to ensure
complete, non-duplicate results. Outputs a human-readable
list to stdout and optionally writes a GeoJSON file.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: requests, geojson, pipenv

**Storage**: None — results written to file on demand

**Testing**: Manual verification (no automated tests)

**Target Platform**: macOS / Linux CLI

**Project Type**: CLI script

**Performance Goals**: Results within 10 seconds for a
10-mile radius in a populated area

**Constraints**: Google Maps API rate limits and costs;
pagination delay (3-second token wait); max ~60 results per
request type

**Scale/Scope**: Single-user CLI tool, one sub-project

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Readability First | PASS | Docstrings on all functions; explicit logic |
| II. Simplicity Over Scale | PASS | Single script, no abstractions |
| III. Reproduceability | PASS | Pinned deps via Pipfile; deterministic output |
| IV. Cost Awareness | PASS | Logs API calls; user provides API key; no retry loops |
| V. Per-Project Independence | PASS | Self-contained under `projects/` |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-grocery-store-search/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli.md           # CLI interface contract
└── tasks.md             # Phase 2 output (not created by /speckit.plan)
```

### Source Code (repository root)

```text
projects/grocery-store-search/
├── Pipfile              # Python dependencies
├── Pipfile.lock         # Pinned versions
├── main.py              # Entry point
├── search.py            # Places API query + pagination logic
├── geo.py               # Distance calculation, mile-to-metre conversion
└── output.py            # GeoJSON file writing
```

**Structure Decision**: Single-project layout. The script
lives under `projects/grocery-store-search/` per the
constitution's per-project independence principle. Four
modules keep concerns separated without over-engineering:
entry point, API logic, geo utilities, and output formatting.

## Complexity Tracking

No constitution violations — no complexity tracking required.
