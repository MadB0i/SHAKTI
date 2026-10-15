# Historical Git recovery and distribution review

Recovery snapshot: 15 October 2026, before the first publication. This file retains the initial repository state and local test record. Current public publication records are the [GitHub Releases](https://github.com/MadB0i/SHAKTI/releases) and [Pages workflow runs](https://github.com/MadB0i/SHAKTI/actions/workflows/pages.yml). Wan2.2 licensing was subsequently verified as recorded below.

## Repository recovery

- Remote: https://github.com/MadB0i/SHAKTI (public), default branch `main`.
- Remote baseline and recovered HEAD: `d0b6672762e57e65bdf412f4c1f867f640425cee`.
- Separate full-history clone: `D:\Projects\SHAKTI-release-v1.0.0`.
- The remote contains one README-only commit. Its original README remains in Git history; the prepared README replaces its outdated claims and broken placeholder links in the uncommitted worktree.
- 119 files transferred from the validated source and SHA-256 verified before documentation updates. Original workspace, cinematic code, media, references and legacy source remain preserved. `node_modules`, builds, evidence, source clips, raw references and caches were not transferred as release content.
- Locked installation and production build succeeded. All 27 built files initially matched the original validated inventory exactly. Documentation and credits were subsequently updated at the owner's request.
- No force operations, history rewrite, deletion of project files, commit, push, tag or GitHub Release creation occurred.

## Current provenance finding

Owner-confirmed **Wan2.2 via local ComfyUI**, edited/exported with Clipchamp. The official Wan2.2 model license and generated-output use statement have now been verified. Exact checkpoint variant/hash is not retained. [License record](COMFYUI-MODEL-LICENSES.md).

## Technical verification

- Clean IGNITE landing, actual 30-second hybrid playback, both real clips and the /discover cultural page passed in the recovered checkout.
- Desktop/mobile navigation, 320/390/768/1440 widths, date controls, reloads, disclosures, keyboard focus, media decoding and reduced motion passed with no HTTP/console/page errors.
- Existing cinematic suite passed pause/seek/replay/fullscreen/share/mute/failure recovery and uninterrupted installed Edge playback (30.032 seconds, zero dropped/corrupted video frames).
- Plain static hosting without an SPA fallback passed /discover, /discover/, /discover/index.html, actual film entry, licenses and credits under /SHAKTI/.
- README GIF decoded as 70 frames at 270×480; local README preview/film/credit links exist. Release-download/live-README links cannot be verified until there is a public release.
- The package audit reports one high Vite and one moderate esbuild development-tool advisory. These tools are not served by static GitHub Pages. No forced dependency upgrade was performed; development-tool upgrades remain a separate maintenance item.
- No obvious credential values or credential files were found in the allowlisted release content. Build/evidence/cache paths are ignored and will not enter the proposed commit.

## Initial public state (before release)

At the initial recovery inspection, the remote pointed at the baseline above and there was no v1.0.0 tag or Release. GitHub's Pages configuration API returned 404, and https://madb0i.github.io/SHAKTI/ returned HTTP 404. These were pre-publication results, not the eventual release status. The prepared cinematic remains the intended main experience; no static substitute was introduced.
