#!/usr/bin/env python3
"""Prepare public place context in Tiger Data, then export for offline use."""
import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/".env",override=False)
from app.store import DATA

MODEL='embeddinggemma'
DIM=768
SQL='''
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS wanderlore_lore (
 id text PRIMARY KEY, place text NOT NULL, content text NOT NULL, source_url text NOT NULL,
 model text NOT NULL, embedding vector(768) NOT NULL,
 terms tsvector GENERATED ALWAYS AS (to_tsvector('english',content)) STORED
);
CREATE INDEX IF NOT EXISTS wanderlore_lore_terms ON wanderlore_lore USING gin(terms);
'''
SEARCH='''
WITH semantic AS (
 SELECT id, row_number() OVER (ORDER BY embedding <=> %s::vector,id) rank
 FROM wanderlore_lore WHERE place=%s AND model=%s ORDER BY embedding <=> %s::vector,id LIMIT 10
), lexical AS (
 SELECT id, row_number() OVER (ORDER BY ts_rank_cd(terms,plainto_tsquery('english',%s)) DESC,id) rank
 FROM wanderlore_lore WHERE place=%s AND model=%s AND terms @@ plainto_tsquery('english',%s)
 ORDER BY ts_rank_cd(terms,plainto_tsquery('english',%s)) DESC,id LIMIT 10
), fused AS (
 SELECT coalesce(s.id,l.id) id,coalesce(1.0/(60+s.rank),0)+coalesce(1.0/(60+l.rank),0) score
 FROM semantic s FULL OUTER JOIN lexical l USING(id)
)
SELECT d.content,d.source_url FROM fused f JOIN wanderlore_lore d USING(id) ORDER BY f.score DESC,d.id LIMIT 2
'''

def embedding(text):
    r=httpx.post('http://127.0.0.1:11434/api/embed',json={'model':MODEL,'input':text,'dimensions':DIM,'truncate':False},timeout=90,trust_env=False)
    r.raise_for_status();values=r.json()['embeddings'][0]
    if len(values)!=DIM or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in values): raise ValueError('Invalid embedding dimensions or values')
    return json.dumps(values)

def validate(records):
    if not isinstance(records,list) or not records: raise ValueError('Supply a nonempty list of public source records')
    for r in records:
        if not all(isinstance(r.get(k),str) and r[k].strip() for k in ('place','text','source_url')): raise ValueError('Each record needs place, text and source_url')
        if not r['source_url'].startswith('https://') or len(r['text'])>6000: raise ValueError('Use HTTPS sources and text under 6000 characters')
    return records

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['import','export']);p.add_argument('file',type=Path);args=p.parse_args()
    if not os.getenv('TIGER_DATABASE_URL'): p.error('Set TIGER_DATABASE_URL locally; do not put it in a command argument.')
    import psycopg
    # Enforce encrypted transport and hostname verification for a hosted database.
    with psycopg.connect(os.environ['TIGER_DATABASE_URL'],sslmode='verify-full',sslrootcert='system',connect_timeout=10) as db:
        if args.action=='import':
            records=validate(json.loads(args.file.read_text()))
            db.execute(SQL)
            for r in records:
                identity=hashlib.sha256((r['place']+r['source_url']+r['text']).encode()).hexdigest()
                db.execute('INSERT INTO wanderlore_lore (id,place,content,source_url,model,embedding) VALUES (%s,%s,%s,%s,%s,%s::vector) ON CONFLICT(id) DO UPDATE SET content=excluded.content,embedding=excluded.embedding,model=excluded.model',(identity,r['place'],r['text'],r['source_url'],MODEL,embedding(r['text'])))
            print(f'Imported {len(records)} public records into Tiger Data.')
        else:
            result={}
            for (place,) in db.execute('SELECT DISTINCT place FROM wanderlore_lore WHERE model=%s ORDER BY place',(MODEL,)).fetchall():
                query=place+' landmarks landscape nature';vector=embedding(query)
                rows=db.execute(SEARCH,(vector,place,MODEL,vector,query,place,MODEL,query,query)).fetchall()
                result[place]=[{'text':text,'source_url':url} for text,url in rows]
            args.file.parent.mkdir(parents=True,exist_ok=True);tmp=args.file.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2));tmp.replace(args.file)
            print(f'Exported context for {len(result)} places. Put the export at {DATA / "lore.json"} for walking.')
if __name__=='__main__':
    try: main()
    except Exception as exc:
        # Database exceptions may embed connection credentials; keep output generic.
        raise SystemExit(f'Preparation failed ({type(exc).__name__}). Check credentials, TLS, database schema, and local embedding model.') from None
