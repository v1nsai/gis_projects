# Feature Specification: Grocery Store Radius Search

**Feature Branch**: `001-grocery-store-search`

**Created**: 2026-08-31

**Status**: Draft

**Input**: User description: "Write a script that finds all the grocery stores in a given mile radius from a given center point and writes a geojson file with the results. Use Python and the Google Maps Places API. Use pagination and deduplication if necessary to make sure all grocery stores are found and displayed once and only once."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search by Coordinates (Priority: P1)

A user provides a latitude/longitude center point and a radius
in miles, then runs the script to get a list of all grocery
stores within that area.

**Why this priority**: Core functionality — without this the
feature has no value.

**Independent Test**: Run the script with known coordinates
(e.g., a city centre) and a reasonable radius (e.g., 5 miles).
Verify the output lists grocery stores that fall within the
specified distance.

**Acceptance Scenarios**:

1. **Given** a valid `--center "lat,lon"` and `--radius` and
   `--output` path, **When** the user runs the script, **Then**
   a GeoJSON file is written with all grocery stores within
   that radius.
2. **Given** a center point where no grocery stores exist
   nearby, **When** the user runs the script, **Then** the
   output GeoJSON is an empty FeatureCollection and a message
   indicates zero results found.
3. **Given** a radius of zero or a negative number, **When**
   the user runs the script, **Then** a clear error message is
   shown and the script exits.

---

### User Story 2 - Output as GeoJSON (Priority: P2)

The results are written to a GeoJSON file so the user can
visualise the stores on a map or feed them into other GIS
tools.

**Why this priority**: GeoJSON is the standard interchange
format for this project and enables downstream mapping.

**Independent Test**: Run the script, confirm a `.geojson`
file is produced with valid FeatureCollection structure
containing Point features for each store.

**Acceptance Scenarios**:

1. **Given** a successful search, **When** the script
   completes, **Then** a valid GeoJSON file is written to the
   specified output path.
2. **Given** a GeoJSON output, **When** inspected, **Then**
   each feature includes store name, address (if available),
   and coordinates.

---

### Edge Cases

- What happens when the API rate limit is hit? Script MUST
  report the error and suggest retrying later.
- What happens when the network is unavailable? Script MUST
  fail gracefully with a clear message.
- What happens when the search radius is extremely large
  (e.g., 500 miles)? Script MUST warn the user that results
  may be incomplete or very slow.
- What happens when a store has no name or address in the
  source data? Script MUST still include it with available
  fields.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a centre point via
  `--center` flag as `"lat,lon"` (decimal degrees, comma-separated).
- **FR-002**: System MUST accept a search radius in miles via
  `--radius` flag.
- **FR-003**: System MUST accept an output file path via
  `--output` flag for GeoJSON output.
- **FR-004**: System MUST query the Google Maps Places API
  (Nearby Search) for grocery store locations within the
  specified radius.
- **FR-005**: System MUST convert the mile radius to metres
  for the Google Maps API radius parameter.
- **FR-006**: System MUST handle API pagination by following
  `next_page_token` references until all results are retrieved.
- **FR-007**: System MUST deduplicate results by `place_id` to
  ensure each store appears exactly once in the output.
- **FR-008**: System MUST write results to the specified
  GeoJSON file path.
- **FR-009**: System MUST handle API errors and network
  failures gracefully with descriptive messages.
- **FR-010**: System MUST log the number of API calls made
  during a run (cost awareness).
- **FR-011**: System MUST include a docstring explaining usage,
  parameters, and examples.

### Key Entities

- **Search Request**: Centre point (lat, long), radius (miles),
  output file path. Represents the user's query.
- **Grocery Store**: Name, address (optional), coordinates
  (lat, long). Represents a single result.
- **Search Result**: Collection of grocery stores matching the
  query, plus metadata (total count, API calls made, execution
  time).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can run the script and receive results
  within 10 seconds for a 10-mile radius in a populated area.
- **SC-002**: Results include all grocery stores visible in
  the data source within the specified radius (no false
  negatives for well-known chains).
- **SC-003**: The GeoJSON output is valid and can be loaded
  into any GIS tool without errors.
- **SC-004**: API call count is logged so the user can track
  cost exposure for paid data sources.
- **SC-005**: Script can be run end-to-end with a single
  command and no manual configuration.

## Clarifications

### Session 2026-08-31

- Q: Where should the Python dependencies (requests, geojson)
  for this shared script be managed? → A: Use the root
  `Pipfile` — this is a shared utility, not project-specific.
- Q: What CLI arguments should the script accept? → A: Exactly
  three named flags: `--center "lat,lon"`, `--radius "miles"`,
  `--output "path/to/file.geojson"`. No positional args, no
  `--place` geocoding.
- Q: How should the script load the Google Maps API key? → A:
  Read from `.env` file in the project root using
  `python-dotenv`.

## Assumptions

- The user has a working internet connection for API queries.
- The user has a valid Google Maps Platform API key with
  Places API enabled. The script reads it from the
  `GOOGLE_MAPS_API_KEY` variable in a `.env` file at the
  project root, loaded via `python-dotenv`.
- Google Maps Places API is the chosen data source. The user
  explicitly requested this over free/open alternatives, accepting
  the associated cost implications.
- Google Maps Nearby Search returns up to 20 results per page;
  pagination via `next_page_token` is required for complete
  coverage in dense areas.
- "Grocery stores" includes supermarkets, convenience stores
  selling food, and similar retail food outlets — not
  restaurants or cafes. The `type=grocery_store` filter is used.
- This is a **shared script** located at
  `scripts/find_grocery_stores.py`, not a standalone sub-project.
  It is reused across multiple projects per Principle V of the
  constitution.
- Python dependencies (requests, geojson, python-dotenv) are
  managed by the root `Pipfile`.
- The `--output` argument is required. Results are always
  written to a GeoJSON file; no stdout output is produced.
