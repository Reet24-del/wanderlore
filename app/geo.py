"""Small, offline GeoJSON reader. Distances are in metres, not degrees."""
import math

EARTH = 6371000

def distance(a, b):
    lat1, lat2 = math.radians(a[1]), math.radians(b[1])
    dlat, dlon = lat2-lat1, math.radians(b[0]-a[0])
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*EARTH*math.asin(min(1, math.sqrt(h)))

def segment_distance(p, a, b):
    scale = math.cos(math.radians(p[1]))
    ax, ay = (a[0]-p[0])*scale, a[1]-p[1]
    bx, by = (b[0]-p[0])*scale, b[1]-p[1]
    dx, dy = bx-ax, by-ay
    t = max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return math.hypot(ax+t*dx, ay+t*dy)*math.pi/180*EARTH

def inside(p, ring):
    odd = False
    for a,b in zip(ring, ring[1:]+ring[:1]):
        if (a[1]>p[1]) != (b[1]>p[1]) and p[0] < (b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:
            odd = not odd
    return odd

def geometry_distance(p, g):
    c, kind = g['coordinates'], g['type']
    if kind == 'Point': return distance(p,c)
    if kind == 'MultiPoint': return min(distance(p,x) for x in c)
    if kind == 'LineString': return min(segment_distance(p,a,b) for a,b in zip(c,c[1:]))
    if kind == 'Polygon':
        if inside(p,c[0]) and not any(inside(p,r) for r in c[1:]): return 0
        return min(geometry_distance(p,{'type':'LineString','coordinates':r}) for r in c)
    if kind == 'MultiLineString': return min(geometry_distance(p,{'type':'LineString','coordinates':r}) for r in c)
    if kind == 'MultiPolygon': return min(geometry_distance(p,{'type':'Polygon','coordinates':r}) for r in c)
    return float('inf')

def validate_pack(data):
    if data.get('type') != 'FeatureCollection' or not isinstance(data.get('features'),list):
        raise ValueError('Choose a GeoJSON FeatureCollection.')
    if not 1 <= len(data['features']) <= 10000: raise ValueError('A pack must contain 1–10,000 features.')
    def coordinate(v):
        if not isinstance(v,list) or len(v)<2 or any(not isinstance(n,(int,float)) or not math.isfinite(n) for n in v[:2]): raise ValueError('Invalid coordinates.')
        if not -180<=v[0]<=180 or not -90<=v[1]<=90: raise ValueError('Coordinates must be longitude, latitude.')
    def line(v, minimum=2):
        if not isinstance(v,list) or len(v)<minimum: raise ValueError('Invalid geometry.')
        for p in v: coordinate(p)
    def polygon(v):
        if not v: raise ValueError('Empty polygon.')
        for ring in v:
            line(ring,4)
            if ring[0][:2]!=ring[-1][:2]: raise ValueError('Polygon rings must be closed.')
    for f in data['features']:
        g = f.get('geometry') or {}; c = g.get('coordinates'); k=g.get('type')
        if k=='Point': coordinate(c)
        elif k=='MultiPoint': line(c,1)
        elif k=='LineString': line(c)
        elif k=='Polygon': polygon(c)
        elif k=='MultiLineString':
            if not c: raise ValueError('Empty geometry.')
            for v in c: line(v)
        elif k=='MultiPolygon':
            if not c: raise ValueError('Empty geometry.')
            for v in c: polygon(v)
        else: raise ValueError('Unsupported geometry: use points, lines or polygons.')
        if not isinstance(f.get('properties',{}),dict): raise ValueError('Invalid properties.')
    return data

def nearest(data, lon, lat, radius=100):
    candidates=[]
    for f in data.get('features',[]):
        props=f.get('properties',{}); name=props.get('name')
        if not isinstance(name,str) or not name.strip(): continue
        d=geometry_distance([lon,lat],f['geometry'])
        if d<=radius: candidates.append({'name':name[:120],'distance_m':round(d,1),'kind':str(props.get('leisure') or props.get('natural') or props.get('amenity') or 'place')[:60]})
    return min(candidates,key=lambda x:x['distance_m']) if candidates else None
