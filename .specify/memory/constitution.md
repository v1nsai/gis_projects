# GIS Projects Constitution

## Core Principles

### I. Readability First
Code is written for humans first, machines second. Every file
MUST be immediately understandable without cross-referencing
unrelated abstractions. Prefer explicit logic over clever
shortcuts. Docstrings on all functions; brief comments on
non-obvious blocks.

### II. Simplicity Over Scale
This is not production software. No distributed systems,
caching layers, or premature optimisation. Each sub-project
MUST be a straightforward script or module that does one job.
If a pattern does not directly solve the current problem, do
not add it.

### III. Reproduceability
Every data pipeline MUST produce deterministic results from
the same inputs. Pin dependency versions. Document the exact
steps to regenerate any output. Raw data and transformed
outputs MUST be storable in the repo.

### IV. Cost Awareness
When using paid third-party APIs (geocoding, satellite
imagery, etc.), ALWAYS check for free tiers or open
alternatives first. Log API usage per run. Fail gracefully on
quota exhaustion rather than retrying blindly. Prefer cached
results over repeated paid calls.

### V. Per-Project Independence
Each sub-project under `projects/` MUST be self-contained.
Shared code goes in `scripts/` only when it is genuinely
reused by two or more projects. No hidden cross-project
dependencies.

## Tech Stack & Conventions

- **Languages**: Python (requests, geojson, pipenv), TypeScript (React, Leaflet), Bash
- **Strict typing** in all Python and TypeScript code; avoid untyped JavaScript
- **Docstrings** on all functions explaining purpose and parameters
- **No third-party libraries** without explicit human consent
- **No automated testing** for now; manual verification is acceptable
- When in doubt, request human clarification rather than guessing intent

## Project Structure

- `projects/` — Individual GIS sub-projects (download, transform, analyse, display)
- `scripts/` — Shared utilities genuinely reused across sub-projects
- `data/` — Shared data assets
- `specs/` — Specifications and documentation

## Governance

This constitution is the single source of truth for project
conventions. All new sub-projects and modifications MUST
comply with these principles.

**Amendments**: Propose changes via commit message referencing
the principle being modified. Update the version and date on
approval.

**Version**: 1.0.0 | **Ratified**: 2026-08-31 | **Last Amended**: 2026-08-31
