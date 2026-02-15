# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Interactive map of Ruhve village (Saaremaa, Estonia) built from Estonian Land Board (Maa- ja Ruumiamet) WFS data. Two main components:
- **Python ETL pipeline** (`etl/01-05`) fetches WFS data (parcels, buildings, roads), enriches with ADS names, and applies overrides
- **MapLibre GL JS web app** (`web/index.html`) for interactive visualization with toggleable layers

## Common Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
npm install

# Run full ETL pipeline (steps must run in order)
bash scripts/build_all.sh

# Run individual ETL steps
source .venv/bin/activate
python etl/01_fetch_parcels.py    # Fetch admin boundaries + parcels from WFS
python etl/02_fetch_roads_buildings.py  # Fetch buildings + roads within bbox
python etl/03_fetch_ads_names.py  # Fetch ADS address names (stub)
python etl/04_join_enrich.py      # Join data, compute has_bldg, build labels
python etl/05_apply_overrides.py  # Apply manual overrides from overrides/overrides.geojson

# Dev server (localhost:5173)
npm run serve

# Production build (outputs to outputs/web-dist/)
npm run build
```

## Architecture

### ETL Pipeline Data Flow

```
config/config.yaml
    |
    v
01_fetch_parcels.py  --> output/ruhve_parcels.geojson (EPSG:3301)
02_fetch_roads_buildings.py --> output/buildings_raw.geojson, output/roads_raw.geojson
03_fetch_ads_names.py --> outputs/csv/ads_names.csv
04_join_enrich.py --> output/parcels_enriched.geojson, output/roads.geojson, outputs/csv/debug.csv
05_apply_overrides.py --> output/parcels_final.geojson
```

**CRS note**: ETL outputs are in EPSG:3301 (Estonian coordinate system). The web app loads `parcels_wgs84_proper.geojson` and `buildings_wgs84_proper.geojson` (WGS84/EPSG:4326). These WGS84 files are not produced by the current ETL scripts — they must be generated separately (e.g. via `gdf.to_crs(epsg=4326)`).

The `wfs_get_gdf(url, layer, bbox, crs_epsg)` helper is duplicated in both `01_fetch_parcels.py` and `02_fetch_roads_buildings.py`. It handles WFS 1.0.0 requests with optional bounding box filtering and returns a GeoDataFrame.

### Web App

Single-file app at `web/index.html` using pre-bundled MapLibre GL JS (no build step for development). Vite dev server (`vite.config.js`) sets root to `web/` and serves on port 5173.

Key details:
- Uses CARTO Positron basemap (`basemaps.cartocdn.com/gl/positron-gl-style/style.json`)
- Data loaded via `fetch('/output/...')` — relies on symlink `web/output -> ../output`
- Labels use single `l_aadress` property field (not the dual `label1`/`label2` from ETL)
- Layer visibility toggled via `map.setLayoutProperty(layerId, 'visibility', ...)`
- Export creates offscreen map with `preserveDrawingBuffer: true`, renders to PNG
- UI is in Estonian

Map layers (in order): sea background, village boundary, parcels outline, parcels highlight (has_bldg), T. family plots highlight, parcel labels, roads, road labels, buildings.

### Configuration

All in `config/config.yaml`:
- WFS endpoint URLs and layer names for parcels, buildings, roads, admin boundaries
- CRS (`crs_epsg: 3301`), village name filter
- ADS API settings (currently stub — `base_url` empty)
- Output paths for GeoJSON and CSV
- Feature flags: `dual_names`, `leader_lines`, `by_building_intersection`

`config/tamkivi_plots.yaml` holds cadastral codes for family plot highlighting (the "T. maad" toggle in the UI). These codes are currently hardcoded in `web/index.html`.

### Overrides

`overrides/overrides.geojson` is a GeoJSON FeatureCollection. Each feature's properties can:
- `parcel_id`: match against the parcel ID column
- `include: false`: exclude a parcel from output
- `label1`, `label2`: override label text

Currently empty (no overrides applied).

## Legal

- Owner data is intentionally excluded
- Include Maa- ja Ruumiamet attribution on all outputs
