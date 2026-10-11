> Historical development notes. Current behavior and setup are documented in [the README](../README.md). References to earlier local-only screenshots are retained as history.

# Wanderlore — PRD v2

An offline story that follows your walk. Revised October 10, 2026 for a laptop-first prototype and the October 12, 12:29 PM IST challenge deadline (as checked on DEV).

## Experience

Choose folklore, mystery or fantasy, a 10/20/30-minute target, and a manual weather tag. Begin on a simulated route or use the browser's GPS. A local open-weight model turns a nearby place into a fictional chapter. Kokoro speaks it. Continue manually or enable automatic chapters. Pause at any time, request an ending, then save a reflection in the journal.

The welcome screen uses a hand-painted woodland and lantern illustration, parchment, and forest-green typography, following the user's request for a storytelling background. The active screen uses a data-driven route sketch.

## First release scope

- FastAPI server, small build-free ES-module web client, SQLite persistence.
- Gemma 3 1B via local Ollama, Kokoro with two selectable voices; both downloaded once.
- Local AI and a clearly labeled scripted preview are separate choices. Both can use local Kokoro audio. Model errors never silently fall back to scripted text.
- Sample mode uses fictional places and a simulated route. It proves the narration workflow, not real-world place awareness.
- GPS mode requires an accurate, fresh fix. Named GeoJSON features within 100 m can be referenced; when none exist, use a place-free observation story.
- Offline GeoJSON pack import, with an online OSM preparation script. During preparation the selected coordinates are sent to Overpass; during a walk no map calls leave the device.
- Weather is selected manually, never presented as a live forecast. Local browser time provides time-of-day context.
- Immutable quest/companion/object plus a short sequence of plot phases provide memory. Chapter history is saved, but full previous model responses are not recycled into the small-model prompt. Coherence is a test target, not a guarantee. The closing beat includes an authored resolution so the walk ends definitively.
- Non-overlapping narration, manual next chapter, pause/resume, closing chapter, and optional automatic continuation after a quiet interval.
- Stationary GPS samples suppress automatic beats; this heuristic needs outdoor validation.
- Journal, saved reflections, JSON export including route/chapters, and route sketch.
- Same-origin local assets and service-worker shell caching. Laptop server remains necessary: caching does not run the model inside the browser.

## Deployment and privacy

Laptop first at http://127.0.0.1:8765. A phone can later connect over a trusted private local network with trusted HTTPS. A pairing code protects API access from remote clients. GPS leaves the phone for the user's laptop, but the app sends no location or story to a cloud model. Ollama cloud features are disabled by the launcher.

Keep the browser tab visible. The first release deliberately pauses when hidden. Continuous locked-phone/background GPS and audio are unverified and are not promised. Airplane mode by itself disables Wi-Fi; a future phone demonstration must re-enable Wi-Fi for the local connection and accurately describe that setup.

## Deferred

BirdNET, Whisper replies, automatic fork detection, saved multi-walk story arcs, second-model comparisons, accounts, native mobile app, and seamless background operation. These do not block the first working demo.

## Acceptance and evidence

1. Local model text plus local Kokoro audio complete on the laptop. Record measured generation-plus-synthesis latency; aim for 8 s warmed, report actual results.
2. Scripted and AI modes have honest labels. Failures preserve the walk and permit retry.
3. Repeated request IDs create one chapter. Paused/finished sessions cannot generate new chapters.
4. Nearby-feature lookup uses geometry rather than arbitrary centroids and rejects stale/low-accuracy fixes.
5. Finished walks survive reload with notes and downloadable data.
6. Check laptop and narrow layouts and keyboard access.
7. A real 20+ minute outdoor walk, phone HTTPS setup, and internet-disconnected field test remain human/device verification before claiming challenge readiness.

## Weekend plan

October 10: complete local narration, sample route, persistence, interface, and desk tests.
October 11: choose a real walk, prepare its map pack, field-test, fix failures, and record the demo.
October 12 before 12:29 PM IST: finish the DEV write-up, attribute models/data/tools, and submit using the official template.

Writing and a real outdoor field report carry more value than adding untested integrations. Do not claim BirdNET, phone-only inference, zero latency, or a completed field test until demonstrated.
