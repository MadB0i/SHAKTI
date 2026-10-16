> Historical v1.0.0 report. Its exports are archived outside Git; [published v1 release](https://github.com/MadB0i/SHAKTI/releases/tag/v1.0.0) remains unchanged. For current preparation see [v2 validation](../docs/VALIDATION-v2.0.0.md).

# SHAKTI — Final production report

15 October 2026 · Created by Rupjyoti Talukdar (MadB0i)

**Historical local production review.** The subsequently verified owner-confirmed Wan2.2 license basis is recorded in [the current license record](../docs/COMFYUI-MODEL-LICENSES.md). This file describes the earlier production pass; remote publication results are verified separately. No new footage was generated in that pass.

## Visual judgment

The film has a stronger progression from a quiet diya to the divine reveal, with a composed, readable greeting. The flame, lamp formation and hero Trishul remain its clearest real-time moments. Portrait is the strongest format; desktop now feels more deliberately composed, though the source remains a portrait shot. The finale’s face is easier to read without removing its directional lighting.

The following focused changes are complete:

- Removed the worst hand/weapon inconsistency by cutting into the existing impact: catch source 8.4–10 seconds now occupies film 16–17.6. The reveal follows at 17.6–27.6; a 2.4-second final-image hold gives the complete greeting room to settle. This is an editorial reduction of the defect, not reconstruction of the catch.
- Applied a feathered, tracked shadow lift to Maa Durga’s face in the delivery encode. Eyes, skin texture, highlights and natural side-to-side contrast remain intact. Source files are unchanged.
- Added a restrained color surround for widescreen footage; retained the clear title/subject separation. Slightly increased gateway material roughness and reduced reflection strength. No model, architecture or camera rebuild.
- Replaced uncleared embedded music with an original synthesized score spanning ignition, flight, gateway, contact, reveal and resolution. It is festival-inspired, not an authentic recorded dhaak/shankh performance.
- Added fullscreen and finale sharing, including a copyable-link fallback. Preserved the single-button opening, diya picking, keyboard/touch controls, auto-hiding HUD, clean capture and replay. Added an error poster and lightweight full-film fallback. Wrapped control labels and tightened finale spacing on the smallest phone layout. Full-resolution export compositions are unchanged.

SHAKTI / THE AWAKENING / শুভ দুর্গাপূজা / Happy Durga Puja remain code-rendered, using local Cinzel and correctly shaped Noto Serif Bengali. Typography leaves the face, lion and Trishul visible.

## Remaining weaknesses, by visual impact

1. **Source hand/Trishul continuity remains imperfect.** The impact edit conceals the most distracting frames; it cannot create a fully convincing physical catch. A truly seamless repair requires different approved source footage.
2. **The WebGL-to-footage style change remains perceptible.** The brief dissolve and common warm palette soften it, but the footage has a different level of detail and lighting. Desktop necessarily retains portrait-source staging.
3. **Gateway surfaces remain stylized.** The material adjustment is modest and preserves the approved geometry. It is not a photoreal temple reconstruction.

These are disclosed artistic limitations, not a proposal for another redesign cycle.

## Delivered files

[Complete launch kit and specifications](README.md) · [Local review player](review.html)

- [1080×1920 Reel, 30.000 seconds](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/video/SHAKTI-Reel-1080x1920.mp4)
- [1440×810 desktop film, 30.000 seconds](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/video/SHAKTI-Desktop-1440x810.mp4)
- [8.5-second vertical teaser](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/video/SHAKTI-Teaser-8.5s.mp4) and [small X clip](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/video/SHAKTI-X-Teaser.mp4)
- [Vertical cover](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/covers/SHAKTI-Reel-Cover-1080x1920.jpg), [GitHub/LinkedIn cover](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/covers/SHAKTI-GitHub-LinkedIn-1200x630.jpg), [social captions](https://github.com/MadB0i/SHAKTI/blob/v1.0.0/launch-assets/social/CAPTIONS.md)

Original browser recordings are retained in `evidence/launch/after/desktop-complete.webm` and `portrait-complete.webm`. That private evidence directory is excluded from the website and source-control staging.

## Evidence and acceptance

Actual complete app recordings and independent normal-speed exported-MP4 playback were tested. All 900 encoded frames of each full film were decoded; every-second contact sheets, critical cut strips, facial close-ups and final greeting frames were visually inspected. This is not a claim of human-equivalent continuous audiovisual perception. **A human listening check of the full new score remains outstanding.**

| Check | Result |
| --- | --- |
| Full exports | Both exactly 30.000 s / 900 frames / 30 fps; H.264 High Level 4.1, yuv420p, AAC stereo 48 kHz; fast-start verified |
| Independent exported playback | Portrait and desktop each reached the end at 1× with sound enabled; 900 displayed frames, **zero dropped frames**, no media errors |
| App capture performance | Desktop 58.70 fps, portrait 58.11 fps; p95 frame interval 16.8 ms; zero dropped/corrupted source-video frames on AMD Radeon / ANGLE D3D11 |
| Installed Edge | Full 30-second playback completed; zero source-video drops/errors. Headless scheduling measured about 143 fps; this is not a physical-display refresh claim |
| Controls | IGNITE by mouse/keyboard/touch, diya picking, rapid double ignition, pause/resume, replay, sound, scrubber, bidirectional/racing seeks, final-hold resume, hidden-tab pause, clean mode and fullscreen passed |
| Sharing | Native-share payload and denied-clipboard fallback verified; no real post/share was sent |
| Accessibility | Visible keyboard focus, named controls, 44px primary control heights, touch emulation and reduced-motion consent at the footage boundary passed. No screen-reader or physical-device claim |
| Layout | Desktop, 1080×1920 portrait, 390×844 phone, 768×1024 tablet and 320×720 phone checked; no page overflow |
| Errors/loading | Delayed video, HTTP 503 and damaged video tested: disabled IGNITE during loading, readable recovery, reload and full-film fallback |
| Production paths | `/SHAKTI/` build loads; runtime requests succeeded; MP4/audio MIME and HTTP 206 byte-range responses verified locally |
| Memory sample | JS heap after GC across five replay/seek cycles: 19.25–19.44 MB; backing storage about 24.03 MB. Limited sample, not total process/GPU memory |
| Loading footprint | About 20.62 MB initially requested; 2.58 s to ready locally. Not a mobile-network benchmark. Complete website about 25.93 MB including lazy fallback film |
| Audio analysis | Both full exports about −14.5 LUFS; true peaks −0.8 dBTP portrait / −0.6 desktop; zero full-scale samples and no internal 10ms digital-silence gaps in 0.5–29 s |
| Synchronization | Approximate waveform/image comparison estimates audio 40–48 ms behind the image, with 33ms image measurement resolution |
| Build | TypeScript and production build pass. Existing large-bundle warning remains: about 912 kB JS / 259 kB gzip |
| Safari | Unverified. Required WebKit build is absent; the older installed build did not finish the probe. No Safari/iPhone test is claimed |

Detailed machine results: `evidence/launch/after/regressions.json`, `export-verification.json`, `export-browser-playback.json`, `environment.json`, `sync.json`, `audio-continuity.json` and `delivery-checks.json`.

Before/after evidence: `evidence/launch/face-lighting-comparison.png`, `catch-edit-comparison.jpg`, `gateway-materials-comparison.jpg`, `desktop-surround-comparison.jpg`. Critical transition strips and final greeting screenshots are under `evidence/launch/after/`.

## Website, README and credits

The README is concise and visual-first, with a seven-second 270×480 GIF (2.54 MB), full preview, four highlights, stack, quick start and visible creator credit. Covers, About text and topics are prepared locally. The repo URL returned HTTP 200; the proposed Pages URL returned **404**. There is intentionally no fabricated Live Experience link, and remote preview files cannot be called uploaded or verified on GitHub yet.

The build uses a runtime allowlist: no original source clips, unused reference art, incoming archives, review evidence or private working files are copied. Font and model licenses, modification notices and dependency credits remain separate. [Asset inventory](../docs/asset-manifest.json). © 2026 Rupjyoti Talukdar applies only to original authored contributions; original code remains MIT.

## Rights gate and smallest next action

The owner confirms local ComfyUI generation and Clipchamp editing/export. The owner identifies Wan2.2; official Apache 2.0 model licensing and generated-output use statement are verified in the current license record. All new delivery clips are video-only, and all new exports use the independently synthesized score; the original embedded music is not distributed in the prepared website.

The cosmic background is recorded as **OpenAI ChatGPT-assisted artwork created for SHAKTI in October 2026**, with owner-confirmed provenance and no exclusive copyright claim. Official terms and the distinct CC BY/font/dependency obligations are documented in [Rights and release](../docs/RIGHTS-AND-RELEASE.md).

**Current release basis:** owner-confirmed Wan2.2 generation, verified official model license/output statement, retained asset credits and existing publication approval. See the current release record for remotely verified publication results.