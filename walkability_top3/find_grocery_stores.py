#!/usr/bin/env python3
"""Find grocery stores near a GPS point using the Google Places API.
 
Searches for grocery stores within a given radius of a latitude/longitude
point and writes the results to a GeoJSON file. By default, performs a
single Places API "Nearby Search" call. Because Nearby Search caps out at
~60 results, an optional grid mode (--grid) runs multiple overlapping
searches across the radius for more thorough coverage of dense areas, at
the cost of additional API calls.
 
Requires:
    pip install requests
 
API key:
    Create a file named ".env" in the same directory as this script
    containing a single line:
        GOOGLE_MAPS_API_KEY=your_api_key_here
    The script raises an error if no .env file is found next to it.

Flags:
    --lat FLOAT                 Center latitude. Required.
    --lng FLOAT                 Center longitude. Required.
    --radius-miles FLOAT        Search radius in miles. Default: 5.
    --out PATH                  Output GeoJSON file path. Default: grocery_stores.geojson.
    --keyword STR                Optional extra keyword to narrow results, e.g. "supermarket".
                                  Default: none.
    --grid                       Use a grid of overlapping searches instead of a single
                                  search, for more thorough coverage of dense areas. Uses
                                  many more API calls -- see --dry-run to estimate first.
    --grid-spacing-miles FLOAT   Spacing between grid points in miles, used only with
                                  --grid. Smaller spacing means more thorough coverage but
                                  a roughly quadratic increase in API calls. Default: 2.
    --dry-run                    Print the grid point count (if --grid) and an estimated
                                  API call range, then exit without calling the API,
                                  requiring an API key, or writing a file.
 
Usage:
    python grocery_stores_geojson.py --lat <latitude> --lng <longitude> --radius-miles 5 --out stores.geojson
    python grocery_stores_geojson.py --lat <latitude> --lng <longitude> --radius-miles 10 --grid --grid-spacing 5 --dry-run
 
Notes:
    - Uses the Places API "Nearby Search" endpoint with type=grocery_or_supermarket.
    - Google caps nearby-search radius at 50,000 meters, so a 5-mile radius is fine.
    - Nearby Search returns at most 60 results (20 per page, up to 3 pages) since
      it's built for "search near a point", not exhaustive coverage of an area.
      If you need every store in a dense area, consider a grid of overlapping
      searches -- see the --grid option below.
    - You need a Google Cloud project with the "Places API" enabled and billing
      set up. Nearby Search calls are billed per request (check current pricing).
"""

import argparse
import json
import os
import sys
import time
from math import cos, radians
from pathlib import Path

import requests

PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
MILES_TO_METERS = 1609.344

def fetch_nearby_grocery_stores(lat, lng, radius_meters, api_key, keyword=None):
    """Fetch grocery stores near (lat, lng) within radius_meters, following pagination."""
    results = []
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "type": "grocery_or_supermarket",
        "key": api_key,
    }
    if keyword:
        params["keyword"] = keyword

    next_page_token = None
    page = 1
    while True:
        if next_page_token:
            params = {"pagetoken": next_page_token, "key": api_key}

        resp = requests.get(PLACES_NEARBY_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            print(
                f"Warning: Places API returned status '{status}': "
                f"{data.get('error_message', '')}",
                file=sys.stderr,
            )
            break

        results.extend(data.get("results", []))
        next_page_token = data.get("next_page_token")

        if not next_page_token:
            break

        page += 1
        # Google requires a short delay before a next_page_token becomes valid.
        time.sleep(2)

    return results


def make_grid_points(center_lat, center_lng, radius_miles, spacing_miles=2.0):
    """
    Generate a grid of points covering a circle of radius_miles around the
    center, spaced spacing_miles apart. Used to work around Nearby Search's
    ~60-result cap when you need more thorough coverage of a wide area.
    """
    points = []
    lat_step = spacing_miles / 69.0  # ~69 miles per degree latitude
    # miles per degree longitude shrinks with latitude
    miles_per_deg_lng = 69.0 * cos(radians(center_lat))
    lng_step = spacing_miles / miles_per_deg_lng if miles_per_deg_lng else spacing_miles / 69.0

    steps = int(radius_miles / spacing_miles) + 1
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            lat = center_lat + i * lat_step
            lng = center_lng + j * lng_step
            # keep only points roughly within the circle (rough distance check)
            dist_miles = (
                ((lat - center_lat) * 69.0) ** 2
                + ((lng - center_lng) * miles_per_deg_lng) ** 2
            ) ** 0.5
            if dist_miles <= radius_miles:
                points.append((lat, lng))
    return points


def build_geojson(places):
    """Convert a list of Google Places results into a GeoJSON FeatureCollection."""
    features = []
    seen_place_ids = set()

    for place in places:
        place_id = place.get("place_id")
        if place_id in seen_place_ids:
            continue
        seen_place_ids.add(place_id)

        location = place.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        if lat is None or lng is None:
            continue

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat],  # GeoJSON order is [lng, lat]
            },
            "properties": {
                "place_id": place_id,
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "business_status": place.get("business_status"),
                "types": place.get("types", []),
            },
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}


