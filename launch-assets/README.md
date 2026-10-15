# SHAKTI — Launch kit

**SHAKTI v1.0.0 launch kit.** Wan2.2 generation provenance and official license basis are documented; creator and third-party credits must accompany shared media.

[Open the review player](review.html) · [Final verification](FINAL-REPORT.md) · [Captions and required credits](social/CAPTIONS.md)

| Deliverable | File | Specification |
| --- | --- | --- |
| Instagram Reel / YouTube Short | [Final Reel](video/SHAKTI-Reel-1080x1920.mp4) | 1080×1920, 30.000 s, 900 frames, 20.58 MB |
| Desktop / LinkedIn film | [Desktop cinematic](video/SHAKTI-Desktop-1440x810.mp4) | 1440×810, 30.000 s, 900 frames, 11.99 MB |
| Vertical teaser | [Teaser](video/SHAKTI-Teaser-8.5s.mp4) | 1080×1920, 8.500 s, 4.61 MB |
| X clip | [Small teaser](video/SHAKTI-X-Teaser.mp4) | 540×960, 8.500 s, 1.32 MB |
| Instagram / YouTube cover | [Vertical cover](covers/SHAKTI-Reel-Cover-1080x1920.jpg) | 1080×1920 JPEG |
| GitHub / LinkedIn cover | [Wide cover](covers/SHAKTI-GitHub-LinkedIn-1200x630.jpg) | 1200×630 JPEG |
| README GIF | [Opening preview](../docs/media/shakti-preview.gif) | 270×480, 7 s, 10 fps, 2.54 MB |
| Lightweight full preview | [Preview film](../docs/media/shakti-cinematic.mp4) | 540×960, 30 s, 4.45 MB |

Films: H.264, progressive yuv420p, 30 fps, AAC stereo 48 kHz, fast-start MP4. Full films use High profile / Level 4.1. The titles and Bengali greeting originate in the app’s canvas text renderer. No editor UI is included. The final image is intentionally held from 27.6–30 seconds.

Created by **Rupjyoti Talukdar (MadB0i)**. © 2026 Rupjyoti Talukdar — original authored contributions. Flight Trishul: keshavckm1, CC BY 4.0; transformed and optimized. Preserve [full attribution and modifications](../public/art/trishul/keshav/ATTRIBUTION.md). [All credits](../docs/CREDITS.md).

The score is independently synthesized without samples; source-video music is excluded. The supplied footage was generated locally with Wan2.2 through ComfyUI and edited/exported in Clipchamp. [Exact rights gate and official terms](../docs/RIGHTS-AND-RELEASE.md).

## Reproduce / verify

Website: `npm ci`, `npm run build -- --base /SHAKTI/`, then `npm run preview -- --port 4186 --base /SHAKTI/`.

Browser checks use Python Playwright with an installed Chromium and Edge: `npm test`. With Pillow, NumPy and FFmpeg available, `tests/launch_capture.py` records the app (set `SHAKTI_URL` to the running server), `scripts/export-launch-kit.py` exports the kit, and `tests/launch_export_playback.py` checks the delivered MP4s. `scripts/compose-score.py` and `scripts/prepare-launch-media.py` reproduce the score and source edit. The latter requires the locally retained original clips; they are intentionally excluded from future source-control staging.

The release check `npm run check:release` verifies recorded rights evidence and owner publication approval.
