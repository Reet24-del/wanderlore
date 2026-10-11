"""Seed public place data only; never upload a laptop's walks database."""
import json
from pathlib import Path
from app import store


def seed():
    root = Path(__file__).resolve().parent
    store.init()
    if not any(p['id'] == 'lucknow-public' for p in store.packs()):
        store.put_pack('lucknow-public', 'Lucknow — central city and adjoining areas',
                       json.loads((root / 'lucknow-places.geojson').read_text()))
    lore = store.DATA / 'lore.json'
    if not lore.exists():
        lore.write_text((root / 'lore.json').read_text())


if __name__ == '__main__':
    seed()
