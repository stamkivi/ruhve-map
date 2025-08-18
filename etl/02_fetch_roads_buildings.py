
import os, sys, yaml, geopandas as gpd
from shapely.geometry import box

def get_cfg():
    with open('config/config.yaml','r',encoding='utf-8') as f:
        return yaml.safe_load(f)

def wfs_get_gdf(url, layer, bbox=None, crs_epsg=3301, extra_params=None):
    import requests
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
    out_dir = cfg['output']['geojson_dir']
    os.makedirs(out_dir, exist_ok=True)
    epsg = cfg['crs_epsg']

    # Load parcels to get working extent
    parcels = gpd.read_file(os.path.join(out_dir,'ruhve_parcels.geojson'))
    ruhve_union = parcels.to_crs(epsg=epsg).unary_union
    bbox = list(ruhve_union.bounds)

    b_url = cfg['services']['buildings_wfs_url']
    b_layer = cfg['services']['buildings_layer']
    r_url = cfg['services']['roads_wfs_url']
    r_layer = cfg['services']['roads_layer']
    if not (b_url and b_layer and r_url and r_layer):
        raise SystemExit('Configure buildings/roads WFS in config/config.yaml first.')

    buildings = wfs_get_gdf(b_url, b_layer, bbox=bbox, crs_epsg=epsg)
    buildings = buildings[buildings.geometry.intersects(ruhve_union)].copy()
    buildings.to_file(os.path.join(out_dir,'buildings_raw.geojson'), driver='GeoJSON')

    roads = wfs_get_gdf(r_url, r_layer, bbox=bbox, crs_epsg=epsg)
    roads = roads[roads.geometry.intersects(ruhve_union)].copy()
    roads.to_file(os.path.join(out_dir,'roads_raw.geojson'), driver='GeoJSON')

    print(f"Fetched buildings: {len(buildings)}, roads: {len(roads)}")

if __name__ == '__main__':
    main()
