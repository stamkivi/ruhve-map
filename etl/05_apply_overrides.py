
import os, json, yaml, geopandas as gpd, pandas as pd
from shapely.geometry import shape

def get_cfg():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    cfg = get_cfg()
    out_dir = cfg['output']['geojson_dir']
    ovr_path = cfg['overrides']['path']
    enriched_path = os.path.join(out_dir,'parcels_enriched.geojson')
    parcels = gpd.read_file(enriched_path)

    if os.path.exists(ovr_path) and os.path.getsize(ovr_path) > 0:
        with open(ovr_path,'r',encoding='utf-8') as f:
            ovr = json.load(f)
        # Expect properties: {parcel_id, include (bool, default True), label1?, label2?}
        pid_col = next((c for c in parcels.columns if 'tunnus' in c.lower() or c.lower()=='parcel_id'), None)
        if pid_col is None:
            pid_col = 'parcel_id'
            if pid_col not in parcels.columns:
                parcels[pid_col] = parcels.index.astype(str)
        include_map = {}
        label1_map = {}
        label2_map = {}
        for feat in ovr.get('features', []):
            props = feat.get('properties', {})
            pid = props.get('parcel_id')
            if pid is None: continue
            if 'include' in props: include_map[pid] = bool(props['include'])
            if 'label1' in props: label1_map[pid] = props['label1']
            if 'label2' in props: label2_map[pid] = props['label2']

        def include_row(row):
            pid = row[pid_col]
            if pid in include_map:
                return include_map[pid]
            return True

        parcels = parcels[parcels.apply(include_row, axis=1)].copy()
        parcels['label1'] = parcels.apply(lambda r: label1_map.get(r[pid_col], r['label1']), axis=1)
        parcels['label2'] = parcels.apply(lambda r: label2_map.get(r[pid_col], r['label2']), axis=1)

    parcels.to_file(os.path.join(out_dir,'parcels_final.geojson'), driver='GeoJSON')
    print('Overrides applied.')

if __name__ == '__main__':
    main()
