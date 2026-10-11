"""Reads the offline Tiger Data export; walking never queries the database."""
import json
from .store import DATA

def for_place(name):
    if not name: return []
    path=DATA/'lore.json'
    if not path.exists(): return []
    try:
        pack=json.loads(path.read_text())
        return [{'text':str(r['text'])[:600],'source_url':str(r['source_url'])} for r in pack.get(name,[])[:2] if str(r.get('source_url','')).startswith('https://')]
    except (ValueError,TypeError,KeyError,OSError): return []