def main():
    # load .env file
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        raise FileNotFoundError(f"No .env file found at {env_path}")

    for line in env_path.read_text().splitlines():
        if line.strip() and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

    # check for google api key
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print(
            "Error: GOOGLE_MAPS_API_KEY not found in .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Find grocery stores near a GPS point and save as GeoJSON."
    )
    parser.add_argument("--lat", type=float, required=True, help="Center latitude")
    parser.add_argument("--lng", type=float, required=True, help="Center longitude")
    parser.add_argument(
        "--radius-miles", type=float, default=5.0, help="Search radius in miles (default: 5)"
    )
    parser.add_argument(
        "--out", type=str, default="grocery_stores.geojson", help="Output GeoJSON file path"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Optional extra keyword to narrow results, e.g. 'supermarket'",
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help=(
            "Use a grid of overlapping searches instead of a single search, to "
            "get more thorough coverage in dense areas (uses more API calls)."
        ),
    )
    parser.add_argument(
        "--grid-spacing-miles",
        type=float,
        default=2.0,
        help="Spacing between grid points in miles when --grid is used (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Don't call the API or write a file. Just print how many grid points "
            "(if --grid) and roughly how many API calls the run would use, then exit."
        ),
    )
    args = parser.parse_args()

    if args.dry_run:
        if args.grid:
            points = make_grid_points(
                args.lat, args.lng, args.radius_miles, args.grid_spacing_miles
            )
            min_calls = len(points)
            max_calls = len(points) * 3  # up to 3 pages per point
            print(f"Grid mode: {len(points)} grid points "
                  f"(spacing={args.grid_spacing_miles} mi, radius={args.radius_miles} mi)")
            print(f"Estimated API calls: {min_calls} (min) to {max_calls} (max, "
                  f"if every point's results paginate fully)")
        else:
            print(f"Single-search mode: radius={args.radius_miles} mi (capped at 50,000 m)")
            print("Estimated API calls: 1 (min) to 3 (max, if results paginate fully)")
        return

    radius_meters = min(args.radius_miles * MILES_TO_METERS, 50000)

    all_results = []

    if args.grid:
        points = make_grid_points(args.lat, args.lng, args.radius_miles, args.grid_spacing_miles)
        # For grid search, use a smaller per-point radius matching the spacing
        per_point_radius = min(args.grid_spacing_miles * MILES_TO_METERS, 50000)
        print(f"Grid mode: searching {len(points)} points...", file=sys.stderr)
        for idx, (plat, plng) in enumerate(points, start=1):
            print(f"  [{idx}/{len(points)}] ({plat:.4f}, {plng:.4f})", file=sys.stderr)
            results = fetch_nearby_grocery_stores(
                plat, plng, per_point_radius, api_key, args.keyword
            )
            all_results.extend(results)
    else:
        all_results = fetch_nearby_grocery_stores(
            args.lat, args.lng, radius_meters, api_key, args.keyword
        )

    geojson = build_geojson(all_results)

    with open(args.out, "w") as f:
        json.dump(geojson, f, indent=2)

    print(
        f"Wrote {len(geojson['features'])} grocery store(s) to {args.out}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()