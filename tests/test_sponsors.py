import json
import wave
import httpx
import pytest
from app import main, providers, store, lore, telemetry
from test_wanderlore import client, start, chapter


def test_elevenlabs_request_and_wav(tmp_path,monkeypatch):
    monkeypatch.setenv('ELEVENLABS_API_KEY','test-secret');monkeypatch.setenv('ELEVENLABS_VOICE_ID','voice123')
    captured={}
    def post(url,**kwargs):
        captured.update(kwargs);captured['url']=url
        return httpx.Response(200,content=b'\0\0'*2400,headers={'content-type':'audio/pcm'},request=httpx.Request('POST',url))
    monkeypatch.setattr(providers.httpx,'post',post)
    path=tmp_path/'audio.wav';providers.speak('A fictional lantern lights the path.',path,'elevenlabs')
    with wave.open(str(path)) as f:
        assert f.getframerate()==24000 and f.getnchannels()==1 and f.getnframes()==2400
    assert captured['params']['output_format']=='pcm_24000'
    assert captured['headers']['xi-api-key']=='test-secret'
    assert set(captured['json'])=={'text','model_id','voice_settings'}


def test_elevenlabs_failure_does_not_fall_back(client,monkeypatch):
    monkeypatch.setenv('ELEVENLABS_API_KEY','test-secret');monkeypatch.setenv('ELEVENLABS_VOICE_ID','voice123')
    def post(url,**kwargs):return httpx.Response(401,request=httpx.Request('POST',url))
    monkeypatch.setattr(providers.httpx,'post',post)
    w=start(client,voice='elevenlabs');r=chapter(client,w)
    assert r.status_code==503 and 'ElevenLabs' in r.json()['detail']
    assert client.get(f'/api/walks/{w["id"]}').json()['beats']==[]


def test_unconfigured_voice_rejected(client,monkeypatch):
    monkeypatch.delenv('ELEVENLABS_API_KEY',raising=False)
    assert client.post('/api/walks',json={'voice':'elevenlabs'}).status_code==503
    assert client.post('/api/voices/elevenlabs/preview').status_code==503


def test_hosted_pairing_required_even_for_loopback(client,monkeypatch):
    monkeypatch.setenv('WANDERLORE_HOSTED','1')
    assert client.get('/api/walks').status_code==401
    r=client.post('/api/pair',json={'code':main.PAIR_CODE})
    assert r.status_code==200 and 'Secure' in r.headers['set-cookie']
    # HTTP test client must not send the HTTPS-only cookie over plaintext.
    assert client.get('/api/walks').status_code==401
    assert client.get('/api/walks',headers={'cookie':f'wanderlore_pair={main.PAIR_CODE}'}).status_code==200


def test_sentry_scrubber_removes_personal_data():
    raw={'type':'transaction','event_id':'123','user':{'ip':'private'},'request':{'data':'GPS'},'exception':'story','transaction':'private-id','contexts':{'trace':{'trace_id':'abc','data':{'secret':'key'}}},'spans':[{'op':'gen_ai.request','description':'story text','data':{'gen_ai.request.model':'gemma3:1b','gen_ai.prompt':'GPS','api_key':'secret'}}]}
    clean=telemetry.scrub(raw)
    assert clean['spans'][0]['data']=={'gen_ai.request.model':'gemma3:1b'}
    assert all(s not in json.dumps(clean) for s in ('private','GPS','secret','story text'))
    assert telemetry.scrub({'exception':'secret'}) is None


def test_offline_lore_is_bounded_and_source_checked(tmp_path,monkeypatch):
    monkeypatch.setattr(lore,'DATA',tmp_path)
    (tmp_path/'lore.json').write_text(json.dumps({'Rumi Gate':[{'text':'x'*900,'source_url':'https://example.org/source'},{'text':'bad','source_url':'javascript:alert(1)'}]}))
    items=lore.for_place('Rumi Gate');assert len(items)==1 and len(items[0]['text'])==600
    assert lore.for_place('Not in this pack')==[]


def test_tiger_record_validation():
    from scripts.tiger_lore import validate
    assert validate([{'place':'Rumi Gate','text':'Public description','source_url':'https://example.org'}])
    with pytest.raises(ValueError):validate([{'place':'x','text':'x','source_url':'javascript:bad'}])


def test_real_sentry_sdk_emits_sanitized_trace(monkeypatch):
    import sentry_sdk
    from sentry_sdk.transport import Transport
    captured=[]
    class MemoryTransport(Transport):
        def capture_envelope(self,envelope):
            for item in envelope.items:
                if item.headers.get('type')=='transaction':captured.append(item.payload.json)
    with sentry_sdk.init(dsn='https://public@example.invalid/1',transport=MemoryTransport,default_integrations=False,auto_enabling_integrations=False,traces_sample_rate=1.0,stream_gen_ai_spans=False,before_send_transaction=telemetry.scrub):
        monkeypatch.setattr(telemetry,'_sdk',sentry_sdk)
        with telemetry.chapter():
            with telemetry.step('gen_ai.request','ollama','gemma3:1b') as span:
                span.set_data('private_prompt','do not export this')
        sentry_sdk.flush()
    assert captured and captured[0]['spans'][0]['data']['gen_ai.request.model']=='gemma3:1b'
    assert 'do not export this' not in json.dumps(captured)


def test_gemma_receives_public_context(monkeypatch):
    captured={}
    def post(url,**kwargs):
        captured.update(json.loads(kwargs['json']['prompt']))
        return httpx.Response(200,json={'response':'The lantern brightens. Your companion smiles.'},request=httpx.Request('POST',url))
    monkeypatch.setattr(providers.httpx,'post',post)
    context={'genre':'folklore','canon':{'object':'lantern','companion':'keeper'},'weather':'clear','time_of_day':'morning','chapter':1,'final':False,'lore':[{'text':'Public place context','source_url':'https://example.org'}]}
    providers.generate(context)
    assert captured['public_place_context']==context['lore']
