
import os, yaml, time, requests, pandas as pd, geopandas as gpd

def get_cfg():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    cfg = get_cfg()
    out_dir = cfg['output']['geojson_dir']
    csv_dir = cfg['output']['csv_dir']
    os.makedirs(csv_dir, exist_ok=True)

    parcels = gpd.read_file(os.path.join(out_dir,'ruhve_parcels.geojson'))
    if not cfg['ads']['enabled'] or not cfg['ads']['base_url']:
        # create empty mapping
        df = pd.DataFrame({'parcel_id': [], 'name_ads': []})
        df.to_csv(os.path.join(csv_dir,'ads_names.csv'), index=False)
        print('ADS disabled or base_url missing; produced empty ads_names.csv')
        return

    # Placeholder: you must adapt to actual ADS API schema. We leave a stub to join by geocode/coordinates if supported.
    # For now, emit empty ads_names.csv and rely on cadastral names.
    df = pd.DataFrame({'parcel_id': [], 'name_ads': []})
    df.to_csv(os.path.join(csv_dir,'ads_names.csv'), index=False)
    print('ADS stub written (implement when API details are known).')

if __name__ == '__main__':
    main()
