# Lucknow offline places

Downloaded October 10, 2026 from the public OpenStreetMap API, after Overpass services returned errors. Imported into Wanderlore as **Lucknow — central city and adjoining areas**.

- 2,114 named mapped features: 837 points, 820 lines, 457 polygons. Road segments can share a name; this is not a count of unique landmarks.
- Includes Rumi Gate, Bara Imambara, Chhota Imambara, Janeshwar Mishra Park, Ambedkar Memorial Park, and named stretches of the Gomti River.
- Source: https://api.openstreetmap.org/api/0.6/map
- Attribution: © OpenStreetMap contributors, ODbL 1.0 — https://www.openstreetmap.org/copyright
- File: `lucknow-places.geojson` (760,078 bytes).

## Downloaded coverage

Each row is a bounding box in west/south/east/north order (longitude, latitude).

| Section | Bounding box |
|---|---|
| Central | 80.92, 26.83, 80.98, 26.89 |
| West | 80.86, 26.83, 80.92, 26.89 |
| East | 80.98, 26.83, 81.04, 26.89 |
| North | 80.92, 26.89, 80.98, 26.95 |
| South | 80.92, 26.77, 80.98, 26.83 |

These adjoining extracts cover the city core and parts of surrounding Lucknow, not the entire municipal district. Coverage is the union of the five rectangles, not the full outer bounding rectangle. Outside this coverage, or more than 100 m from a named feature, the app uses observation-only story context. Coordinates alone do not supply place names.

Named nodes and complete ways with leisure, tourism, historic, natural, waterway, highway, amenity, or place tags are included; unnamed features and relation-only geometries are omitted. English names are preferred where supplied by OSM. Geometry and source element IDs are retained; no artificial coordinates or invented places were added.

Validated the GeoJSON with the app's geometry validator. Proximity lookups at mapped coordinates returned Rumi Gate, Janeshwar Mishra Park, and Ambedkar Memorial Park at zero distance. This verifies map lookup, not the user's live GPS or an outdoor walk. Imported via the local API and verified selection persists after browser reload.
