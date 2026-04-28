
import os, sys, yaml, requests, geopandas as gpd
from urllib.parse import urlencode
from pyproj import CRS

def get_cfg():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def wfs_get_gdf(url, layer, bbox=None, crs_epsg=3301, extra_params=None):
    params = {
        'service':'WFS','version':'1.0.0','request':'GetFeature',
        'typeName':layer,'outputFormat':'application/json'
    }
    if bbox is not None:
        # For WFS 1.0.0, bbox format is: minx,miny,maxx,maxy
        params['bbox'] = ','.join(map(str, bbox))
    if extra_params:
        params.update(extra_params)
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    gdf = gpd.read_file(r.text)
    if gdf.crs is None:
        gdf.set_crs(epsg=crs_epsg, inplace=True)
    return gdf

def main():
    cfg = get_cfg()
    print(f"Fetching admin boundaries for '{cfg['village_name']}'...")
    
    # Get admin boundaries (fetch all and filter locally)
    admin_gdf = wfs_get_gdf(
        cfg['services']['admin_wfs_url'],
        cfg['services']['admin_layer']
    )
    
    if admin_gdf.empty:
        print(f"❌ No admin boundaries found")
        return
    
    # Find the settlement name column
    name_col = None
    for col in admin_gdf.columns:
        if 'asustusyksus' in col.lower():
            name_col = col
            break
    
    if name_col is None:
        print("❌ Could not find settlement name column")
        print(f"Available columns: {admin_gdf.columns.tolist()}")
        return
    
    # Filter by village name
    village_mask = admin_gdf[name_col].str.contains(cfg['village_name'], case=False, na=False)
    village_gdf = admin_gdf[village_mask]
    
    if village_gdf.empty:
        print(f"❌ No admin boundaries found for '{cfg['village_name']}'")
        print(f"Available settlements: {admin_gdf[name_col].unique()}")
        return
    
    print(f"✅ Found admin boundaries for '{village_gdf[name_col].iloc[0]}'")
    
    # Get bounding box
    bbox = village_gdf.total_bounds  # [minx, miny, maxx, maxy]
    print(f"📦 Bbox: {bbox}")
    
    # Fetch parcels within bbox
    print(f"Fetching cadastral parcels...")
    parcels_gdf = wfs_get_gdf(
        cfg['services']['parcels_wfs_url'],
        cfg['services']['parcels_layer'],
        bbox=bbox
    )
    
    if parcels_gdf.empty:
        print("❌ No parcels found")
        return

    print(f"✅ Found {len(parcels_gdf)} parcels in bbox")

    # Filter parcels to those whose registered settlement (ay_nimi) matches the
    # configured village. Without this we leak parcels from neighbouring villages
    # that fall inside Ruhve's bounding box (Randvere, Viltina, Asva, ...).
    if 'ay_nimi' in parcels_gdf.columns:
        before = len(parcels_gdf)
        mask = parcels_gdf['ay_nimi'].str.contains(cfg['village_name'], case=False, na=False)
        dropped = parcels_gdf.loc[~mask, 'ay_nimi'].value_counts()
        parcels_gdf = parcels_gdf[mask].copy()
        print(f"🔎 Filtered by ay_nimi: {before} → {len(parcels_gdf)}")
        if not dropped.empty:
            print(f"   Dropped from other settlements: {dropped.to_dict()}")
    else:
        print("⚠️  Parcels have no ay_nimi column — skipping settlement filter")
    
    # Save to output
    os.makedirs(cfg['output']['geojson_dir'], exist_ok=True)
    output_path = os.path.join(cfg['output']['geojson_dir'], 'ruhve_parcels.geojson')
    parcels_gdf.to_file(output_path, driver='GeoJSON')
    print(f"💾 Saved parcels to {output_path}")

if __name__ == '__main__':
    main()
