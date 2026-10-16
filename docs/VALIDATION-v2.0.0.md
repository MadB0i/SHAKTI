# SHAKTI v2.0.0 — pre-publication verification

**Local checks complete; owner-authorized for publication on 16 October 2026.** [Actual audio terms and owner-reviewed scope interpretation](AUDIO-PROVENANCE-v2.0.0.md). This document records checks performed before publication; release/tag and Pages Actions records establish the final publication state.

## Final film and audio

The owner-final Clipchamp MP4 is unchanged: **30.000 seconds, 900 frames, 1080×1920**. SHA-256: `d4b11d61c774f820e17a3fee31ea9ad1e3dc769850c11744ace672f8ef5b6e28`. The runtime M4A and compressed watch film contain **identical audio packets and decoded samples** to that MP4: **zero added sample offset**, no remix or new sound. One compressed file remains under `public/audio/`.

Audio is **−21.29 LUFS / −6.66 dBTP**, unaltered; zero clipped samples or full-decode errors. The final MP4 played completely at normal speed in installed Edge with embedded audio enabled, zero dropped/corrupted frames and no playback error. Browser native-player preroll counters exceed the encoded count; the authoritative file contains 900 frames.

Desktop and mobile live IGNITE each used **one uninterrupted buffer source** through both 16 s and 17.6 s handoffs. No legacy resonance context/output and no footage-clip audio layer. Actual-output mute/unmute, pause silence, forward/backward seek and replay passed. The maximum sampled live clock difference was **57.59 ms**; this is a browser-clock observation, not a claim of zero physical device latency. Opening decoded PCM correlation to the approved source: 1.000000. Native AAC duration rounding was within one sample.

The first 16 seconds follow the soundtrack clock; all camera, material, geometry, title and scene cue times remain unchanged. The only `Experience.ts` change after normalization is this playback-clock binding. A content-derived request revision prevents cached v1 audio being loaded by the new build.

## Build, controls and cultural companion

TypeScript and production build pass. Existing cinematic regression suite passes: keyboard/touch ignition, pause/resume, repeated and racing seeks, fullscreen, mute, replay, hidden-tab pause, reduced-motion consent, loading/corrupt-media recovery and sharing fallbacks. Existing `/discover/` checks pass at 1440, 768, 390 and 320 widths, including calendar URL/reload/arrows, disclosures, navigation and visible focus. Cultural correction, illustrations, CSS and source text are unchanged. All 29 production asset URLs respond successfully, including fallback and OG images.

The build retains its existing large-bundle advisory; no build errors. Subjective audio quality and real screen-reader listening are not claimed by automated checks. The owner supplied final editorial/listening approval for this MP4.

## Presentation and cleanup

README uses own-film stills and a 768×456 animated three-act preview. Native GitHub Markdown was rendered in a GitHub page shell at desktop/mobile widths and inspected visually; no horizontal overflow. Correct heading hierarchy, descriptive image alternatives and native links are retained. Before/after screenshots are local review artifacts under `D:/Projects/SHAKTI/v2-preparation/`; those captures record the local pre-publication preview.

[Keep/remove report](ASSET-CLEANUP-v2.0.0.md) · [Exact deletion and backup hashes](deletion-manifest-v2.0.0.json). Eight media files (47,315,607 bytes) were removed locally after verified external backups in `D:/Projects/SHAKTI-Social-Masters/v2-preparation-2026-10-16/`. All reports, source files, creator credits, model/font/asset licenses and history remain. No WAV/audio experiments existed in this release checkout; none are proposed for commit. Personal social metadata stays ignored, with its records backed up outside Git.

## Release preparation

Package and lock version: 2.0.0. Release workflow validates an existing annotated tag against package version and hashes, takes its names/checksums/notes from that actual tag, refuses existing-release overwrite and runs the rights gate before publishing. It packages one final full-HD film, one website ZIP, credits and checksums. Legacy synthesis/export scripts remain as historical source but refuse execution over the approved film.

GitHub About description/homepage and focused festival/cultural topics have been updated; this metadata change uploads no audio. Existing live URLs responded successfully before publication. The v2 push starts from main `6041a8400ec315b7446182696517a95f092bcff7`; existing v1.0.0 tags/releases are preserved. Publication uses a normal new commit and annotated tag, without rewriting history.

The recorded owner approval and attribution-conditioned music terms satisfy the documented publication gate on the owner-reviewed scope basis. v2 download/tag links are verified after normal publication. No soundtrack replacement is made.

[Machine-readable verification](VALIDATION-v2.0.0.json) · [Development](DEVELOPMENT.md) · [Credits](CREDITS.md).
