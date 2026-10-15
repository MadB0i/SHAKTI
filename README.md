<h1 align="center">SHAKTI — The Awakening</h1>
<p align="center"><em>One flame. A thousand lights. The awakening of Shakti.</em></p>
<p align="center"><a href="docs/media/shakti-cinematic.mp4"><img src="docs/media/shakti-preview.gif" width="270" height="480" alt="A golden diya ignites and its light becomes a Trishul." /></a></p>
<p align="center"><a href="https://madb0i.github.io/SHAKTI/"><strong>Ignite SHAKTI · Live experience</strong></a> · <a href="https://madb0i.github.io/SHAKTI/discover/">The Story of Shakti</a></p>
<p align="center"><a href="docs/media/shakti-cinematic.mp4"><strong>Watch the full cinematic · 30 seconds</strong></a> · <a href="https://github.com/MadB0i/SHAKTI/releases">Releases & downloads</a></p>
<p align="center">Created by <strong>Rupjyoti Talukdar (MadB0i)</strong><br/>শুভ দুর্গাপূজা · Happy Durga Puja</p>

Ignite a diya and follow its light through a cosmic gateway to Maa Durga. **SHAKTI** is an interactive, 30-second Durga Puja film, composed for both portrait and desktop.

- **One flame begins the journey.** A minimalist diya and IGNITE landing.
- **Light becomes movement.** Real-time WebGL, lamp propagation and a Trishul's flight.
- **A cinematic awakening.** A 16-second WebGL opening transitions into locally generated Wan2.2 footage, code-rendered greetings and an original synthesized score.
- **Your own pace.** Pause, seek, replay, mute and fullscreen controls, with keyboard and reduced-motion support.

### The Story of Shakti

A separate `/discover/` cultural companion explores the 2026 Kolkata Bengali calendar, Maa Durga and Mahishasura, the festival's history, rituals, and Bengal/Assam context. Original vector illustrations, an interactive calendar and short editorial passages continue the film's antique-gold, crimson and near-black world.

Open it through **The Story of Shakti** on the landing or **Explore Durga Puja** after the film. Calendar differences and religious traditions are qualified in context, with compact links to UNESCO, museums, tourism authorities and Drik Panchang. [Research and sources](docs/DISCOVER-SOURCES.md).

### Run locally

Node.js **20.19+**:

```sh
npm ci
npm run dev
```

`npm run build` checks TypeScript and creates the production site. `npm run preview` serves that build. For GitHub Pages:

```sh
npm run build -- --base /SHAKTI/
npm run preview -- --port 4187 --base /SHAKTI/
```

Both `/SHAKTI/` and `/SHAKTI/discover/` have physical production entry files. Python Playwright checks cover the film and story page: `npm run test:discover` and `npm test` (set `SHAKTI_URL` for another preview origin). [Validation](docs/VALIDATION-v1.0.0.md).

**Built with:** React · TypeScript · Three.js · GLSL · GSAP · Vite. Video generation: **Wan2.2 via local ComfyUI**. Editing/export: **Clipchamp**.

### Credits & licensing

© 2026 **Rupjyoti Talukdar** — original authored contributions. Original code, procedural scene assets, vector illustrations and synthesized score: [MIT](LICENSE).

- **AI cinematic footage:** owner-confirmed **Wan2.2**, generated locally using **ComfyUI**, edited/exported in **Clipchamp**. Official Wan2.2 models use Apache 2.0; the project states it claims no rights over generated content. [Model license and provenance](docs/COMFYUI-MODEL-LICENSES.md).
- **Flight Trishul:** [keshavckm1](https://sketchfab.com/3d-models/trishul-7d154946cba44ac7ae858bc205727581), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); [modifications and full attribution](public/art/trishul/keshav/ATTRIBUTION.md).
- **Cinzel / Noto Serif Bengali:** [SIL OFL notices](public/fonts/ATTRIBUTION.md).
- **Cosmic artwork:** project-specific ChatGPT-assisted artwork, with owner-confirmed provenance and no exclusive AI-output copyright claim.

Model weights and ComfyUI software are not bundled. Source clip audio is excluded; the release uses the original synthesized score. Third-party materials retain their own terms, including GSAP's separate license. No model, tool or asset creator endorsement is implied.

[Complete credits](docs/CREDITS.md) · [Dependency notices](docs/DEPENDENCY-LICENSES.txt) · [Release notes](docs/RELEASE-v1.0.0.md) · [Launch kit](launch-assets/README.md)
