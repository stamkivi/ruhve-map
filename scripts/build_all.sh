
#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate || true
python etl/01_fetch_parcels.py
python etl/02_fetch_roads_buildings.py
python etl/03_fetch_ads_names.py
python etl/04_join_enrich.py
python etl/05_apply_overrides.py
echo "Build complete. Outputs in outputs/geojson and outputs/csv."
