import json
import math
import os
import secrets
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from . import geo, providers, store, choices, telemetry, lore

AUDIO=store.DATA/'audio';AUDIO.mkdir(exist_ok=True)
_lock_guard=threading.Lock();_locks={}

def lock(walk_id):
    with _lock_guard: return _locks.setdefault(walk_id,threading.Lock())

def now(): return datetime.now(timezone.utc).isoformat()

def load(walk_id):
    w=store.get(walk_id)
    if not w: raise HTTPException(404,'Walk not found.')
    for b in w['beats']:
        b.setdefault('choices', [] if b.get('final') else choices.for_chapter(w['canon'],b['number']))
    return w

@asynccontextmanager
async def lifespan(app):
    store.init()
    telemetry.setup()
    yield

app=FastAPI(title='Wanderlore',lifespan=lifespan)
PAIR_FILE=store.DATA/'pairing-code'
if not PAIR_FILE.exists():
    PAIR_FILE.write_text(secrets.token_urlsafe(12));PAIR_FILE.chmod(0o600)
PAIR_CODE=os.getenv('WANDERLORE_PAIR_CODE') or PAIR_FILE.read_text().strip()

@app.middleware('http')
async def local_guard(request,call_next):
    if request.headers.get('sec-fetch-site')=='cross-site' and request.url.path.startswith(('/api/','/audio/')):
        return Response('Cross-site access is disabled.',status_code=403)
    if int(request.headers.get('content-length','0'))>8_000_000:
        return Response('Map pack is too large (8 MB maximum).',status_code=413)
    remote=os.getenv('WANDERLORE_HOSTED')=='1' or request.client and request.client.host not in ('127.0.0.1','::1','testclient')
    if remote and request.url.path.startswith(('/api/','/audio/')) and request.url.path!='/api/pair':
        if not secrets.compare_digest(request.cookies.get('wanderlore_pair',''),PAIR_CODE):
            return Response('Pair this device with the laptop first.',status_code=401)
    result=await call_next(request)
    result.headers['X-Content-Type-Options']='nosniff'
    result.headers['Referrer-Policy']='no-referrer'
    result.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    if request.url.path.startswith(('/api/','/audio/')): result.headers['Cache-Control']='no-store'
    return result

class Pair(BaseModel): code: str=Field(max_length=100)
@app.post('/api/pair')
def pair(body:Pair,response:Response):
    if not secrets.compare_digest(body.code,PAIR_CODE): raise HTTPException(403,'Incorrect pairing code.')
    response.set_cookie('wanderlore_pair',PAIR_CODE,httponly=True,samesite='strict',secure=os.getenv('WANDERLORE_HOSTED')=='1',max_age=86400)
    return {'paired':True}

@app.get('/healthz')
def healthz():
    # Public liveness only; provider and journal details still require pairing.
    return {'status':'ok'}

@app.get('/api/health')
def health(): return {**providers.readiness(),'packs':store.packs(),'version':'0.2.0','temporary_storage':os.getenv('WANDERLORE_TEMPORARY_STORAGE')=='1','cloud_requests':bool(providers.ONLINE_GEMMA or providers.eleven_ready() or os.getenv('SENTRY_DSN')),'hosted':os.getenv('WANDERLORE_HOSTED')=='1','integrations':{'elevenlabs':providers.eleven_ready(),'sentry':bool(os.getenv('SENTRY_DSN')),'tiger_data':(store.DATA/'lore.json').exists()}}

@app.post('/api/voices/{voice}/preview')
def voice_preview(voice:Literal['af_heart','bf_emma','elevenlabs']):
    if voice=='elevenlabs' and not providers.eleven_ready(): raise HTTPException(503,'Configure ElevenLabs in the server environment first.')
    import hashlib
    version=hashlib.sha256((os.getenv('ELEVENLABS_VOICE_ID','')+os.getenv('ELEVENLABS_MODEL','eleven_multilingual_v2')).encode()).hexdigest()[:12]
    path=AUDIO/(f'preview-elevenlabs-{version}.wav' if voice=='elevenlabs' else f'preview-v1-{voice}.wav')
    with lock(f'preview-{voice}'):
        if not path.exists():
            try:
                providers.speak("There's a little light between the trees. You almost miss it. Then the lantern keeper smiles. I've been waiting for you, she says. Come, there's a story I'd like you to hear.",path,voice)
            except providers.ProviderError as exc: raise HTTPException(503,str(exc))
    return {'audio_url':f'/audio/{path.name}'}

class Pack(BaseModel):
    name:str=Field(min_length=1,max_length=80)
    geojson:dict

@app.post('/api/packs')
def add_pack(body:Pack):
    try: geo.validate_pack(body.geojson)
    except (ValueError,TypeError,KeyError,IndexError) as e: raise HTTPException(422,str(e))
    pack_id=str(uuid.uuid4());store.put_pack(pack_id,body.name,body.geojson)
    return {'id':pack_id,'name':body.name,'features':len(body.geojson['features'])}

