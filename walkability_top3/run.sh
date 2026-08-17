#!/bin/bash

# pull grocery store data from Google since Fairfax County doesn't provide any data on grocery stores specifically
python big3/run.py \
    --lat 38.882591 \
    --lng -77.171069 \
    --radius-miles 10 \
    --grid  \
    --grid-spacing 5 \
    --out data/10_falls_church.geojson

