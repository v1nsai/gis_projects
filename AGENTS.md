# Project Overview
This is a monorepo containing multiple GIS projects under the `projects/` folder that download, transform and analyze data, then generate a site to display the results.  Pay attention to the current feature spec being worked on, identified in the file `.specify/feature.json`.

# Tech Stack
- Python
    - requests
    - geojson
    - pipenv
- Typescript
    - reactjs
    - leaflet
- BASH

## Code Style
- Keep the code style simple, avoid unnecessary abstractions or unspecified unrequested features
- Use strict typing with all Python and Typescript (avoid Javascript if possible) code
- Add docstrings to functions that explain what they do, and add short comments to large code blocks to explain
- All scripts are designed to be run from the root of the project, no using `cd` before running

## Testing
- No tests for now, maybe in the future

## Things to Avoid
- DO NOT add third party libraries without human consent
- DO NOT guess about intent; request human clarification