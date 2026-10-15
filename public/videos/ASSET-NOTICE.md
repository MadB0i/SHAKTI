# Delivery edit and generation provenance

The creator confirms that `divine-catch.mp4` and `divine-finale.mp4` were generated locally with **Wan2.2 using ComfyUI**, then edited/exported with **Clipchamp**. Source MP4 metadata corroborates the editing/export step. Official Wan2.2 model licensing and the generated-output statement have been reviewed. [License record](../../docs/COMFYUI-MODEL-LICENSES.md) · [retained generation attribution](../WAN2.2-NOTICE.txt).

Exact checkpoint variant/hash and workflow are not retained; no binary inspection is claimed. Model weights and ComfyUI software are not included in the website. Source audio is omitted in favour of SHAKTI's independently synthesized score. The two supplied source files remain unchanged locally and outside the distribution build.

`scripts/prepare-launch-media.py` produces video-only H.264 derivatives:

- Catch source **8.400–10.000** → film **16.000–17.600**. The impact cut removes the most inconsistent hand/weapon frames.
- Finale source **0.000–10.000** → film **17.600–27.600**, followed by a final-frame hold through **30.000**.
- Native 30 fps and 1× motion. Encoded pillar bars are cropped. A soft tracked shadow lift improves facial readability without generated repair, retouching or skin smoothing.
- A 0.2-second code dissolve bridges WebGL into the impact. Code-rendered antique-gold titles/greetings enter at 24–27.6 seconds. These are absent from source footage.
- Source audio is omitted. `audio/shakti-original.m4a` is independently synthesized by `scripts/compose-score.py`, with no external samples. It is not represented as authentic recorded traditional instrumentation.

No character meshes from a marketplace are used in the video shots. Their characters are not real-time 3D assets. Captures must retain the separate CC BY 4.0 credit for the WebGL flight Trishul by keshavckm1. See [credits](../../docs/CREDITS.md) and [rights status](../../docs/RIGHTS-AND-RELEASE.md).
