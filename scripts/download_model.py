#!/usr/bin/env python3
"""Install the default model from the Ollama registry over IPv4, verifying every digest.
Fallback for networks with a broken IPv6 route to the model registry.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

root=Path(os.environ.get('OLLAMA_MODELS',Path(__file__).resolve().parent.parent/'models/ollama'))
root.mkdir(parents=True,exist_ok=True)
registry='https://registry.ollama.ai/v2/library/gemma3'
result=subprocess.run(['curl','-4','-fsSL','--retry','3','--max-time','30',registry+'/manifests/1b'],check=True,capture_output=True)
manifest=json.loads(result.stdout)
for layer in [manifest['config'],*manifest['layers']]:
    digest=layer['digest']
    if not re.fullmatch(r'sha256:[a-f0-9]{64}',digest): raise ValueError('Invalid digest')
    path=root/'blobs'/digest.replace(':','-');path.parent.mkdir(parents=True,exist_ok=True)
    def checksum(p):
        h=hashlib.sha256()
        with p.open('rb') as f:
            while chunk:=f.read(1024*1024): h.update(chunk)
        return h.hexdigest()
    if path.is_file() and checksum(path)==digest[7:]: continue
    partial=path.with_suffix('.download')
    subprocess.run(['curl','-4','-fL','--retry','3','--connect-timeout','20','--max-time','900',registry+'/blobs/'+digest,'-o',str(partial)],check=True)
    if partial.stat().st_size!=layer['size'] or checksum(partial)!=digest[7:]: raise RuntimeError('Model integrity verification failed')
    partial.replace(path)
mp=root/'manifests/registry.ollama.ai/library/gemma3/1b'
mp.parent.mkdir(parents=True,exist_ok=True);mp.write_text(json.dumps(manifest))
print('Gemma 3 1B installed and all SHA-256 digests verified.')