@app.get('/api/packs/{pack_id}')
def get_pack(pack_id:str): return store.get_pack(pack_id)

class Start(BaseModel):
    genre:Literal['folklore','mystery','fantasy']='folklore'
    minutes:Literal[10,20,30]=20
    weather:Literal['clear','cloudy','rainy','windy']='clear'
    mode:Literal['sample','gps']='sample'
    engine:Literal['sample','local']='sample'
    voice:Literal['af_heart','bf_emma','elevenlabs']='af_heart'
    pack_id:str|None=None

@app.post('/api/walks')
def start(body:Start):
    if body.voice=='elevenlabs' and not providers.eleven_ready(): raise HTTPException(503,'ElevenLabs is not configured. Choose a local voice or configure it in Setup.')
    if body.engine=='local':
        state=providers.readiness()
        if not state['model_ready'] or (body.voice!='elevenlabs' and not state['voice_ready']): raise HTTPException(503,'Local narration needs Ollama, the selected model, and the Kokoro voice files. Open Setup for details.')
    if body.pack_id and not any(p['id']==body.pack_id for p in store.packs()): raise HTTPException(422,'Map pack does not exist.')
    canon={'folklore':{'companion':'the lantern keeper','object':'brass lantern','quest':'recover a forgotten message'},'mystery':{'companion':'the quiet archivist','object':'folded letter','quest':'discover who left a message'},'fantasy':{'companion':'the star cartographer','object':'silver compass','quest':'restore a fading constellation'}}[body.genre]
    w={'id':str(uuid.uuid4()),'created':now(),**body.model_dump(),'title':'A walk waiting to unfold','status':'active','beats':[],'positions':[],'canon':canon,'summary':'The quest has not begun.','notes':'','duration_seconds':0}
    store.save(w);return w

@app.get('/api/walks')
def walks():
    return [{k:v for k,v in w.items() if k not in ('positions','beats','canon')}|{'chapters':len(w['beats'])} for w in store.all_walks()]

@app.get('/api/walks/{walk_id}')
def walk(walk_id:str): return load(walk_id)

class Fix(BaseModel):
    lat:float=Field(ge=-90,le=90,allow_inf_nan=False)
    lon:float=Field(ge=-180,le=180,allow_inf_nan=False)
    accuracy:float=Field(ge=0,le=100000,allow_inf_nan=False)
    timestamp:float=Field(ge=0,allow_inf_nan=False)


def accept_fix(w,fix):
    if fix.accuracy>80: raise HTTPException(422,'Location accuracy is low. Wait for a clearer GPS fix.')
    if abs(time.time()-fix.timestamp)>45: raise HTTPException(422,'Location is stale. Wait for a new GPS fix.')
    if w['positions'] and fix.timestamp<=w['positions'][-1]['timestamp']: return
    w['positions'].append(fix.model_dump())
    w['positions']=w['positions'][-3000:]

@app.post('/api/walks/{walk_id}/position')
def position(walk_id:str,fix:Fix):
    with lock(walk_id):
        w=load(walk_id)
        if w['status']=='finished': raise HTTPException(409,'This walk has finished.')
        if w['mode']!='gps': raise HTTPException(409,'Sample walks use a simulated route.')
        accept_fix(w,fix);store.save(w)
    return {'accepted':True}

class BeatRequest(BaseModel):
    request_id:str=Field(min_length=8,max_length=80)
    fix:Fix|None=None
    choice_id:str|None=Field(default=None,max_length=80)
    final:bool=False
    automatic:bool=False
    hour:int=Field(default=12,ge=0,le=23)

SAMPLE_POINTS=[[-0.1582,51.5298],[-0.1573,51.5306],[-0.1564,51.5316],[-0.1554,51.5321],[-0.1542,51.5314],[-0.1533,51.5307]]
SAMPLE_NAMES=['Riverside Meadow','Willow Brook','Mossy Wood','Old Stone Lane','The Quiet Garden','Riverside Meadow']
OBSERVATIONS=['If you like, notice one colour around you.','If you like, listen to a sound in the distance.','If you like, take one easy breath.','If you like, notice how the light falls.','If you like, look for a shape you have not noticed before.']

