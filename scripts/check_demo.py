#!/usr/bin/env python3
"""Read-only localhost readiness check; never prints credentials or generates audio."""
import sys
import httpx


def check(base='http://127.0.0.1:8766'):
    try:
        with httpx.Client(base_url=base, timeout=8, trust_env=False) as client:
            reply = client.get('/api/health')
            reply.raise_for_status()
            health = reply.json()
            shell = client.get('/')
            shell.raise_for_status()
    except (httpx.HTTPError, ValueError):
        print('NOT READY: local app is unreachable. Start Wanderlore.command and keep it open.')
        return 1
    model = bool(health.get('model_ready'))
    local_voice = bool(health.get('voice_ready'))
    online_voice = bool(health.get('elevenlabs_ready'))
    print('App: reachable')
    print('Gemma: ' + ('ready' if model else 'not ready'))
    print('Offline narration: ' + ('ready' if local_voice else 'not ready'))
    print('ElevenLabs: ' + ('configured (not a connection or credit check)' if online_voice else 'not configured'))
    print(f"Map packs: {len(health.get('packs', []))}")
    print('Live location: must be checked in your browser; server health cannot verify GPS.')
    print('For a desktop demo: Sample walk + Local AI. The route is simulated.')
    return 0 if model and (local_voice or online_voice) else 1


if __name__ == '__main__':
    sys.exit(check())
