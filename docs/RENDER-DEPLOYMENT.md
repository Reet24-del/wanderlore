# Hosted demo

Live URL: https://wanderlore.onrender.com

Render service: `srv-db5n0gflk1mc73aidbu0`, Free plan, Singapore. No paid disk or database is configured. The deployment uses online Gemma through Google AI Studio and ElevenLabs within existing account quotas; local Ollama and Kokoro remain available in the desktop installation.

Use the private access code saved in `data/render-access.txt` to pair a phone through Setup. This code protects a shared demo journal. API keys are private server settings and must never be pasted into the app or committed.

For real location, open the HTTPS URL in the phone's normal browser, pair it, select Use my location, and allow browser location access. A successful sample route does not verify real GPS. Nearby named-place context needs a map pack covering the current area; otherwise the story uses general surroundings.

The free server sleeps after inactivity; waking can take 50 seconds or more. Saved walks and audio use temporary storage and can disappear when the service sleeps, restarts, or redeploys. Export walks you want to keep.

GPS is processed by the hosted Wanderlore server. Story context and nearby place names go to Google, while raw landmark coordinates and distances are stripped from generation requests. Chapter text goes to ElevenLabs. Google free-tier prompts may be used to improve its products.

Final release: `3724a424aa1b795ba588edfbdc54a9419d38383e`, Render deployment `dep-db5nl2navr4c739ed13g`. Story, Voice and Preview voice controls are removed from the landing form; configured defaults still generate and narrate chapters.

Live browser smoke test on October 11, 2026: private pairing succeeded; real online Gemma plus ElevenLabs chapters were ready in 3.5 and 4.3 seconds. The second chapter acknowledged the selected lantern-keeper choice. Audio reached readyState 4 and played with no media error. The closing chapter was ready in 4.2 seconds; Finish & save, reflection saving, and JSON export succeeded. The downloaded export contained the reflection. No browser console errors were reported. This test used the explicitly selected fictional sample route; the agent did not directly test phone GPS. The owner subsequently reported that real location and movement work on their phone; Mac location timed out.

Automatic continuation regression verification: 29 Python tests and five Node scheduler tests passed. With the checkbox enabled during live narration, chapter two generated and narrated without selecting any option or pressing Next chapter (ready in 3.1 seconds). Turning the checkbox off prevented chapter three from being generated; the test walk remained at two chapters and was saved. Automatic mode waits eight seconds after narration, does not require a choice or movement, and stops on pause or the closing chapter. GPS chapters still require a fresh accurate real reading.

The DEV submission is now [published](https://dev.to/reet_singh_ee97da2986538e/wanderlore-what-if-your-next-walk-had-a-plot-a3g). Source and hosted-walk access remain private.
