import json
import httpx
import pytest
from app import providers
from test_wanderlore import client


def test_online_gemma_keeps_coordinates_out(monkeypatch):
    monkeypatch.setattr(providers,'ONLINE_GEMMA',True)
    monkeypatch.setattr(providers,'MODEL','gemma-4-26b-a4b-it')
    monkeypatch.setenv('GOOGLE_API_KEY','test-only')
    captured={}
    def post(url,**kwargs):
        captured.update(kwargs)
        return httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'PRIVATE THOUGHT','thought':True},{'text':'Near Rumi Gate, the lantern glows softly. Your companion smiles.'}]},'finishReason':'STOP'}]},request=httpx.Request('POST',url))
    monkeypatch.setattr(providers.httpx,'post',post)
    result=providers.generate({'genre':'folklore','canon':{},'nearby_feature':{'name':'Rumi Gate','lat':26.12345,'lon':80.12345,'distance_m':12},'time_of_day':'day','weather':'clear','chapter':1,'final':False})
    prompt=json.dumps(captured['json'])
    assert '26.12345' not in prompt and '80.12345' not in prompt and 'distance_m' not in prompt
    assert 'Rumi Gate' in result['text'] and 'PRIVATE THOUGHT' not in result['text']
    assert captured['headers']['x-goog-api-key']=='test-only'


def test_render_liveness_does_not_unlock_private_data(client,monkeypatch):
    monkeypatch.setenv('WANDERLORE_HOSTED','1')
    assert client.get('/healthz').json()=={'status':'ok'}
    assert client.get('/api/health').status_code==401
    assert client.get('/api/walks').status_code==401
