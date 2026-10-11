# Sponsor setup and evidence

Updated October 11, 2026. Configuration alone is not a connection test. Never commit real API keys, pairing codes, recordings, GPS exports, or a walks database.

| Integration | Role | Verified status |
| --- | --- | --- |
| Gemma | Story generation | Local Ollama Gemma 3 and hosted Google AI Studio Gemma 4 chapters generated |
| ElevenLabs | Online speech | Roger narration generated and played in the hosted browser |
| Sentry Agent Tracing | Timing/model metadata | Real chapter transaction and generation span visible in Sentry |
| Tiger Data | Sourced place-context preparation | Four public records; hybrid retrieval export for two Lucknow places |
| Render | Hosting | HTTPS preview runs on the Free plan |
| Entire | Optional development-session tooling | CLI/hook setup prepared; captured session not verified |
| DigitalOcean | Optional deployment source | Package included, but no deployment is used |

## Configuration

Copy `.env.example` to `.env` on your own machine and populate only the services you intend to use. Render values belong in private environment settings. Install optional Python packages with:

```sh
uv pip install --python .venv/bin/python -r requirements-sponsors.txt
```

Restart after editing configuration. The landing form uses available server defaults; it no longer exposes engine, voice, or preview selectors. A successful generated chapter and playable audio are the practical narration check.

## Gemma and ElevenLabs

Local Gemma uses Ollama (`gemma3:1b` by default) and local Kokoro assets. The connected generation adapter is enabled with `WANDERLORE_NARRATOR=google`, `GOOGLE_API_KEY`, and an optional `WANDERLORE_MODEL`. The Render blueprint uses `gemma-4-26b-a4b-it`.

Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` for online speech. `ELEVENLABS_MODEL` defaults to `eleven_multilingual_v2`; the hosted voice is Roger. Narration text, including any place names, is sent to ElevenLabs. Google receives story context and place names; raw landmark coordinates and distances are stripped. The hosted server still processes GPS. Google free-tier prompts may be used to improve its products. All connected requests require internet and available quota.

## Sentry Agent Tracing

Set `SENTRY_DSN` for a Python project. Generate a real chapter, then inspect `wanderlore.chapter`: `gen_ai.request` covers generation and `gen_ai.execute_tool` covers speech. The opt-in instrumentation exports timings, provider/model metadata, and success. It excludes prompts, generated text, GPS, cookies, request bodies, and user identifiers. Automatic integrations and error events are disabled. Token/cost accounting is not claimed.

Verified development trace: `51bdfd74bf8149c1b67ec73c12adc34c`, 3.28 seconds. [Evidence](../submission/screenshots/08-sentry-trace.jpg).

## Tiger Data

Use a PostgreSQL service with pgvector and a certificate-valid `TIGER_DATABASE_URL`. Records contain public `place`, `text`, and HTTPS `source_url` fields, with exact map-pack names. Do not include private route history.

```sh
.runtime/ollama pull embeddinggemma
.venv/bin/python scripts/tiger_lore.py import docs/lucknow-lore.json
.venv/bin/python scripts/tiger_lore.py export data/lore.json
```

Use `ollama` on PATH instead of `.runtime/ollama` when appropriate. The importer generates 768-dimensional vectors locally. Keyword/vector retrieval combines rankings with reciprocal rank fusion and prepares a source-carrying export. During a walk, the storyteller reads that file; it does not query Tiger Data with each GPS reading.

On the current Shared Free service, direct psycopg access failed certificate verification. Verification was preserved: import and retrieval were executed through the authenticated HTTPS SQL editor. Four public summaries were stored. A prepared query returned two Rumi Gate records and one Janeshwar Mishra Park record in 0.7 seconds. The small export is bundled at `deploy/render/lore.json`. This demonstrates retrieval, not broad coverage or a benchmark. Future CLI imports/exports still require a verified TLS endpoint; do not disable certificate checks.

## Render

Follow [the deployment guide](../deploy/render/README.md) and `render.yaml`. The Free service uses online Gemma/ElevenLabs rather than local model inference. Pairing protects a shared journal; do not publish the owner code. Saved walks/audio can reset, so export before leaving.

## Optional source that is not claimed

Entire's setup wrapper is `scripts/enable_entire.sh`. It can prepare future supported Codex session capture after the required hook approval. Recorded sessions may contain prompts and transcripts; review before sharing. No captured session or prize category is claimed.

The DigitalOcean package remains in `deploy/digitalocean/` as an alternative deployment example. It is not used for this entry. Vercel and Copilot are not used.

## Documentation consulted

- [ElevenLabs speech API](https://elevenlabs.io/docs/api-reference/text-to-speech/convert)
- [Tiger Data hybrid search](https://www.tigerdata.com/docs/learn/tutorials/hybrid-search)
- [Ollama embeddings API](https://docs.ollama.com/api/embed)
- [Sentry custom instrumentation](https://docs.sentry.io/platforms/python/tracing/instrumentation/custom-instrumentation/)
- [Entire Codex integration](https://entire.io/blog/getting-started-with-codex-in-entire-cli)
