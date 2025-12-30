# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This project generates an interactive map of Ruhve village (Saaremaa, Estonia) from Estonian Land Board (Maa- ja Ruumiamet) data. It consists of:
- **Python ETL pipeline** that fetches WFS data (parcels, buildings, roads), enriches with ADS names, and applies overrides
- **MapLibre GL JS web app** for interactive visualization with two-line labels (cadastral + ADS)
- **Export placeholder** for high-DPI PDF/SVG generation via QGIS/Mapnik

## Common Commands

### Initial Setup
```bash
# Create Python virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install web dependencies
npm install
```

### Running the ETL Pipeline
```bash
# Run complete ETL pipeline (all 5 steps)
bash scripts/build_all.sh

# Run individual ETL steps (must be run in order)
source .venv/bin/activate
python etl/01_fetch_parcels.py
python etl/02_fetch_roads_buildings.py
python etl/03_fetch_ads_names.py
python etl/04_join_enrich.py
python etl/05_apply_overrides.py
```

### Running the Web App
```bash
# Development server (localhost:5173)
npm run serve

# Build for production
npm run build
```

## Configuration

All configuration is in `config/config.yaml`:
- **WFS endpoints**: Configure Maa- ja Ruumiamet service URLs and layer names
- **CRS**: Default is EPSG:3301 (Estonian coordinate system)
- **Village name**: Filter admin boundaries by settlement name
- **ADS API**: Optional In-ADS endpoint for address data
- **Output paths**: Locations for GeoJSON, CSV, and tiles
- **Feature flags**: Enable/disable dual labels, leader lines, building-based highlighting

**IMPORTANT**: WFS URLs must be configured before running ETL. See `.env.sample` for optional environment variables.

## ETL Pipeline Architecture

The ETL pipeline runs in 5 sequential steps:

1. **01_fetch_parcels.py**: Fetches admin boundaries for the village, then fetches all parcels within that bounding box from WFS
2. **02_fetch_roads_buildings.py**: Fetches building footprints and road geometries using the same bounding box
3. **03_fetch_ads_names.py**: Optionally fetches ADS (address data system) names from In-ADS API and saves to CSV
4. **04_join_enrich.py**: Joins all data together:
   - Identifies parcel ID and name columns heuristically (`tunnus`, `nimi`)
   - Computes `has_bldg` by intersecting parcels with buildings
   - Joins ADS names from CSV (if available)
   - Calculates area in hectares
   - Builds two-line labels (`label1` = cadastral name/ID, `label2` = ADS name)
   - Outputs `parcels_enriched.geojson` and cleaned `roads.geojson`
5. **05_apply_overrides.py**: Applies manual overrides from `overrides/overrides.geojson`:
   - Can exclude parcels (`include: false`)
   - Can override label text (`label1`, `label2`)
   - Outputs final `parcels_final.geojson`

### Key Helper Function
`wfs_get_gdf(url, layer, bbox, crs_epsg)` in `01_fetch_parcels.py` is the reusable WFS fetcher that returns a GeoDataFrame. It handles WFS 1.0.0 requests with optional bounding box filtering.

## Web App Architecture

The web app (`web/index.html`) is a single-file MapLibre GL JS application:
- **Data loading**: Fetches GeoJSON files from `output/` (symlinked as `web/output`)
- **Layer structure**:
  - Background: Sea water highlighting (light blue polygon)
  - Village boundary (red dashed outline)
  - Roads layer (toggleable)
  - Parcels with conditional styling (highlight parcels with buildings)
  - Building footprints (red polygons)
  - Two separate label layers for `label1` and `label2` (creates two-line effect)
- **Interactivity**: Click parcels to see popup with details; hover for cursor change
- **Export function**: Creates offscreen map with higher pixel ratio for high-DPI exports

### Key Patterns
- Map initialization uses local style with no external basemap tiles
- All layers use inline GeoJSON sources loaded via fetch
- Labels use MapLibre's `symbol` layer type with text fields from properties
- Layer visibility toggled via `map.setLayoutProperty(layerId, 'visibility', 'visible'|'none')`
- Export creates a temporary map with `pixelRatio: 3` for 3x resolution

## Data Flow

```
config/config.yaml → ETL steps 01-05 → output/*.geojson → web app (MapLibre GL JS)
                                    ↓
                              outputs/csv/ruhve_parcels_debug.csv (for inspection)
```

Overrides are applied at the end: `overrides/overrides.geojson` can manually adjust which parcels to show and what labels to use.

## Legal & Attribution

- Respect Maa- ja Ruumiamet terms of service
- Include attribution on both web and print outputs
- Owner data is **intentionally excluded** unless provided via a legally compliant dataset
- No sensitive data should be committed to version control

## Development Notes

- The project is designed to be "Cursor-friendly" (minimal dependencies, single-file web app)
- `vite.config.js` sets root to `web/` directory with dev server on port 5173
- Python dependencies use GeoPandas/Shapely for spatial operations
- Web app has no build step for development (uses pre-bundled MapLibre GL JS)
- `print/export_map.py` is a placeholder for future QGIS/Mapnik integration
