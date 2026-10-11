"""Opt-in, metadata-only Sentry traces. Never export prompts or routes."""
import os
from contextlib import contextmanager

_sdk=None
ALLOWED={'gen_ai.operation.name','gen_ai.provider.name','gen_ai.request.model','gen_ai.agent.name','gen_ai.tool.name','gen_ai.usage.input_tokens','gen_ai.usage.output_tokens','success'}

def scrub(event, hint=None):
    # Deliberate allow-list: even SDK-added HTTP, exception and user fields are dropped.
    if event.get('type')!='transaction': return None
    clean={k:event[k] for k in ('event_id','type','timestamp','start_timestamp','platform','release','environment') if k in event}
    clean['transaction']='wanderlore.chapter'
    trace=event.get('contexts',{}).get('trace',{})
    clean['contexts']={'trace':{k:v for k,v in trace.items() if k in ('trace_id','span_id','parent_span_id','op','status')}}
    clean['contexts']['trace']['data']={k:v for k,v in trace.get('data',{}).items() if k in ALLOWED}
    clean['spans']=[]
    for span in event.get('spans',[]):
        item={k:v for k,v in span.items() if k in ('trace_id','span_id','parent_span_id','start_timestamp','timestamp','op','status')}
        item['data']={k:v for k,v in span.get('data',{}).items() if k in ALLOWED}
        clean['spans'].append(item)
    return clean

def setup():
    global _sdk
    if not os.getenv('SENTRY_DSN'): return
    import sentry_sdk
    sentry_sdk.init(dsn=os.environ['SENTRY_DSN'],default_integrations=False,auto_enabling_integrations=False,send_default_pii=False,include_local_variables=False,traces_sample_rate=1.0,stream_gen_ai_spans=False,before_send=lambda event,hint:None,before_send_transaction=scrub,environment='wanderlore',release='wanderlore@0.2.0')
    _sdk=sentry_sdk

@contextmanager
def chapter():
    if not _sdk:
        yield
        return
    with _sdk.start_transaction(name='wanderlore.chapter',op='gen_ai.invoke_agent') as span:
        span.set_data('gen_ai.agent.name','Wanderlore')
        span.set_data('gen_ai.operation.name','invoke_agent')
        yield

@contextmanager
def step(op,provider,model):
    if not _sdk:
        yield None
        return
    with _sdk.start_span(op=op,name=op) as span:
        span.set_data('gen_ai.operation.name','chat' if op=='gen_ai.request' else 'execute_tool')
        if op=='gen_ai.execute_tool': span.set_data('gen_ai.tool.name','synthesize_speech')
        span.set_data('gen_ai.provider.name',provider)
        span.set_data('gen_ai.request.model',model)
        try:
            yield span
            span.set_data('success',True)
        except Exception:
            span.set_data('success',False)
            span.set_status('internal_error')
            raise
