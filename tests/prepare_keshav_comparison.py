"""Inspect the supplied archive and normalize a COPY for matched runtime A/B.

No active asset is written. PNGs, UVs, topology and material factors are preserved.
"""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/asset-comparison'
SOURCE = OUT / 'candidate-source'
g = json.loads((SOURCE / 'scene.gltf').read_text())
binary = bytearray((SOURCE / 'scene.bin').read_bytes())

def accessor(i):
    a = g['accessors'][i]
    v = g['bufferViews'][a['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    dtype = {5126: '<f4', 5125: '<u4'}[a['componentType']]
    item = np.dtype(dtype).itemsize
    return np.ndarray((a['count'], width), dtype=dtype, buffer=binary,
                      offset=v.get('byteOffset', 0) + a.get('byteOffset', 0),
                      strides=(v.get('byteStride', width * item), item))

primitive = g['meshes'][0]['primitives'][0]
pos = accessor(primitive['attributes']['POSITION'])
normal = accessor(primitive['attributes']['NORMAL'])
tangent = accessor(primitive['attributes']['TANGENT'])
uv = accessor(primitive['attributes']['TEXCOORD_0'])
indices = accessor(primitive['indices']).reshape(-1, 3)
world = np.eye(4)
# This archive has a single nested chain, one mesh and no animation/skinning.
assert len(g['meshes']) == 1 and len(g['meshes'][0]['primitives']) == 1
for node in g['nodes']:
    assert not any(k in node for k in ['translation', 'rotation', 'scale'])
    world = world @ np.array(node.get('matrix', np.eye(4).flatten(order='F'))).reshape(4, 4, order='F')
original_pos = pos.copy()
world_pos = original_pos @ world[:3, :3].T + world[:3, 3]
lo, hi = world_pos.min(0), world_pos.max(0)
# Match the complete current hero's Y bounds, preserving candidate proportions.
target_lo, target_hi = -0.18400000035762787, 12.555645942687988
scale = (target_hi - target_lo) / (hi[1] - lo[1])
center = (lo + hi) / 2
normalized = (world_pos - [center[0], lo[1], center[2]]) * scale + [0, target_lo, 0]
pos[:] = normalized
rotation = world[:3, :3]
normal[:] = normal.copy() @ np.linalg.inv(rotation)
normal[:] /= np.linalg.norm(normal, axis=1)[:, None]
tangent[:, :3] = tangent[:, :3].copy() @ rotation.T
tangent[:, :3] /= np.linalg.norm(tangent[:, :3], axis=1)[:, None]
assert np.linalg.det(rotation) > 0  # No mirrored winding or tangent sign correction.
for key in ['POSITION', 'NORMAL', 'TANGENT']:
    a = g['accessors'][primitive['attributes'][key]]
    a['min'], a['max'] = accessor(primitive['attributes'][key]).min(0).tolist(), accessor(primitive['attributes'][key]).max(0).tolist()

cross = np.cross(pos[indices[:, 1]] - pos[indices[:, 0]], pos[indices[:, 2]] - pos[indices[:, 0]])
# Retain independent audit arrays before growing the bytearray for embedded PNGs.
pos, normal, uv, indices = pos.copy(), normal.copy(), uv.copy(), indices.copy()
texture_info = []
for image in g['images']:
    path = SOURCE / image.pop('uri')
    texture_info.append({'file': path.name, 'dimensions': list(Image.open(path).size), 'bytes': path.stat().st_size})
    binary.extend(b'\0' * (-len(binary) % 4))
    data = path.read_bytes()
    image.update(bufferView=len(g['bufferViews']), mimeType='image/png')
    g['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(data)})
    binary.extend(data)
g['nodes'] = [{'mesh': 0, 'name': 'keshavckm1 — comparison copy; baked scale and pivot'}]
g['scenes'] = [{'nodes': [0]}]
g['asset']['extras']['comparisonChanges'] = 'Nested transforms baked into geometry/normals/tangents. Complete height matched to SHAKTI hero. Bottom pivot and X/Z center aligned. Original textures, UVs, topology and materials preserved. Not integrated.'
g['buffers'] = [{'byteLength': len(binary)}]
binary.extend(b'\0' * (-len(binary) % 4))
doc = json.dumps(g, separators=(',', ':'), ensure_ascii=True).encode()
doc += b' ' * (-len(doc) % 4)
glb = struct.pack('<III', 0x46546C67, 2, 28 + len(doc) + len(binary)) + struct.pack('<II', len(doc), 0x4E4F534A) + doc + struct.pack('<II', len(binary), 0x004E4942) + binary
(OUT / 'candidate-normalized.glb').write_bytes(glb)
files = ['public/art/trishul/trishul-hero.glb', 'scripts/build-trishul.mjs', 'public/art/durga-reveal.png', 'src/cinema/Experience.ts', 'src/cinema/geometry.ts', 'src/cinema/shaders.ts', 'src/App.tsx', 'src/style.css', 'package.json', 'package-lock.json']
hashes = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}
(OUT / 'preservation-before.json').write_text(json.dumps(hashes, indent=2))
report = {'archive': 'incoming-assets/trishul-keshav.zip', 'archive_sha256': hashlib.sha256((ROOT/'incoming-assets/trishul-keshav.zip').read_bytes()).hexdigest(),
          'creator': g['asset']['extras']['author'], 'source': g['asset']['extras']['source'], 'license': g['asset']['extras']['license'],
          'triangles': len(indices), 'vertices': len(pos), 'mesh_primitives': 1, 'materials': g['materials'],
          'textures': texture_info, 'uv_min': uv.min(0).tolist(), 'uv_max': uv.max(0).tolist(),
          'has_normals': True, 'has_tangents': True, 'nonfinite_positions': int((~np.isfinite(pos)).sum()),
          'nonfinite_normals': int((~np.isfinite(normal)).sum()), 'near_zero_area_triangles': int((np.linalg.norm(cross, axis=1) < 1e-10).sum()),
          'normalized_bounds': [pos.min(0).tolist(), pos.max(0).tolist()], 'normalized_glb_bytes': len(glb),
          'normalization': g['asset']['extras']['comparisonChanges'], 'original_world_matrix': world.tolist(),
          'texture_gpu_memory_note': 'Two 4096x4096 uncompressed RGBA maps with mipmaps: approximately 170.7 MiB, excluding geometry/render targets. Estimate, not a measured VRAM allocation.',
          'provenance_note': 'Node/material names contain tripo; authoring workflow is not established by those names alone.'}
(OUT / 'inspection.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
