import json
import os
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.environ.get('WANDERLORE_DATA',ROOT/'data'))
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/'walks.sqlite3'

def connect():
    db=sqlite3.connect(DB,timeout=20)
    db.row_factory=sqlite3.Row
    return db

def init():
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS walks (id TEXT PRIMARY KEY, created TEXT NOT NULL, state TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS packs (id TEXT PRIMARY KEY, name TEXT NOT NULL, data TEXT NOT NULL)')

def save(walk):
    with connect() as db:
        db.execute('INSERT INTO walks VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state',(walk['id'],walk['created'],json.dumps(walk)))

def get(walk_id):
    with connect() as db:
        row=db.execute('SELECT state FROM walks WHERE id=?',(walk_id,)).fetchone()
    return json.loads(row['state']) if row else None

def all_walks():
    with connect() as db: rows=db.execute('SELECT state FROM walks ORDER BY created DESC LIMIT 100').fetchall()
    return [json.loads(r['state']) for r in rows]

def packs():
    with connect() as db: rows=db.execute('SELECT id,name FROM packs ORDER BY name').fetchall()
    return [dict(r) for r in rows]

def get_pack(pack_id):
    with connect() as db: row=db.execute('SELECT data FROM packs WHERE id=?',(pack_id,)).fetchone()
    return json.loads(row['data']) if row else {'type':'FeatureCollection','features':[]}

def put_pack(pack_id,name,data):
    with connect() as db: db.execute('INSERT INTO packs VALUES (?,?,?)',(pack_id,name,json.dumps(data)))
