"""
Find grocery stores within a given radius of a centre point.

Queries the Google Maps Places API (Nearby Search) for grocery
stores and writes results to a GeoJSON file.

Usage:
    python scripts/find_grocery_stores.py \\
        --center "45.5155,-122.6789" \\
        --radius 5.0 \\
        --output stores.geojson

Arguments:
    --center    Centre point as "lat,lon" (decimal degrees)
    --radius    Search radius in miles (> 0)
    --output    Path to write GeoJSON output file

Environment:
    GOOGLE_MAPS_API_KEY  Loaded from .env file in project root
"""

import argparse
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from geojson import Feature, FeatureCollection, Point

# Load .env from project root (parent of scripts/)
PROJECT_ROOT = os.getcwd()
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
MILES_TO_METRES = 1609.344
PAGE_DELAY_SECONDS = 3


def parse_args() -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Find grocery stores within a radius of a centre point."
    )
    parser.add_argument(
        "--center",
        required=True,
        help='Centre point as "lat,lon" (decimal degrees)',
    )
    parser.add_argument(
        "--radius",
        required=True,
        type=float,
        help="Search radius in miles (> 0)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write GeoJSON output file",
    )
    return parser.parse_args()


def validate_center(center_str: str) -> tuple[float, float]:
    """Parse and validate lat,lon from --center argument.

    Returns:
        Tuple of (latitude, longitude).

    Raises:
        SystemExit: If format is invalid or values out of range.
    """
    try:
        lat_str, lon_str = center_str.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except ValueError:
        print(
            "Error: --center must be in 'lat,lon' format (e.g. '45.5155,-122.6789')",
            file=sys.stderr,
        )
        sys.exit(1)

    if not (-90 <= lat <= 90):
        print(f"Error: latitude must be between -90 and 90, got {lat}", file=sys.stderr)
        sys.exit(1)

    if not (-180 <= lon <= 180):
        print(f"Error: longitude must be between -180 and 180, got {lon}", file=sys.stderr)
        sys.exit(1)

    return lat, lon


def validate_radius(radius: float) -> None:
    """Validate radius is positive.

    Raises:
        SystemExit: If radius <= 0.
    """
    if radius <= 0:
        print(f"Error: radius must be greater than 0, got {radius}", file=sys.stderr)
        sys.exit(1)


def load_api_key() -> str:
    """Load GOOGLE_MAPS_API_KEY from environment.

    Raises:
        SystemExit: If key is not set.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print(
            "Error: GOOGLE_MAPS_API_KEY not set. "
            "Add it to .env file in project root.",
            file=sys.stderr,
        )
        sys.exit(2)
    return api_key


def search_nearby(
    api_key: str, lat: float, lon: float, radius_miles: float
) -> dict:
    """Send a single Nearby Search request to Google Places API.

    Args:
        api_key: Google Maps API key.
        lat: Centre latitude.
        lon: Centre longitude.
        radius_miles: Search radius in miles.

    Returns:
        Parsed JSON response dict.

    Raises:
        SystemExit: On HTTP or API errors.
    """
    radius_metres = radius_miles * MILES_TO_METRES
    params = {
        "location": f"{lat},{lon}",
        "radius": radius_metres,
        "type": "grocery_store",
        "key": api_key,
    }

    try:
        resp = requests.get(GOOGLE_PLACES_URL, params=params, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Error: Network unavailable. Check your internet connection.", file=sys.stderr)
        sys.exit(3)
    except requests.exceptions.Timeout:
        print("Error: API request timed out.", file=sys.stderr)
        sys.exit(3)
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        print(f"Error: HTTP {status_code} from API", file=sys.stderr)
        sys.exit(3)
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(3)

    data = resp.json()
    status = data.get("status", "")

    if status == "REQUEST_DENIED":
        print(
            f"Error: API request denied: {data.get('error_message', 'unknown')}",
            file=sys.stderr,
        )
        sys.exit(3)
    elif status == "OVER_QUERY_LIMIT":
        print(
            "Error: API quota exceeded. Wait a moment and try again.",
            file=sys.stderr,
        )
        sys.exit(3)
    elif status not in ("OK", "ZERO_RESULTS"):
        print(f"Error: API returned status: {status}", file=sys.stderr)
        sys.exit(3)

    return data


def collect_all_stores(
    api_key: str, lat: float, lon: float, radius_miles: float
) -> list[dict]:
    """Collect all stores across paginated API results.

    Follows next_page_token until exhausted. Deduplicates by place_id.
    Filters out non-OPERATIONAL businesses.

    Returns:
        List of store dicts with keys: place_id, name, address, lat, lon.
    """
    seen_ids: set[str] = set()
    stores: list[dict] = []
    api_calls = 0
    next_page_token = None

    while True:
        api_calls += 1
        data = search_nearby(api_key, lat, lon, radius_miles)

        for place in data.get("results", []):
            place_id = place.get("place_id", "")
            if not place_id:
                continue

            # Skip duplicates
            if place_id in seen_ids:
                continue
            seen_ids.add(place_id)

            # Skip non-operational businesses
            if place.get("business_status") != "OPERATIONAL":
                continue

            location = place.get("geometry", {}).get("location", {})
            store = {
                "place_id": place_id,
                "name": place.get("name", "Unknown"),
                "address": place.get("vicinity", ""),
                "lat": location.get("lat", 0),
                "lon": location.get("lng", 0),
            }
            stores.append(store)

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

        # Google requires a delay before using next_page_token
        time.sleep(PAGE_DELAY_SECONDS)

    print(f"API calls made: {api_calls}", file=sys.stderr)
    return stores


def write_geojson(stores: list[dict], output_path: str) -> None:
    """Write stores to a GeoJSON FeatureCollection file.

    Args:
        stores: List of store dicts with place_id, name, address, lat, lon.
        output_path: Path to write the GeoJSON file.
    """
    features = []
    for store in stores:
        feature = Feature(
            geometry=Point((store["lon"], store["lat"])),
            properties={
                "name": store["name"],
                "address": store["address"],
                "place_id": store["place_id"],
            },
        )
        features.append(feature)

    collection = FeatureCollection(features)

    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)

    if not features:
        print("No grocery stores found in the specified area.", file=sys.stderr)
    else:
        print(f"Wrote {len(features)} stores to {output_path}", file=sys.stderr)


def main() -> None:
    """Main entry point: parse args, search API, write GeoJSON."""
    args = parse_args()
    lat, lon = validate_center(args.center)
    validate_radius(args.radius)
    api_key = load_api_key()

    # Warn about large radius
    if args.radius > 100:
        print(
            f"Warning: Large radius ({args.radius} mi) — "
            "results may be slow or incomplete.",
            file=sys.stderr,
        )

    stores = collect_all_stores(api_key, lat, lon, args.radius)
    write_geojson(stores, args.output)


if __name__ == "__main__":
    main()
