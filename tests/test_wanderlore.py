import time
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from app import geo, main, providers, store

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'walks.sqlite3')
    monkeypatch.setattr(main,'AUDIO',tmp_path)
    monkeypatch.setattr(providers,'VOICE',tmp_path/'missing.onnx')
    with TestClient(main.app) as c: yield c

def start(c,**kwargs):
    r=c.post('/api/walks',json=kwargs);assert r.status_code==200,r.text;return r.json()

def chapter(c,w,**kwargs):
    return c.post(f'/api/walks/{w["id"]}/beats',json={'request_id':'request-0001',**kwargs})

def test_distance_and_polygon_hole():
    assert 110<geo.distance([0,0],[0,.001])<112
    polygon={'type':'Polygon','coordinates':[[[0,0],[.01,0],[.01,.01],[0,.01],[0,0]],[[.004,.004],[.006,.004],[.006,.006],[.004,.006],[.004,.004]]]}
    assert geo.geometry_distance([.002,.002],polygon)==0
    assert geo.geometry_distance([.005,.005],polygon)>100
    assert 110<geo.geometry_distance([.011,.005],polygon)<112

def test_line_distance_not_centroid():
    assert geo.geometry_distance([.099,.0001],{'type':'LineString','coordinates':[[0,0],[.1,0]]})<12

