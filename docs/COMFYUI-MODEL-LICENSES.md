# Wan2.2 / ComfyUI generation license record

Reviewed 15 October 2026. The owner identifies both cinematic clips as **Wan2.2**, generated locally using **ComfyUI** and edited/exported in **Clipchamp**. This is the release provenance; no hosted generation service is attributed.

## Evidence and scope

- Owner confirmation establishes the generation model family and local tool. The supplied MP4 encoder metadata independently records Clipchamp editing/export.
- [Official Wan2.2 repository](https://github.com/Wan-Video/Wan2.2#license-agreement) states that its models use **Apache 2.0** and that the project claims no rights over generated content, subject to its stated terms and applicable law. The official model cards corroborate this, including [I2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B), [T2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B) and [TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B). No specific variant is asserted for these clips.
- [License text](licenses/Wan2.2-Apache-2.0.txt) retained verbatim from official source revision `1ea34ff48f87168174e12956e200b1d908b1c5ff`. SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- Exact checkpoint variant/hash and workflow were not retained. The record relies on the owner's explicit Wan2.2 identification, not a claimed forensic match. No additional model, fine-tune or LoRA is invented.
- ComfyUI's GPLv3 software license is separate from Wan2.2 licensing. Neither ComfyUI software nor model weights are distributed with SHAKTI. This record concerns generated footage publication, not model-weight redistribution.
- Input artwork and WebGL scenes are owner-confirmed project materials. Source embedded audio is excluded; an independently synthesized score is used. Generated output is not asserted to have exclusive copyright or blanket MIT licensing.

## Release decision

The owner's model identification, official Wan2.2 license/output statement, retained notices and existing input/asset provenance support publication of this release. The earlier unidentified-model gate is resolved on that stated basis. This does not certify unknown models or make a general guarantee about all AI output. No additional model restriction is evidenced in the available record.

Flight Trishul remains CC BY 4.0 with its supplied notices/modifications. Fonts remain SIL OFL 1.1. Dependency notices, including GSAP's separate terms, are retained. SHAKTI creator credit remains **Rupjyoti Talukdar (MadB0i)**. No endorsement by Team Wan, ComfyUI, Clipchamp or the asset creator is implied.

[Per-clip source hashes and provenance](video-generation-provenance.json) · [Full credits](CREDITS.md).
