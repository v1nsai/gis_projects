#!/usr/bin/env python3
"""
Find walkability hotspots in Fairfax County, VA.

Identifies 1-mile radius areas where all three categories are present:
- Grocery stores
- Housing units
- Transit stops (FFX Connector, WMATA Bus, WMATA Rail)

Output: hotspots.geojson with polygons, and points_in_hotspots.geojson with all
points that fall within the hotspots.
"""

import argparse
import json
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

MILES_TO_METERS = 1609.344
# UTM Zone 18N for Fairfax County, VA
UTM_CRS = "EPSG:32618"
WGS84 = "EPSG:4326"


def load_geojson(path, category):
    """Load a GeoJSON file and add a category column."""
    gdf = gpd.read_file(path)
    gdf["category"] = category
    # Keep only needed columns
    cols = [c for c in gdf.columns if c != "geometry"]
    keep = [c for c in cols if c in ["name", "address", "place_id", "stop_name", "stop_id",
                                       "OBJECTID", "PIN", "CURRE_UNIT",
                                       "HOUSI_UNIT_TYPE", "category"]]
    return gdf[keep + ["geometry"]]


def load_csv(path, category, lat_col="stop_lat", lon_col="stop_lon"):
    """Load a CSV with lat/lon columns and convert to GeoDataFrame."""
    df = pd.read_csv(path)
    geometry = [Point(lon, lat) for lat, lon in zip(df[lat_col], df[lon_col])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=WGS84)
    gdf["category"] = category
    # Keep name columns if they exist
    keep_cols = [c for c in gdf.columns if c in ["stop_name", "stop_id", "category"]]
    return gdf[keep_cols + ["geometry"]]


def find_hotspots(grocery, housing, transit, radius_meters):
    """
    Find areas where all three categories are within radius_meters of each other.

    Strategy: Two-step intersection to avoid buffering 300K housing points.
    1. Buffer grocery and transit → intersect → candidate regions
    2. Use spatial index to find housing in candidates
    3. Buffer only those housing points → final intersection
    """
    print("Buffering grocery stores...")
    grocery_buf = grocery.copy()
    grocery_buf["geometry"] = grocery.geometry.buffer(radius_meters)
    grocery_dissolved = grocery_buf.dissolve().explode(index_parts=False).reset_index(drop=True)

    print("Buffering transit stops...")
    transit_buf = transit.copy()
    transit_buf["geometry"] = transit.geometry.buffer(radius_meters)
    transit_dissolved = transit_buf.dissolve().explode(index_parts=False).reset_index(drop=True)

    print("Intersecting grocery ∩ transit...")
    gt_intersection = gpd.overlay(grocery_dissolved, transit_dissolved, how="intersection")
    if gt_intersection.empty:
        print("No overlap between grocery and transit buffers")
        return None, None, None

    print(f"  Found {len(gt_intersection)} grocery-transit overlap regions")

    print("Finding housing units in candidate regions (spatial index)...")
    housing_sindex = housing.sindex
    candidate_indices = set()
    for geom in gt_intersection.geometry:
        possible_matches = housing_sindex.query(geom, predicate="intersects")
        candidate_indices.update(possible_matches)

    housing_in_candidates = housing.iloc[list(candidate_indices)].copy()
    print(f"  Found {len(housing_in_candidates)} housing units in candidate regions")

    if housing_in_candidates.empty:
        print("No housing units found in grocery-transit overlap regions")
        return None, None, None

    print("Buffering matched housing units...")
    housing_buf = housing_in_candidates.copy()
    housing_buf["geometry"] = housing_in_candidates.geometry.buffer(radius_meters)
    housing_dissolved = housing_buf.dissolve().explode(index_parts=False).reset_index(drop=True)

    print("Final 3-way intersection...")
    hotspots = gpd.overlay(gt_intersection, housing_dissolved, how="intersection")
    if hotspots.empty:
        print("No 3-way hotspots found")
        return None, None, None

    # Dissolve overlapping hotspot polygons
    hotspots_dissolved = hotspots.dissolve().explode(index_parts=False).reset_index(drop=True)
    hotspots_dissolved["hotspot_id"] = range(1, len(hotspots_dissolved) + 1)
    print(f"  Found {len(hotspots_dissolved)} hotspot polygons")

    return hotspots_dissolved, grocery, housing_in_candidates, transit