def test_pack_rejects_bad_geometry(client):
    for coords in [[],[200,50]]:
        pack={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':coords},'properties':{}}]}
        assert client.post('/api/packs',json={'name':'bad','geojson':pack}).status_code==422

def test_sample_memory_idempotency_and_finish(client):
    w=start(client,genre='mystery')
    first=chapter(client,w);assert first.status_code==200
    assert first.json()['beat']['engine']=='sample'
    assert 'folded letter' in first.json()['beat']['text']
    assert chapter(client,w).json()['beat']['id']==first.json()['beat']['id']
    second=chapter(client,w,request_id='request-0002',final=True).json()
    assert second['walk']['canon']==w['canon']
    assert len(second['walk']['beats'])==2
    assert chapter(client,w,request_id='request-0003').status_code==409
    result=client.patch(f'/api/walks/{w["id"]}',json={'status':'finished','notes':'Heard a blackbird.','duration_seconds':124})
    assert result.status_code==200
    assert client.get(f'/api/walks/{w["id"]}/export').json()['notes']=='Heard a blackbird.'
    assert client.patch(f'/api/walks/{w["id"]}',json={'status':'active'}).status_code==409

def test_pause_blocks_generation(client):
    w=start(client);client.patch(f'/api/walks/{w["id"]}',json={'status':'paused'})
    assert chapter(client,w).status_code==409

def test_local_failure_does_not_create_fake_beat(client,monkeypatch):
    monkeypatch.setattr(providers,'readiness',lambda:{'model_ready':True,'voice_ready':True})
    def fail(_): raise providers.ProviderError('offline model failed')
    monkeypatch.setattr(providers,'generate',fail)
    w=start(client,engine='local')
    assert chapter(client,w).status_code==503
    assert client.get(f'/api/walks/{w["id"]}').json()['beats']==[]

def test_gps_freshness_accuracy_and_sparse_map(client):
    w=start(client,mode='gps');f={'lat':51.5,'lon':-.1,'accuracy':10,'timestamp':time.time()}
    assert chapter(client,w).status_code==422
    assert chapter(client,w,fix={**f,'accuracy':150}).status_code==422
    assert chapter(client,w,fix={**f,'timestamp':time.time()-90}).status_code==422
    r=chapter(client,w,fix=f);assert r.status_code==200
    assert r.json()['beat']['feature'] is None
    assert 'Riverside' not in r.json()['beat']['text']

def test_nearby_feature_used(client):
    data={'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[-.1,51.5]},'properties':{'name':'Test Garden'}}]}
    pack=client.post('/api/packs',json={'name':'test','geojson':data}).json()
    w=start(client,mode='gps',pack_id=pack['id'])
    b=chapter(client,w,fix={'lat':51.5,'lon':-.1,'accuracy':5,'timestamp':time.time()}).json()['beat']
    assert b['feature']['distance_m']==0
    assert 'Test Garden' in b['text']

def test_stationary_auto_continues_without_a_choice(client):
    w=start(client,mode='gps')
    chapter(client,w,fix={'lat':51.5,'lon':-.1,'accuracy':5,'timestamp':time.time()-30})
    for age in [15,1]: client.post(f'/api/walks/{w["id"]}/position',json={'lat':51.5,'lon':-.1,'accuracy':5,'timestamp':time.time()-age})
    r=chapter(client,w,request_id='request-0002',automatic=True,fix={'lat':51.5,'lon':-.1,'accuracy':5,'timestamp':time.time()})
    assert r.status_code==200
    assert 'waiting' not in r.json()
    assert r.json()['beat']['decision'] is None
    assert len(client.get(f'/api/walks/{w["id"]}').json()['beats'])==2

def test_duplicate_requests_concurrent(client):
    w=start(client)
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(lambda _:chapter(client,w).json(),range(2)))
    assert results[0]['beat']['id']==results[1]['beat']['id']
    assert len(client.get(f'/api/walks/{w["id"]}').json()['beats'])==1

def test_cross_site_requests_rejected(client):
    assert client.post('/api/walks',json={},headers={'sec-fetch-site':'cross-site'}).status_code==403

def test_remote_device_requires_pairing(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB',tmp_path/'walks.sqlite3')
    with TestClient(main.app,client=('192.168.1.9',1234)) as remote:
        assert remote.get('/api/health').status_code==401
        assert remote.post('/api/pair',json={'code':'wrong'}).status_code==403
        assert remote.post('/api/pair',json={'code':main.PAIR_CODE}).status_code==200
        monkeypatch.setattr(providers,'readiness',lambda:{})
        assert remote.get('/api/health').status_code==200

def test_selected_voice_is_saved_and_used(client,monkeypatch,tmp_path):
    model=tmp_path/'voice.onnx';model.touch()
    monkeypatch.setattr(providers,'VOICE',model)
    calls=[]
    def speak(text,path,voice):
        calls.append(voice);path.write_bytes(b'test-audio')
    monkeypatch.setattr(providers,'speak',speak)
    w=start(client,voice='bf_emma')
    assert chapter(client,w).status_code==200
    assert calls==['bf_emma']
    assert client.get(f'/api/walks/{w["id"]}').json()['voice']=='bf_emma'
    assert client.post('/api/walks',json={'voice':'unknown'}).status_code==422
    for _ in range(2):
        preview=client.post('/api/voices/af_heart/preview')
        assert preview.status_code==200
        assert client.get(preview.json()['audio_url']).status_code==200
    assert calls==['bf_emma','af_heart']
    assert client.post('/api/voices/unknown/preview').status_code==422


def test_empty_story_retried_once_without_json_constraint(monkeypatch):
    responses=iter(['', 'A small light appears beside the path. The companion smiles and the story begins.'])
    class Reply:
        def raise_for_status(self): pass
        def json(self): return {'response':next(responses)}
    def post(*args,**kwargs):
        assert 'format' not in kwargs['json']
        return Reply()
    monkeypatch.setattr(providers.httpx,'post',post)
    result=providers.generate({'final':False,'chapter':1,'genre':'fantasy','canon':{},'time_of_day':'night','weather':'clear'})
    assert result['text'].startswith('A small light')

def test_choices_branch_persist_and_reject_stale_decisions(client):
    w=start(client)
    first=chapter(client,w).json()['beat']
    assert len(first['choices'])==3
    selected=first['choices'][1]
    second=chapter(client,w,request_id='decision-0002',choice_id=selected['id'])
    assert second.status_code==200
    beat=second.json()['beat']
    assert beat['decision']['label']==selected['label']
    assert 'promise made to an old friend' in beat['text']
    assert client.get(f'/api/walks/{w["id"]}/export').json()['beats'][1]['decision']==selected
    assert chapter(client,w,request_id='decision-0002',choice_id=selected['id']).json()['beat']['id']==beat['id']
    assert chapter(client,w,request_id='decision-0003',choice_id=selected['id']).status_code==422
    last=chapter(client,w,request_id='decision-0004',choice_id=beat['choices'][0]['id'],final=True).json()['beat']
    assert last['choices']==[]
    assert 'engraved symbol' in last['text']

def test_decision_context_reaches_local_model(client,monkeypatch):
    w=start(client)
    first=chapter(client,w).json()['beat']
    saved=store.get(w['id']);saved['engine']='local';store.save(saved)
    received=[]
    def generate(context):
        received.append(context)
        return {'title':'The promise','text':'The companion remembers an old promise.'}
    monkeypatch.setattr(providers,'generate',generate)
    monkeypatch.setattr(providers,'speak',lambda *args:None)
    result=chapter(client,w,request_id='choice-model-2',choice_id=first['choices'][1]['id'])
    assert result.status_code==200
    assert received[0]['decision']['id']==first['choices'][1]['id']
    assert 'promise' in received[0]['decision']['consequence']


def test_generated_dialogue_keeps_quotes_and_previous_scene(monkeypatch):
    import json
    dialogue='“The word is share,” says the keeper. You remember the bluebell meadow.'
    def post(*args, **kwargs):
        prompt=json.loads(kwargs['json']['prompt'])
        assert prompt['previous_scene']=='The lantern revealed a bluebell.'
        assert 'already carry' in prompt['scene_task']
        class Reply:
            def raise_for_status(self): pass
            def json(self): return {'response':dialogue}
        return Reply()
    monkeypatch.setattr(providers.httpx,'post',post)
    context={'final':False,'chapter':1,'genre':'folklore','canon':{},'time_of_day':'day','weather':'clear','recent_chapters':['Old scene','The lantern revealed a bluebell.']}
    assert providers.generate(context)['text']==dialogue


def test_truncated_generation_excludes_unfinished_sentence(monkeypatch):
    class Reply:
        def raise_for_status(self): pass
        def json(self): return {'response':'A lantern glows. The keeper starts to reveal a', 'done_reason':'length'}
    monkeypatch.setattr(providers.httpx,'post',lambda *args,**kwargs:Reply())
    context={'final':False,'chapter':2,'genre':'folklore','canon':{},'time_of_day':'day','weather':'clear'}
    assert providers.generate(context)['text']=='A lantern glows.'