@app.post('/api/walks/{walk_id}/beats')
def beat(walk_id:str,body:BeatRequest):
    with lock(walk_id), telemetry.chapter():
        w=load(walk_id)
        existing=next((b for b in w['beats'] if b['request_id']==body.request_id),None)
        if existing: return {'beat':existing,'walk':w}
        if w['status']!='active': raise HTTPException(409,'Resume this walk before creating a chapter.')
        if len(w['beats'])>=60: raise HTTPException(409,'This walk has reached its chapter limit. Finish and save it.')
        if w['beats'] and w['beats'][-1].get('final'): raise HTTPException(409,'The closing chapter is ready. Finish and save this walk.')
        decision=None
        if body.choice_id:
            available=w['beats'][-1].get('choices',[]) if w['beats'] else []
            decision=next((c for c in available if c['id']==body.choice_id),None)
            if not decision: raise HTTPException(422,'That choice belongs to another chapter. Reload this walk and choose again.')
        n=len(w['beats']);feature=None
        if w['mode']=='gps':
            if not body.fix: raise HTTPException(422,'A current GPS fix is required for each chapter.')
            accept_fix(w,body.fix)
            feature=geo.nearest(store.get_pack(w['pack_id']),body.fix.lon,body.fix.lat) if w['pack_id'] else None
        else:
            p=SAMPLE_POINTS[n%len(SAMPLE_POINTS)]
            feature={'name':SAMPLE_NAMES[n%len(SAMPLE_NAMES)],'distance_m':0,'kind':'sample location'}
            w['positions'].append({'lon':p[0],'lat':p[1],'accuracy':0,'timestamp':time.time()})
        period='morning' if 5<=body.hour<12 else 'afternoon' if 12<=body.hour<17 else 'dusk' if 17<=body.hour<20 else 'night'
        context={'genre':w['genre'],'canon':w['canon'],'summary':w['summary'],'recent_chapters':[b['text'] for b in w['beats'][-3:]],'chapter':n+1,'nearby_feature':feature,'weather':w['weather'],'time_of_day':period,'final':body.final,'decision':decision,'previous_decisions':[b['decision']['label'] for b in w['beats'] if b.get('decision')][-3:]}
        context['lore']=lore.for_place(feature['name']) if feature and w['mode']=='gps' else []
        t=time.monotonic();audio_url=None;bid=str(uuid.uuid4())
        try:
            result=providers.generate(context) if w['engine']=='local' else providers.sample(context)
            if body.final and w['engine']=='local' and 'message is restored' not in result['text'].lower():
                result['text']+=f" The message is restored: ordinary places become extraordinary when you notice them. In the story, {w['canon']['companion']} thanks you, and your quest is complete."
            elif not body.final:
                result['text']+=' '+OBSERVATIONS[n%len(OBSERVATIONS)]
            if w.get('voice','af_heart')=='elevenlabs' or w['engine']=='local' or providers.VOICE.is_file():
                path=AUDIO/f'{bid}.wav';providers.speak(result['text'],path,w.get('voice','af_heart'));audio_url=f'/audio/{bid}.wav'
        except providers.ProviderError as e: raise HTTPException(503,str(e))
        b={'sources':context['lore'],'voice':w.get('voice','af_heart'),'decision':decision,'choices':[] if body.final else choices.for_chapter(w['canon'],n+1),'id':bid,'request_id':body.request_id,'number':n+1,**result,'feature':feature,'audio_url':audio_url,'engine':w['engine'],'time_of_day':period,'created':now(),'generation_ms':round((time.monotonic()-t)*1000),'final':body.final,'position':w['positions'][-1]}
        w['beats'].append(b)
        if n==0: w['title']=b['title']
        # Immutable canon + recent narrative are the memory. No claim of guaranteed coherence.
        w['summary']=f"Quest: {w['canon']['quest']}. Companion: {w['canon']['companion']}. Object: {w['canon']['object']}. Latest scene: {b['text']}"
        store.save(w);return {'beat':b,'walk':w}

class Update(BaseModel):
    status:Literal['active','paused','finished']|None=None
    notes:str|None=Field(default=None,max_length=5000)
    duration_seconds:int|None=Field(default=None,ge=0,le=86400)

@app.patch('/api/walks/{walk_id}')
def update(walk_id:str,body:Update):
    with lock(walk_id):
        w=load(walk_id)
        if w['status']=='finished' and body.status and body.status!='finished': raise HTTPException(409,'Finished walks cannot be resumed.')
        w.update(body.model_dump(exclude_none=True));store.save(w);return w

@app.get('/api/walks/{walk_id}/export')
def export(walk_id:str):
    w=load(walk_id)
    return Response(json.dumps(w,indent=2),media_type='application/json',headers={'Content-Disposition':f'attachment; filename="wanderlore-{w["id"][:8]}.json"'})

@app.get('/audio/{filename}')
def audio(filename:str):
    try:
        if filename not in {f'preview-v1-{v}.wav' for v in providers.VOICES} and not __import__('re').fullmatch(r'preview-elevenlabs-[0-9a-f]{12}\.wav',filename):
            uuid.UUID(filename.removesuffix('.wav'))
    except ValueError: raise HTTPException(404)
    path=AUDIO/filename
    if not filename.endswith('.wav') or not path.is_file(): raise HTTPException(404)
    return FileResponse(path,media_type='audio/wav')

app.mount('/',StaticFiles(directory=store.ROOT/'web',html=True),name='web')
