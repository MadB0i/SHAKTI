# SHAKTI ornate Trishul hero

`trishul-hero.glb` is an original project asset modeled locally from the source in `scripts/build-trishul.mjs`. It is not a downloaded or commissioned model. No external images, models, fonts, textures or other third-party artwork are embedded. There are no image planes.

The model contains convex tapered tines, raised leaf relief, inset channels, a fluted/turned staff, beaded collars, a layered lotus boss and a ruby cabochon. Four PBR materials distinguish burnished gold, polished edges, aged recesses and ruby. The asset contains 131,832 triangles and is approximately 2.47 MB. Indices are welded, vertex normals are normalized, and geometry is batched by material.

Rebuild from the project root:

```powershell
node scripts/build-trishul.mjs
```

The geometry is independent of the website and can be inspected or refined in a glTF-compatible 3D editor. It requires no additional modeling runtime or dependency installation to rebuild with the project's existing Node/Three.js dependencies.

Runtime treatment is in `src/cinema/Experience.ts`: reflection-only light cards, fine roughness variation, an assembly edge and a reveal mask. Particles sample the imported model's triangle surfaces. The model is preloaded and shaders are warmed before ignition becomes available. Failed loads produce a visible retry message rather than substituting a flat image.
