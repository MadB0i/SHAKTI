# v1.0.0 publication procedure

The recovered checkout preserves the existing GitHub history. SHAKTI's main experience is the complete 30-second hybrid cinematic, with The Story of Shakti at `/discover/`.

## Approval and license basis

The owner authorised normal push, an annotated v1.0.0 tag, GitHub Release and Pages deployment. The owner confirms local Wan2.2 generation through ComfyUI and editing/export through Clipchamp. Official Wan2.2 Apache 2.0 licensing and its generated-output use statement are retained in the [model-license record](COMFYUI-MODEL-LICENSES.md). Exact model variant and workflow were not retained. No model weights, ComfyUI software or private evidence are bundled.

## Publication and verification

1. Run the recorded release gate, TypeScript/build checks and production browser checks. Keep the original cinematic and source files intact.
2. Commit and push normally to the existing `main` history; never force-push.
3. Configure GitHub Pages to use Actions. Dispatch `pages.yml`, wait for deployment success, and verify the actual cinematic and story page before adding live README links.
4. Create and push annotated `v1.0.0` on the verified final commit. Dispatch `release.yml` with that tag to build the website archive, copy the portrait/desktop films, calculate SHA-256 checksums and publish the prepared release notes. This packages existing media on GitHub without a second local upload.
5. Dispatch `pages.yml` at the release tag. Verify that the live deployment corresponds to that commit.
6. Verify desktop/mobile navigation, uninterrupted 30-second playback, both video decoders, the cultural page, website credits, rendered README GIF, and the hashes of all published release downloads.

The GitHub Release and Actions deployment histories are the public publication records. Local screenshots and detailed verification JSON remain in ignored evidence folders rather than the source repository.
