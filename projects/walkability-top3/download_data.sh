#!/bin/bash

set -e # quit on error
source walkability_top3/.env

if [[ ! -n "${WMATA_API_KEY}" ]]; then
    echo "WMATA_API_KEY must be set in walkability_top3/.env"
    exit 1
fi

if [[ ! -n "${GOOGLE_MAPS_API_KEY}" ]]; then
    echo "GOOGLE_MAPS_API_KEY must be set in walkability_top3/.env"
    exit 1
fi

# Grocery store locations (from Google since FFX county doesn't seem to have a dataset for this)
python scripts/find_grocery_stores.py \
    --lat 38.882591 \
    --lng -77.171069 \
    --radius-miles 10 \
    --grid  \
    --grid-spacing 5 \
    --out data/10_falls_church.geojson

# Transit Stop Locations
## FFX Connector bus stop locations
curl -O --output-dir /tmp https://www.fairfaxcounty.gov/connector/sites/connector/files/assets/connector_gtfs.zip 
unzip /tmp/connector_gtfs.zip stops.txt -d /tmp
mv /tmp/stops.txt ./data/ffx_connector_bus_stops.csv
## WMATA Metrobus stop locations
curl -L \
  -H "api_key: $WMATA_API_KEY" \
  "https://api.wmata.com/gtfs/bus-gtfs-static.zip" \
  --output /tmp/bus-gtfs-static.zip
unzip /tmp/bus-gtfs-static.zip stops.txt -d /tmp
mv /tmp/stops.txt ./data/wmata_bus_stops.csv
## WMATA Metrorail station locations
curl -L \
  -H "api_key: $WMATA_API_KEY" \
  "https://api.wmata.com/gtfs/rail-gtfs-static.zip" \
  --output /tmp/rail-gtfs-static.zip
unzip /tmp/rail-gtfs-static.zip stops.txt -d /tmp
mv /tmp/stops.txt ./data/wmata_rail_stops.csv

# Housing Locations
curl -o ./data/housing_units.geojson 'https://hub.arcgis.com/api/v3/datasets/4f00b13df5a24cc19068bf356d3d1c45_1/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1'
## Housing Data dictionary
curl -o ./data/dictionaries/ipls-data-dictionary-gis.pdf https://www.fairfaxcounty.gov/demographics/sites/demographics/files/assets/datadictionary/ipls-data-dictionary-gis.pdf

