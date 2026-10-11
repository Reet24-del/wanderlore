> Historical development notes. Current behavior and setup are documented in [the README](../README.md). References to earlier local-only screenshots are retained as history.

# Immersive landing revision — October 10, 2026

The user's two reference screenshots inspired a full-bleed illustrated adventure landscape with text directly over the sky. The original split-column welcome page is replaced by a scene and a separate setup section below it. The existing walk, narration, journal, GPS, and import flows remain available.

## Artwork and motion

- Asset: `web/sunset-forest.png`, generated with the built-in OpenAI image-generation tool. Original artwork, not a copied game screenshot.
- Final prompt: “Create original full-bleed cinematic landscape illustration for Wanderlore storytelling website, landscape 1536x1024. Stylized hand-painted adventure game environment, strong depth from layered silhouettes, burnt terracotta and deep aubergine foreground pines framing left/right edges, distant copper mountains and a winding golden river leading toward a glowing peach sunset center-right. Tiny distant lookout cabin on a ridge at right, gentle luminous haze. Restrained palette ochre honey gold russet wine-dark brown. Large uninterrupted softly glowing amber sky in upper central 55 percent for dark title overlay. Dramatic low foreground rocks and pine branches, immersive, elegant, richly textured but clean silhouettes. Inspired by scenic wilderness adventure poster art and illustrated narrative games; entirely original composition. No text, typography, logos, UI, borders, watermarks, or people. This is the artwork only, not a website screenshot.”
- Landscape and embers move at different depths with the pointer. The glowing lantern uses CSS perspective, transformed faces, a flame, and slow swaying. This is an illustrated 2.5D scene with a CSS 3D object, not a fully modeled WebGL environment.
- Motion is disabled for `prefers-reduced-motion`. Touch devices retain the composition without pointer parallax.

## Sound

Original Web Audio synthesis produces soft filtered wind and occasional bird-like chirps. No audio service, microphone, or network download is involved. Audio starts on the first pointer/keyboard interaction, or the Enable sound control, to comply with browser autoplay restrictions. The mute setting persists. Ambience fades out outside the landing page, ducks during audio playback, and suspends while the page is hidden.

## Verification

- Browser checks: sound enable → on; mute → off; mute persists after reload; Find your story scrolls to the setup heading and transfers keyboard focus; genre control still updates.
- 390px and 320px widths: document width equals viewport width, no horizontal overflow.
- Desktop and mobile screenshots captured and visually reviewed. Header backing improved for text contrast over foreground trees; removed tiny low-contrast copy over the forest.
- JavaScript syntax checks pass; 13 existing API tests pass with one upstream test-client deprecation warning.
- Screenshots: `landing-immersive.jpg`, `landing-mobile.jpg`. The previous design references remain as historical artifacts.
- AudioContext activation and UI state verified in the browser; perceptual sound mixing still benefits from listening on the user's speakers/headphones.
