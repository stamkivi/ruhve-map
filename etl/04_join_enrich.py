
import os, yaml, pandas as pd, geopandas as gpd
from shapely.geometry import shape

def get_cfg():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    cfg = get_cfg()
    out_dir = cfg['output']['geojson_dir']
    csv_dir = cfg['output']['csv_dir']
    os.makedirs(out_dir, exist_ok=True); os.makedirs(csv_dir, exist_ok=True)

    parcels = gpd.read_file(os.path.join(out_dir,'ruhve_parcels.geojson'))
    buildings = gpd.read_file(os.path.join(out_dir,'buildings_raw.geojson'))
    roads = gpd.read_file(os.path.join(out_dir,'roads_raw.geojson'))

    # Identify id and name columns heuristically
    pid_col = next((c for c in parcels.columns if 'tunnus' in c.lower() or 'id'==c.lower()), 'parcel_id')
    if pid_col not in parcels.columns:
        parcels[pid_col] = parcels.index.astype(str)

    # Cadastral unit name column (if any)
    name_cp_col = next((c for c in parcels.columns if 'nimi' in c.lower() or 'name' in c.lower()), None)

    # Compute has_bldg
    parcels['has_bldg'] = parcels.geometry.apply(lambda g: buildings.intersects(g).any())

    # Join ADS names (if available)
    ads_csv = os.path.join(csv_dir,'ads_names.csv')
    name_ads = None
    if os.path.exists(ads_csv):
        ads_df = pd.read_csv(ads_csv)
        if 'parcel_id' in ads_df.columns and 'name_ads' in ads_df.columns:
            name_ads = ads_df.set_index('parcel_id')['name_ads']
    if name_ads is not None:
        parcels['name_ads'] = parcels[pid_col].map(name_ads).fillna('')
    else:
        parcels['name_ads'] = ''

    # Normalize fields
    parcels.rename(columns={name_cp_col:'name_cp'} if name_cp_col else {}, inplace=True)
    if 'name_cp' not in parcels.columns: parcels['name_cp'] = ''

    # Area in hectares
    parcels['area_ha'] = parcels.geometry.area / 10000.0

    # Label text (two-line)
    def build_label(row):
        line1 = row.get('name_cp') or row.get(pid_col) or ''
        line2 = row.get('name_ads') or ''
        return (line1.strip(), line2.strip())
    lab = parcels.apply(build_label, axis=1, result_type='expand')
    parcels['label1'] = lab[0]; parcels['label2'] = lab[1]

    # Save enriched outputs
    parcels.to_file(os.path.join(out_dir,'parcels_enriched.geojson'), driver='GeoJSON')
    roads.to_file(os.path.join(out_dir,'roads.geojson'), driver='GeoJSON')

    # Debug CSV (no owners)
    dbg_cols = [pid_col, 'name_cp', 'name_ads', 'area_ha', 'has_bldg']
    parcels[dbg_cols].to_csv(os.path.join(csv_dir,'debug.csv'), index=False)
    print('Enrichment complete.')

if __name__ == '__main__':
    main()
