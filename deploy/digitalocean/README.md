# DigitalOcean private demo

This package runs FastAPI, local Gemma (Ollama), Kokoro and Caddy HTTPS on one Docker-enabled DigitalOcean Droplet. Cloud hosting is online and stores walks on that server; it is not phone-only offline inference. The original local edition is unchanged. This is a paired private demo, not a multi-user SaaS: paired users share the journal. Do not distribute the pairing code publicly.

## Deploy after selecting an account and spending limit

1. Provision a Docker-enabled Linux Droplet. Start capacity planning at 4 vCPU / 8 GB RAM for this CPU inference workload; measure latency before choosing a final size. No performance guarantee. Add a domain A record pointing to the Droplet.
2. Allow inbound 80/443. Allow SSH only from your own IP using a DigitalOcean firewall. Never publish ports 11434 or 8766. Copy this repository, excluding personal `data/`, `.env`, `.git` and `.runtime`.
3. Copy `.env.example` to `.env` on the server. Set only the optional services you want. `chmod 600 .env`. Copy the two already-downloaded files from `models/kokoro/` into the same directory on the server (or use official release downloads linked in scripts/setup.sh).
4. From the repository root, run:

```sh
export WANDERLORE_DOMAIN=your-real-domain.example
docker compose -f deploy/digitalocean/compose.yaml up -d --build
docker compose -f deploy/digitalocean/compose.yaml exec ollama ollama pull gemma3:1b
```

5. Read the pairing code privately on the server:

```sh
docker compose -f deploy/digitalocean/compose.yaml exec app cat /app/data/pairing-code
```

Open the HTTPS domain, choose Setup, and pair. The app requires pairing even when a reverse proxy makes a request appear local. Cookies are secure in hosted mode. Import `docs/lucknow-places.geojson` in Setup. To install your prepared public lore, copy `data/lore.json` to `/app/data/lore.json` in the app container.

## Acceptance before sharing a demo

Check TLS, deny anonymous `/api/walks` and `/audio/...`, pair a phone, verify live GPS outdoors, generate a Gemma chapter with audio, restart containers and confirm persistence. Verify Sentry has only metadata if enabled. Make one successful ElevenLabs preview if configured. Capture genuine provider evidence; configuration alone is not a prize claim.

Back up the `walks` volume securely. Stop with `docker compose -f deploy/digitalocean/compose.yaml down`; do not add `-v` unless deliberately discarding saved walks. A powered-off Droplet can still incur charges; check billing before provisioning.

Sources: [DigitalOcean setup](https://docs.digitalocean.com/products/droplets/getting-started/recommended-droplet-setup/), [firewalls](https://docs.digitalocean.com/products/networking/firewalls/how-to/configure-rules/).
