
# Ruhve Map (Cursor-ready)

A minimal, **Cursor-friendly** starter to build a beautiful, accurate map of **Ruhve (Saaremaa, Estonia)** with:
- **Python ETL** (GeoPandas/Shapely) to fetch WFS data (parcels, roads, buildings), enrich with ADS names, compute highlights.
- **MapLibre GL JS** web app for the **interactive** view (two-line labels: cadastral + ADS).
- An **export hook** to generate high-DPI **PDF/SVG** later via QGIS/Mapnik (placeholder included).

> **Note:** MaRu (Maa- ja Ruumiamet) endpoints vary by service. Fill in the WFS/WMS URLs in `config/config.yaml` before running ETL.
> Owner names are **intentionally excluded** unless you supply a legally compliant dataset.

## Quick start (inside Cursor)

1. Open folder in Cursor.
2. Create a Python venv and install deps:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Install web dev deps:
   ```bash
   npm install
   ```
4. Configure endpoints and options:
   - Copy `.env.sample` to `.env` (optional).
   - Edit `config/config.yaml` (set **WFS URLs** and **village_name: Ruhve**).
5. Run end-to-end build:
   ```bash
   bash scripts/build_all.sh
   ```
6. Launch the web app (in another terminal):
   ```bash
   npm run serve
   ```
   Open http://localhost:5173

## What you get

- **Interactive map** with:
  - Toggle between **two-line labels** (cadastral + ADS) vs **cadastral-only**.
  - Highlight parcels **with buildings**.
  - Search bar (placeholder wired for In-ADS; set endpoint in config to enable).
- **Debug CSV** with parcel list (id, names, area, has_bldg). No owners by default.
- **Overrides**: `overrides/overrides.geojson` lets you include/exclude or rename specific parcels.

## Exports (print later)
- `print/export_map.py` is a **placeholder** for headless QGIS/Mapnik export to **PDF/SVG** from the same snapshot.
- Once the visual style is approved, we wire this to your Export button or a CLI.

## Structure
```
etl/                 Python ETL pipeline (steps 01..05)
web/                 MapLibre app (Vite dev server)
overrides/           Manual per-parcel overrides
config/              Endpoints and switches
outputs/             GeoJSON, tiles, CSV (gitignored in real repo)
print/               Export placeholders
scripts/             Build convenience scripts
```

## Legal & attribution
- Respect Maa- ja Ruumiamet terms; include attribution on web & print. Owner data is **not** included unless you provide a lawful export.
- This scaffold stores no sensitive data in version control.
