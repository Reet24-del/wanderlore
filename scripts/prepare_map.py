#!/usr/bin/env python3
"""Online preparation only. Store an OSM extract for offline walking."""
import argparse
import json
from pathlib import Path
import httpx

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lat',type=float,required=True)
p.add_argument('--lon',type=float,required=True)
p.add_argument('--radius',type=int,default=1500)
p.add_argument('--endpoint',default='https://overpass-api.de/api/interpreter')
p.add_argument('--out',type=Path,default=Path('places.geojson'))
a=p.parse_args()
if not -90<=a.lat<=90 or not -180<=a.lon<=180 or not 100<=a.radius<=5000: p.error('Use valid coordinates and radius 100–5000 metres.')
query=f'''[out:json][timeout:60];(nwr(around:{a.radius},{a.lat},{a.lon})[name][leisure];nwr(around:{a.radius},{a.lat},{a.lon})[name][natural];nwr(around:{a.radius},{a.lat},{a.lon})[name][waterway];nwr(around:{a.radius},{a.lat},{a.lon})[name][tourism];);out geom;'''
print('Downloading public OSM places for this area. Coordinates are sent to Overpass during this preparation step only.')
try:
    r=httpx.get(a.endpoint,params={'data':query},headers={'User-Agent':'Wanderlore/0.1 (offline map preparation)'},timeout=90)
    r.raise_for_status()
except httpx.HTTPError as exc:
    raise SystemExit(f'Overpass could not provide this pack: {exc}. Retry later, or import an existing GeoJSON extract.') from exc
features=[]
for item in r.json()['elements']:
    if item['type']=='node': geometry={'type':'Point','coordinates':[item['lon'],item['lat']]}
    elif item['type']=='way' and item.get('geometry'):
        coords=[[v['lon'],v['lat']] for v in item['geometry'] if 'lon'in v and 'lat'in v]
        if len(coords)<2: continue
        # Waterways remain lines. A closed park is an area.
        is_area=len(coords)>=4 and coords[0]==coords[-1] and not item.get('tags',{}).get('waterway')
        geometry={'type':'Polygon','coordinates':[coords]} if is_area else {'type':'LineString','coordinates':coords}
    else: continue  # Do not use misleading relation centroids.
    features.append({'type':'Feature','id':f"{item['type']}/{item['id']}",'properties':item.get('tags',{}),'geometry':geometry})
if not features: raise SystemExit('No supported named features found. Try another area or import a richer GeoJSON extract.')
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps({'type':'FeatureCollection','attribution':'© OpenStreetMap contributors, ODbL','features':features}))
print(f'Saved {len(features)} places to {a.out}. Import this file in Wanderlore → Setup.')
