> Historical development notes. Current behavior and setup are documented in [the README](../README.md). References to earlier local-only screenshots are retained as history.

# Wanderlore design

Direction: an illustrated field journal. Forest ink #243c32, warm paper #f5f3eb, muted sage #dde2d3, thin dividers, Georgia display/story type and system sans controls. Large touch targets, restrained borders, no external fonts or assets.

Initial generated concept: desktop setup and companion active/journal states, preserved in docs/concept.png. User then requested a more storytelling-oriented background. The implementation replaces the welcome map with the locally bundled woodland painting in web/woodland.png. Actual route data remains on the walking screen. The welcome caption sits on a parchment inset to maintain contrast over trees.

Functional additions to the concept: Setup button, visible narrator choice, labeled duration/weather inputs, pause-on-hidden behavior, explicit scripted/AI labels, error notices, reflection and export. These are necessary for honest setup and a working offline product.

Welcome copy: Wanderlore; Your walk; Journal; Setup; Every path has a story.; A little wonder. A longer way home.; MAKE IT YOURS; Folklore; Mystery; Fantasy; Time to wander; Weather, as you see it; Sample walk; Use my location; Begin the walk; Sample route · No location needed; Narrator; Familiar places. Unfamiliar possibilities.; The next chapter is just outside.; Made for wandering, not scrolling.

Components: full-width masthead, two-column setup/illustration, genre button group, native select controls, mode radios, full-width primary action; two-column story/route during a walk; journal list; one setup dialog. On phones the story illustration precedes setup and walking content remains before the map.

Generated artwork prompt: a winding pale woodland path, lantern on a weathered trail post, layered sage trees, drifting mist and distant hills; gouache and pencil texture on parchment; no people, buildings or text. Built-in image generation was used. No generated screenshot is used as interactive UI.

Source concept prompt: “Complete desktop Wanderlore app and compact mobile active/journal states; warm paper #f5f3eb, forest #243c32, sage, Georgia-like display type, system sans controls; header Your walk/Journal; genre, duration, weather, sample/GPS controls; route-map region and ruled footer.”

Final background prompt: “Landscape 3:2 literary storybook painting; winding pale woodland footpath, warmly illuminated lantern on a weathered trail post, soft sage layered trees, mist and distant hills; hand-painted gouache and delicate pencil texture on parchment; muted sage, olive, cream, forest green and amber accents; no humans, buildings, text or logos.”
