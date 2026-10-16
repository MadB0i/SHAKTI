# SHAKTI v2.0.1 — focused correction validation

Prepublication checks passed on 16 October 2026. Scope: restore the previously reviewed discover implementation and correct the two README presentation assets. No soundtrack work, choreography changes or restoration of retired exports.

## Corrective port

Only `src/Discover.tsx`, `src/DiscoverArt.tsx`, `src/discover.css`, the 16,408-byte OFL Bengali font subset and relevant correction evidence/tests were ported from the earlier reviewed v1.0.1 work. Old package, workflow, approval and media changes in that patch were not applied. Patch SHA-256: `3b2f3614c1debe963e1b9244e5dc6b6e0c6fcbd451d696d87f91c5eae73a6461`.

The page explicitly attributes Elephant/Horse arrival and Boat departure to the Bengali panjika comparison reported by Anandabazar. Printed panjika publisher pages were not inspected. Drik Panchang's convention is distinguished; conflicting Assamese reports and Kamakhya's distinct practice remain qualified. See [the evidence and boundaries](DISCOVER-CORRECTION-v1.0.1.md).

## Verification

- TypeScript check and production build for `/SHAKTI/`: passed. Existing large cinema bundle advisory remains unchanged; discover does not load that bundle.
- Discover at 1440, 768, 390, 360 and 320 px: no horizontal overflow or script errors; calendar/URL/reload/native radio arrows, keyboard disclosures, chapter links, visible focus, scroll entrances, pause/resume, OS reduced motion and no-observer fallback passed. Accessibility-tree snapshots retained; axe WCAG 2 A/AA, 2.1 AA and 2.2 AA scans reported zero violations in all five viewports. This is automated/keyboard evidence, not a claim of a manual screen-reader certification.
- Cold simulated mobile profile (150 ms latency, 1.6 Mbps down, CPU 4×): LCP 1240 ms; CLS 0; discover resource transfer 192,355 bytes. Simulation, not field data.
- Both complete MP4s fully decode: exactly 30.000 seconds and 900 encoded video frames each. Full-HD owner film and public runtime movie both played to completion in Edge, with no corrupt or dropped frames in the recorded native playback checks.
- Complete IGNITE desktop/mobile journeys passed. One soundtrack source throughout uninterrupted playback, no additional resonance output, all video clips muted. Handoff at 16/17.6 seconds remained continuous; pause/mute/seek/replay passed. Maximum sampled film/audio drift 0.0571 seconds; browser opening PCM correlation exceeded 0.9999. Existing audio files and implementation are byte-identical to v2.0.0.
- README hero: one uncomposited 1080×1920 frame at 24.2 seconds in the approved film; 190,396 bytes. GIF: 432×768, 96 frames at 10 fps, exactly 9.6 seconds, 8,344,531 bytes; Diya → Trishul → cosmic gateway → Maa Durga, one shot at a time with brief fades through black. Full source framing preserved. All GIF frames decoded; source ranges are recorded in [media provenance](README-MEDIA-v2.0.1.json).
- Approved full-HD film, public runtime film, extracted audio, Hybrid/Experience/Resonance source, original credits and audio provenance hashes unchanged. No cleanup reversed. Existing v2.0.0 release and tag identities recorded before publication.

Detailed evidence: [VALIDATION-v2.0.1.json](VALIDATION-v2.0.1.json). Public GitHub README rendering, live discover interactions and deployed media/release checks must also pass after deployment; those screenshots and final live report are retained outside Git to avoid an unrelated evidence-media commit.
