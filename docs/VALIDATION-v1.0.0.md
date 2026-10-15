# v1.0.0 candidate validation

15 October 2026. Local review only. No push, tag, upload or publication.

| Check | Result |
| --- | --- |
| TypeScript | `npm run typecheck` passed; also run by the production build. |
| Production build | `npm run build -- --base /SHAKTI/` passed. The existing cinematic chunk is approximately 213 KB gzipped; Vite emits its size advisory. The separate story chunk is approximately 8.8 KB gzipped, plus 3.5 KB gzipped CSS. |
| Story interaction | Calendar mouse/touch selection, native arrow-key radio navigation, URL/reload persistence, six native ritual disclosures, anchor navigation and browser Back passed. |
| Responsive layouts | Browser-emulated 1440×900, 768×1024, 390×844 and 320×740; no horizontal overflow. Desktop and phone screenshots inspected. |
| Navigation | Quiet landing story link, post-film “Explore Durga Puja”, return to film, direct `/discover`, `/discover/`, `/discover/index.html` and deep links passed. |
| Static hosting | Separate Python static server with **no SPA fallback** successfully served both physical entries and their assets under `/SHAKTI/`; a nonexistent page returned 404. |
| Actual film | IGNITE, WebGL opening, gateway, both actual playback clips, greeting and completion verified. Uninterrupted 30-second playback passed in Chromium and installed Edge. Both clips decoded with **zero dropped or corrupted frames** on this machine. Edge wall duration was 30.094 seconds. |
| Existing regression suite | Desktop/mobile pause/resume, seek in both directions and racing seeks, fullscreen, share payload/fallback, mute gain, hidden-tab pause, replay, diya picking, clean-view focus restoration, reduced-motion consent, delayed video and HTTP/damaged-video recovery passed. |
| Network and console | New production checks: zero HTTP errors, console errors or uncaught page errors. The story made no requests for film clips, Trishul assets or the cinematic JS chunk. |
| Keyboard and accessibility | Native Tab traversal with visible focus passed at all four widths. Pinned axe-core 4.10.3 reported **zero violations** for desktop/mobile story, an expanded ritual, film entry and finale. |
| Contrast | Story primary/base 16.33:1; secondary/surface 9.93:1; tertiary/surface 8.07:1; secondary/selected card 7.21:1; gold/selected card 7.57:1; meaningful control border/surface 3.63:1; focus/base 11.06:1. |
| Preservation | 75 files hashed against the pre-edit snapshot. Cinematic scene code, source/delivery media, legacy source, references and incoming assets unchanged. Only `public/credits.html` intentionally changed within that snapshot. |
| Release gate | The recorded gate now passes on owner publication approval and the verified official Wan2.2 license/output-use statement. |

## Visual review

First impression: a cultural companion to the film, with a clear calendar entry and an illuminated manuscript aesthetic. The headline and original Goddess illustration lead; the numbered chapter navigation exposes the content structure. Calendar cards and ritual disclosures visibly communicate their interactions. Both desktop and phone renders retain readable measures, ordered headings, consistent gold rules and generous section spacing. The cinematic remains the actual original experience.

No unresolved functional or layout defects were observed in these checks. The source article/card/typography system uses scoped CSS; the discovered production CSS preload problem and radio hit-testing issue were corrected before the passing run.

## Limits and release blockers

Browser mobile emulation is not a physical-device test. A manual screen-reader session and human full-volume soundtrack audition were not performed. Axe marked some contrast checks “incomplete” because of gradients/canvas content; measured story token pairs and visual inspection supplement that scan. This report is not a claim of comprehensive WCAG certification.

The generation-model condition is resolved on owner-confirmed Wan2.2 use and its official license/output statement; [evidence](COMFYUI-MODEL-LICENSES.md). Remote publication results are recorded separately after verification.

## Evidence

- [Discover desktop](../evidence/v1-preparation/browser/discover-desktop.png) · [desktop hero](../evidence/v1-preparation/browser/discover-desktop-hero.png)
- [Discover phone](../evidence/v1-preparation/browser/discover-mobile.png) · [phone hero](../evidence/v1-preparation/browser/discover-mobile-hero.png)
- [Film desktop landing](../evidence/v1-preparation/browser/film-desktop-landing.png) · [finale with Explore link](../evidence/v1-preparation/browser/film-desktop-finale.png)
- [Film phone landing](../evidence/v1-preparation/browser/film-mobile-landing.png) · [phone finale](../evidence/v1-preparation/browser/film-mobile-finale.png)
- [Browser results](../evidence/v1-preparation/browser/results.json) · [existing cinematic regressions](../evidence/v1-preparation/browser/cinematic-regressions.json)
- [Accessibility](../evidence/v1-preparation/browser/accessibility.json) · [contrast measurements](../evidence/v1-preparation/browser/contrast.json) · [static routes](../evidence/v1-preparation/browser/static-routes.json)
- [Preservation result](../evidence/v1-preparation/preservation-result.json) · [build asset inventory](asset-manifest.json)
