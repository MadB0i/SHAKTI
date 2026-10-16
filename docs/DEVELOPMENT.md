# Developing SHAKTI

SHAKTI combines a 16-second real-time WebGL opening with locally generated cinematic footage and code-rendered greetings. The cultural companion lives at `/discover/`. React, TypeScript, Three.js, GLSL, GSAP and Vite power the experience. [Accurate film/model provenance](COMFYUI-MODEL-LICENSES.md) and [asset credits](CREDITS.md) remain separate from the invitation on the README.

Node.js 20.19 or newer:

```sh
npm ci
npm run dev
```

```sh
npm run typecheck
npm run build -- --base /SHAKTI/
npm run preview -- --port 4187 --base /SHAKTI/
```

The production allowlist in `vite.config.js` includes runtime media, fonts, fallback/OG images and their notices. Both `/SHAKTI/` and `/SHAKTI/discover/` have physical entry files for GitHub Pages.

```sh
npm test
npm run test:discover
npm run test:audio
npm run check:release
```

Set `SHAKTI_URL` to the preview origin, including `/SHAKTI`, for Python Playwright tests. Use a Python environment with Playwright and its Chromium browser installed. Tests record local evidence under ignored `evidence/`.

## Film and audio

`docs/media/shakti-cinematic.mp4` is the owner's final 30-second full-HD edit. Preserve it. `public/media/shakti-film.mp4` is a smaller watch/fallback copy; its audio packets are copied unchanged. `public/audio/shakti-original.m4a` is the only runtime audio file, extracted from the owner's edit without transcoding. A content-derived query revision prevents reuse of a cached v1 soundtrack. It plays on one timeline through IGNITE, the 16-second handoff, pause, seek and replay. The legacy oscillator cue is disabled and opens no audio context. The WebGL opening follows the soundtrack clock while retaining every original cue time; the audio source remains active across both video handoffs. Explicit pause/seek/replay controls still govern source lifetime. Source clip audio is muted.

The old synthesis/export scripts are retained as historical source only and refuse to overwrite the approved film. Personal launch/social masters are stored outside Git in `D:\Projects\SHAKTI-Social-Masters\`; old published downloads remain on the v1.0.0 release. [Cleanup manifest](ASSET-CLEANUP-v2.0.0.md).

## Publication

The release workflow takes an existing annotated `v<package version>` tag, validates the recorded rights/verification gate, builds the site, and packages one full-HD movie, one website archive, credits and SHA-256 checksums. Existing releases/tags are never updated in place. Release notes are selected by the actual tag. Pages is dispatched separately after checks pass.

Publication requires the recorded owner approval, source terms, exact film/audio hashes and technical checks in `release-status.json`. [Actual music terms and owner-reviewed publication basis](AUDIO-PROVENANCE-v2.0.0.md).
