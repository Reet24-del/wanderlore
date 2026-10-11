---
title: "Wanderlore: What if your next walk had a plot?"
published: true
tags: devchallenge, hf26challenge, ai, webdev
canonical_url: https://dev.to/reet_singh_ee97da2986538e/wanderlore-what-if-your-next-walk-had-a-plot-a3g
---

![Wanderlore's illustrated sunset landing page on desktop](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/bzivfng3z8r9iokkxjjw.jpg)


*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05).*

The first time I tried to test my walking app properly, I couldn't even get it to find me.

I was on my laptop, staring at another location timeout. I kept wondering what was wrong. How was I supposed to build a story that followed a walk if it couldn't tell where I was?

Then I tried it on my phone. It detected my location and picked up my movement. After all that testing at a desk, the part that finally worked was the part that meant leaving it.

That little moment made Wanderlore feel real to me.

I wanted a walk to have a little anticipation: a reason to notice something, a character to follow, a small mystery waiting around the next chapter. If you've ever wanted a reason to step outside but couldn't quite find one, this is the feeling I built it around.



## What I Built

**Wanderlore turns a walk into a narrated, interactive story.**

You choose folklore, mystery, or fantasy, decide how long you want to wander, and tell it what the weather looks like. The page responds too: choose rain and the scene gains drizzle, with rain ambience after you enable sound.

When you begin, Gemma writes a short chapter and a narrator reads it aloud. In location mode, each new chapter uses your latest position and nearby named places when your selected map pack covers the area. Your earlier chapters and decisions help shape what happens next.


![Choose a genre, duration, weather, and location mode on desktop](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/ewdcfbpks2nr17hzjpak.jpg)

The choices are small invitations into the story. Do you look more closely at the lantern? Ask its keeper a question? Offer to help? Your answer becomes part of the next chapter's context.

Some days you might want to make every decision. Other days, you might just want to listen. **Continue automatically** lets the storyteller choose and starts the next chapter after narration finishes. Keep the browser visible while using it; background and locked-screen continuation are still future work.

When you're done, save the walk, leave a reflection, and export your story. I like the idea of coming home with a small memory of what you noticed.

## Demo

**[Open the live preview](https://wanderlore.onrender.com/)**

The hosted walk currently requires a private demo access code. The screenshots below show the live experience without exposing a personal route.


![Wanderlore landing page in a mobile browser viewport](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/dxq00zrrb8y74zxs4l3j.jpg)

*Mobile layout, captured at 390 × 844 pixels in a browser. Real location and movement were also tested on my phone.*


![A narrated chapter and three story choices in the mobile layout](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/i97obnsswm7twcgq0zt5.jpg)

*This chapter uses Sample walk: its route and place names are fictional. It was generated and voiced in 3.8 seconds in this particular test.*


![Desktop story with its illustrated sample route and choices](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/6hmk2u3g3yv1jkm394tb.jpg)

For a first try, choose ten minutes and whichever genre you feel like hearing. On a phone, allow location and use **Use my location**. On a laptop, **Sample walk** lets you explore the storytelling without relying on desktop location services.

The sketch records the story's route; it doesn't provide walking directions. The current Lucknow map pack covers central and adjoining areas. You can import a GeoJSON pack for another area; without matching nearby places, the story uses general surroundings.

## Code

**[Wanderlore on GitHub — currently private](https://github.com/Reet24-del/wanderlore)**

The app uses Python, FastAPI, and a responsive HTML/CSS/JavaScript frontend. The application code is GPL-3.0; model and map data have their own terms. OpenStreetMap contributors provide the underlying place data. I used Codex to help implement, debug, and test the project.

## How I Built It

**Gemma is the story engine.** The local setup supports Gemma 3 through Ollama. The hosted preview uses `gemma-4-26b-a4b-it` through Google AI Studio because the small free hosting instance cannot run the local model stack. Chapters carry forward the previous story, selected choices, genre, weather, and available place context.

**ElevenLabs supplies the hosted narration.** I wanted the voice to feel like someone telling you a story, with enough warmth to keep listening. The hosted version uses the Roger voice. The local setup also supports Kokoro after downloading its voice assets.

**Tiger Data supplies a small, sourced place-context pack.** I stored four summaries of public Lucknow sources in PostgreSQL with pgvector. Keyword and vector results are combined with reciprocal rank fusion. A verified retrieval produced context for Rumi Gate and Janeshwar Mishra Park, which is exported for the storyteller to read. This is a prepared context pack; walking doesn't trigger a database query for every step. The resulting tale is fiction, even when it includes a real place.

**Sentry makes the wait visible.** I instrumented the chapter pipeline with a `wanderlore.chapter` transaction and spans for generation and speech. One verified development trace for Gemma generation measured 3.28 seconds. Seeing where time goes helps me assess the pauses between chapters. The trace integration exports timing and model metadata while excluding prompts, story text, GPS, cookies, and request bodies.


![Sentry waterfall showing the Wanderlore chapter transaction and Gemma request lasting 3.28 seconds](https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/u33d36gw43g7ed5t1hte.jpg)

**Render hosts the HTTPS preview on its Free plan.** That made phone testing possible without running the server on my laptop. The hosted version needs internet for generation and narration. Free hosting can sleep and reset saved files, so exporting a walk matters.

Verification included 29 passing Python tests, five automatic-continuation scheduler tests, and a live browser check where a second chapter started without selecting a choice or pressing Next. My phone detected location and movement; desktop location remained unreliable on my setup.

## Why Does Open Innovation Matter?

For Wanderlore, it means having a path to storytelling on your own machine. Gemma's available weights let the local version generate chapters through Ollama, and Kokoro provides a local voice option. After the models and assets are downloaded, that setup can work offline with the local server running.

The hosted preview trades that independence for easier access. It sends story context and nearby place names to Google, and narration text to ElevenLabs. Raw landmark coordinates are stripped from the generation payload, although the hosted server still processes GPS. These are different ways to run the same idea, with different privacy and connectivity needs.

I also want people to be able to improve the experience: bring their own map pack, experiment with a narrator, or make the choices more interesting. Open application code makes those changes possible.

## Prize Categories

I'm entering these categories based on the integrations above:

- **Best Use of Gemma** — context-aware chapter generation, with local and hosted inference paths.
- **Best Use of ElevenLabs** — spoken narration for generated chapters.
- **Best Use of Tiger Data** — pgvector and keyword retrieval for sourced place context.
- **Best Use of Sentry Agent Tracing** — instrumented generation and narration, with trace evidence shown above.
- **Best Use of Render** — the deployed HTTPS web experience used for phone testing.

If there's a familiar path near you, that's where I'd start. Pick a mood, give yourself ten minutes, and see what you notice when there's a story waiting for you.

I'd love to hear which genre you'd take on your first walk—and what you would want to happen next.