def find_points_in_hotspots(hotspots, grocery, housing, transit):
    """Find all original points that fall within hotspot polygons."""
    print("Finding points within hotspots...")

    def query_points(points_gdf, hotspots_gdf):
        sindex = points_gdf.sindex
        indices = set()
        for geom in hotspots_gdf.geometry:
            matches = sindex.query(geom, predicate="intersects")
            indices.update(matches)
        return points_gdf.iloc[list(indices)].copy() if indices else points_gdf.iloc[[]]

    grocery_in = query_points(grocery, hotspots)
    print(f"  Grocery stores in hotspots: {len(grocery_in)}")

    housing_in = query_points(housing, hotspots)
    print(f"  Housing units in hotspots: {len(housing_in)}")

    transit_in = query_points(transit, hotspots)
    print(f"  Transit stops in hotspots: {len(transit_in)}")

    # Combine all points
    all_points = pd.concat([grocery_in, housing_in, transit_in], ignore_index=True)
    return gpd.GeoDataFrame(all_points, geometry="geometry", crs=hotspots.crs)


def main():
    parser = argparse.ArgumentParser(description="Find walkability hotspots")
    parser.add_argument("--data-dir", default="data",
                        help="Directory containing input data files (default: data)")
    parser.add_argument("--radius-miles", type=float, default=1.0,
                        help="Radius in miles for proximity (default: 1)")
    parser.add_argument("--out-dir", default="site/walkability-top3",
                        help="Output directory (default: site/walkability-top3)")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    radius_meters = args.radius_miles * MILES_TO_METERS

    print(f"Loading data from {data_dir}/")

    # Load all datasets
    t0 = time.time()

    grocery = load_geojson(data_dir / "grocery_stores_10_mile_radius_falls_church.geojson", "Grocery")
    print(f"  Grocery: {len(grocery)} points")

    housing = load_geojson(data_dir / "housing_units.geojson", "Housing")
    print(f"  Housing: {len(housing)} points")

    transit_ffx = load_csv(data_dir / "ffx_connector_bus_stops.csv", "FFX Connector Bus Stop")
    transit_wmata_bus = load_csv(data_dir / "wmata_bus_stops.csv", "WMATA Bus Stop")
    transit_wmata_rail = load_csv(data_dir / "wmata_rail_stops.csv", "WMATA Train Station")
    transit = pd.concat([transit_ffx, transit_wmata_bus, transit_wmata_rail], ignore_index=True)
    transit = gpd.GeoDataFrame(transit, geometry="geometry", crs=WGS84)
    print(f"  Transit: {len(transit)} points (FFX: {len(transit_ffx)}, WMATA Bus: {len(transit_wmata_bus)}, WMATA Rail: {len(transit_wmata_rail)})")

    # Project to UTM for accurate buffering
    print(f"Projecting to UTM ({UTM_CRS})...")
    grocery = grocery.to_crs(UTM_CRS)
    housing = housing.to_crs(UTM_CRS)
    transit = transit.to_crs(UTM_CRS)

    # Find hotspots
    result = find_hotspots(grocery, housing, transit, radius_meters)
    if result[0] is None:
        print("No hotspots found. Exiting.")
        return

    hotspots, grocery_used, housing_used, transit_used = result

    # Find points in hotspots
    all_points = find_points_in_hotspots(hotspots, grocery_used, housing_used, transit_used)

    # Reproject to WGS84 for GeoJSON output
    print("Reprojecting to WGS84...")
    hotspots_wgs84 = hotspots.to_crs(WGS84)
    points_wgs84 = all_points.to_crs(WGS84)

    # Simplify hotspot geometries for file size
    hotspots_wgs84["geometry"] = hotspots_wgs84.geometry.simplify(0.0001)

    # Save outputs
    out_dir.mkdir(parents=True, exist_ok=True)

    hotspots_path = out_dir / "hotspots.geojson"
    hotspots_wgs84.to_file(hotspots_path, driver="GeoJSON")
    print(f"Wrote {len(hotspots_wgs84)} hotspot polygons → {hotspots_path}")

    points_path = out_dir / "points_in_hotspots.geojson"
    points_wgs84.to_file(points_path, driver="GeoJSON")
    print(f"Wrote {len(points_wgs84)} points in hotspots → {points_path}")

    # Summary
    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print(f"Hotspot summary:")
    for cat in points_wgs84["category"].unique():
        count = len(points_wgs84[points_wgs84["category"] == cat])
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
