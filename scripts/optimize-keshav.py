"""Prepare the already-downloaded CC BY asset, without changing its design."""
from pathlib import Path
from io import BytesIO
import copy, json, struct, shutil
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'evidence/asset-comparison/candidate-normalized.glb'
dest=ROOT/'public/art/trishul/keshav';dest.mkdir(parents=True,exist_ok=True)
b=source.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);old=b[28+n:]
out=bytearray();views=[];accessors=[];attributes={};images=[];report={}
def append(data,extra=None):
    out.extend(b'\0'*(-len(out)%4));view={'buffer':0,'byteOffset':len(out),'byteLength':len(data)}
    if extra:view.update(extra)
    views.append(view);out.extend(data);return len(views)-1
primitive=g['meshes'][0]['primitives'][0]
for key,i in list(primitive['attributes'].items())+[('indices',primitive['indices'])]:
    if key=='TEXCOORD_1':continue # Duplicate UV set, unused by all supplied textures.
    a=copy.deepcopy(g['accessors'][i]);v=g['bufferViews'][a['bufferView']]
    size={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dtype={5126:'<f4',5125:'<u4'}[a['componentType']]
    data=np.ndarray((a['count'],size),dtype=dtype,buffer=old,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*4),4)).copy()
    if key=='indices':
        assert data.max()<65536;data=data.astype('<u2');a['componentType']=5123
    a['bufferView']=append(data.tobytes(),{'target':34963 if key=='indices' else 34962});a.pop('byteOffset',None)
    attributes[key]=len(accessors);accessors.append(a)
for i,im in enumerate(g['images']):
    view=g['bufferViews'][im['bufferView']];data=old[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
    original=Image.open(BytesIO(data)).convert('RGB');image=original.resize((2048,2048),Image.Resampling.LANCZOS)
    encoded=BytesIO()
    if i==0:
        image.save(encoded,format='WEBP',quality=95,method=6);mime='image/webp'
    else:
        # Renormalize downsampled tangent-space normals to avoid softened vectors.
        normal=np.asarray(image,dtype=np.float32)/127.5-1
        normal/=np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-6)
        image=Image.fromarray(np.clip((normal+1)*127.5,0,255).round().astype('uint8'))
        image.save(encoded,format='PNG',optimize=True);mime='image/png'
    payload=encoded.getvalue();images.append({'bufferView':append(payload),'mimeType':mime})
    report['base_color' if i==0 else 'normal']={'source_size':list(original.size),'optimized_size':list(image.size),'bytes':len(payload),'format':mime}
g['accessors']=accessors;g['bufferViews']=views;g['images']=images
primitive['attributes']={k:v for k,v in attributes.items() if k!='indices'};primitive['indices']=attributes['indices']
# EXT_texture_webp is required by glTF for WebP, even where browsers decode it natively.
g['textures'][0]={'sampler':0,'extensions':{'EXT_texture_webp':{'source':0}}}
g.setdefault('extensionsUsed',[]).append('EXT_texture_webp');g['extensionsRequired']=['EXT_texture_webp']
g['asset']['extras']['modifications']='SHAKTI Phase 2A: normalized transform/height/pivot (comparison source); removed unused duplicate UV1; losslessly converted indices to uint16; base color resized to 2048 WebP quality 95; normal resized to 2048 PNG and vectors renormalized. Geometry, UV0 and material factors unchanged.'
g['buffers']=[{'byteLength':len(out)}];out.extend(b'\0'*(-len(out)%4))
doc=json.dumps(g,separators=(',',':')).encode();doc+=b' '*(-len(doc)%4)
glb=struct.pack('<III',0x46546c67,2,28+len(doc)+len(out))+struct.pack('<II',len(doc),0x4e4f534a)+doc+struct.pack('<II',len(out),0x004e4942)+out
(dest/'trishul-flight.glb').write_bytes(glb)
shutil.copy2(ROOT/'evidence/asset-comparison/candidate-source/license.txt',dest/'license.txt')
(dest/'ATTRIBUTION.md').write_text('''# Flight Trishul attribution

This work is based on "trishul" (https://sketchfab.com/3d-models/trishul-7d154946cba44ac7ae858bc205727581) by keshavckm1 (https://sketchfab.com/keshavckm1), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

Original supplied notice: license.txt. The original archive remains in incoming-assets/trishul-keshav.zip; full-resolution extracted source and comparison GLB remain in evidence/asset-comparison/.

Changes: nested transforms baked; complete height/pivot aligned to the SHAKTI baseline; unused duplicate UV1 removed; indices losslessly repacked to uint16; base color resized from 4096 to 2048 and encoded as WebP quality 95; normal resized to 2048, renormalized and stored as PNG. Positions/topology/UV0 and original material factors preserved. Conversion source: scripts/optimize-keshav.py.

Retain creator, source, license link, supplied notices and this modification notice when redistributing the asset. Credit keshavckm1 and link CC BY 4.0 in promotional video descriptions/credits as well as the website and repository. No creator endorsement is implied. The asset remains CC BY 4.0 independently of project code licensing.
''',encoding='utf-8')
report.update(original_glb_bytes=len(b),optimized_glb_bytes=len(glb),reduction_percent=(1-len(glb)/len(b))*100,triangles=95632,modifications=g['asset']['extras']['modifications'])
(ROOT/'evidence/phase2a/optimization.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
