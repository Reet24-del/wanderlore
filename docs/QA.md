# Verification — October 11, 2026

## Current source and live checks

The latest application source matches the live Render release `3724a424aa1b795ba588edfbdc54a9419d38383e`. The repository completion update adds local setup, documentation, the license, tests, and published submission assets; it does not alter the app interface or redeploy it.

- 29 Python tests and five Node automatic-continuation scheduler tests passed in the deployment regression check. They cover geometry and polygon holes, fresh/accurate fixes, persistence, pairing, cross-site requests, idempotent concurrent requests, choices, closed stories, provider errors, hosted configuration, and telemetry scrubbing.
- In a live browser test, online Gemma plus ElevenLabs generated and played chapters. Choice selection influenced chapter two. Closing, Finish & save, reflection saving, and JSON export succeeded without browser console errors.
- With Continue automatically selected, chapter two generated and narrated without a selected choice or Next click. Turning the checkbox off prevented chapter three. Automatic mode waits eight seconds after narration, stops on pause/closing, and requires a visible tab. GPS mode still requires a fresh usable fix.
- The owner reported real phone location and movement working. The Codex browser on the Mac timed out, so agent-generated sample-route screenshots are not evidence of real GPS.
- On October 11, a fresh sample chapter was generated and voiced in 3.8 seconds for screenshots. Earlier hosted requests measured 3.5, 4.3, and 3.1 seconds. These are individual observations, not performance guarantees.
- Desktop layout was captured at 1440 × 1000 and mobile at 390 × 844. Mobile document width was 390 pixels, with no horizontal overflow in the checked landing view. Temporary viewport settings were reset.
- Six screenshots plus a cover were uploaded to the published DEV article. All story screenshots use a clearly labeled fictional sample route. See [the images](../submission/screenshots) and [published article](../submission/DEV-POST.md).

## Connected-service evidence

- Gemma: local generation through Ollama verified earlier; online hosted chapters verified through the live browser.
- ElevenLabs: generated narration played to completion with no media error. Roger supplies the hosted voice; perceived naturalness remains a listening judgment, not a parity claim with another product.
- Sentry: verified transaction and generation span, trace `51bdfd74bf8149c1b67ec73c12adc34c`, measured 3.28 seconds. This is a development generation trace, not the entire current hosted pipeline. [Screenshot](../submission/screenshots/08-sentry-trace.jpg).
- Tiger Data: four public summaries with local 768-dimensional embeddinggemma vectors; authenticated SQL-editor hybrid retrieval returned two Rumi Gate facts and one Janeshwar Mishra Park fact in 0.7 seconds. Its prepared export is loaded locally. Direct psycopg access failed TLS certificate verification; verification was not disabled. The CLI direct-connection path still needs a valid TLS endpoint.
- Render: live HTTPS deployment on the Free plan. No paid disk or compute was added. Saved data is temporary.

## Practical limits

A complete 20-minute outdoor walk, an internet-disconnected physical field test, and phone background operation are not verified. The app pauses when hidden. Nearby-place context depends on pack coverage and accurate GPS; the map does not locate the user. Small-model prose may repeat or introduce inconsistencies. Bird recognition, speech replies, automatic direction forks, cross-walk story arcs, and separate user accounts are not implemented.

The GitHub repository and hosted walk access remain private. Publishing the article did not change those permissions. Entire session capture remains incomplete; DigitalOcean, Vercel, and Copilot are not claimed.
