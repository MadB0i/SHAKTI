/** Bounded art-direction studies, derived from build-trishul.mjs.
 * Writes ONLY evidence/trishul-art-direction. Never rebuilds the active hero.
 * Reuses the original loft/lathe/relief/merged-GLB construction approach.
 */
import * as T from 'three'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import { mergeGeometries, mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { deflateSync } from 'node:zlib'

globalThis.FileReader=class {
 readAsArrayBuffer(blob){blob.arrayBuffer().then(result=>{this.result=result;this.onloadend?.()})}
 readAsDataURL(blob){blob.arrayBuffer().then(result=>{this.result=`data:application/octet-stream;base64,${Buffer.from(result).toString('base64')}`;this.onloadend?.()})}
}
const out='evidence/trishul-art-direction';await mkdir(out,{recursive:true})
const protectedFiles=['public/art/trishul/trishul-hero.glb','scripts/build-trishul.mjs','src/cinema/Experience.ts','src/cinema/geometry.ts','src/cinema/shaders.ts','src/App.tsx','src/style.css','package.json','package-lock.json','public/art/durga-reveal.png']
const hashes={};for(const f of protectedFiles)hashes[f]=createHash('sha256').update(await readFile(f)).digest('hex')
await writeFile(`${out}/preservation-before.json`,JSON.stringify(hashes,null,2))
const v=(x,y,z=0)=>new T.Vector3(x,y,z)
const curve=p=>new T.CatmullRomCurve3(p.map(a=>v(...a)))
const styles=[
 {id:'a-padma',name:'A · Padma / sweeping lotus crown',tone:0xb99148,rough:.38,
  side:[[.14,7.05],[1.65,7.35],[3.25,8.05],[3.85,9.5],[3.65,10.95],[2.8,12.05]],
  width:t=>.002+(.35+.22*Math.sin(t*Math.PI))*Math.pow(Math.sin(Math.PI*(.12+.88*t)),.8),
  middle:[[0,7.4],[0,8.8],[0,10.65],[0,12.55]],mw:.7,md:.34,motif:'lotus',gem:.18},
 {id:'b-vajra',name:'B · Vajra / ceremonial spear',tone:0xc39b50,rough:.34,
  side:[[.1,7.05],[1.9,7.35],[3.05,8.3],[3.48,9.9],[3.1,11.95]],
  width:t=>.002+(.45+.23*Math.exp(-(((t-.38)/.18)**2)))*Math.pow(Math.sin(Math.PI*(.1+.9*t)),.75),
  middle:[[0,7.4],[0,8.8],[0,10.25],[0,12.55]],mw:.94,md:.4,motif:'spear',gem:.13},
 {id:'c-agni',name:'C · Agni / flowing flame',tone:0xb68c43,rough:.4,
  side:[[.1,7.05],[1.7,7.55],[2.7,8.95],[2.6,10.5],[3.45,12.0]],
  width:t=>.002+(.41+.19*Math.sin(t*Math.PI*1.25))*Math.pow(Math.sin(Math.PI*(.1+.9*t)),.9),
  middle:[[0,7.4],[-.14,9.0],[.16,10.65],[0,12.55]],mw:.7,md:.36,motif:'flame',gem:.11},
]

// Small, embedded spatial roughness atlas, with broad burnishing and fine grain.
// No bump/normal map: all silhouette, ridges and channels below are real geometry.
function crc32(buf){let c=0xffffffff;for(const b of buf){c^=b;for(let k=0;k<8;k++)c=(c>>>1)^((c&1)?0xedb88320:0)}return (c^0xffffffff)>>>0}
function pngChunk(name,data){const type=Buffer.from(name),body=Buffer.concat([type,data]),size=Buffer.alloc(4),crc=Buffer.alloc(4);size.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(body));return Buffer.concat([size,body,crc])}
function roughnessPNG(){
 const n=256,rows=Buffer.alloc(n*(1+n*3));let seed=319
 for(let y=0;y<n;y++)for(let x=0;x<n;x++){
  seed=(Math.imul(seed,1664525)+1013904223)>>>0
  const broad=.5+.22*Math.sin(x*.031+y*.017)+.19*Math.cos(y*.057-x*.023)
  const value=Math.round(255*(.63+.28*broad+.07*(seed/4294967296)))
  const i=y*(n*3+1)+1+x*3;rows[i]=255;rows[i+1]=value;rows[i+2]=255
 }
 const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(n,0);ihdr.writeUInt32BE(n,4);ihdr[8]=8;ihdr[9]=2
 return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),pngChunk('IHDR',ihdr),pngChunk('IDAT',deflateSync(rows)),pngChunk('IEND',Buffer.alloc(0))])
}
const roughPNG=roughnessPNG()
await writeFile(`${out}/roughness-atlas.png`,roughPNG)
function embedRoughness(data){
 const buf=Buffer.from(data),jsonLength=buf.readUInt32LE(12),doc=JSON.parse(buf.subarray(20,20+jsonLength).toString()),binStart=28+jsonLength,bin=buf.subarray(binStart)
 const imageStart=(bin.length+3)&~3,content=Buffer.concat([bin,Buffer.alloc(imageStart-bin.length),roughPNG])
 doc.bufferViews.push({buffer:0,byteOffset:imageStart,byteLength:roughPNG.length})
 doc.images=[{bufferView:doc.bufferViews.length-1,mimeType:'image/png',name:'Spatial burnishing roughness; original SHAKTI study'}]
 doc.samplers=[{magFilter:9729,minFilter:9987,wrapS:33071,wrapT:33071}];doc.textures=[{sampler:0,source:0}]
 for(const m of doc.materials)if(!m.name.includes('Crimson'))m.pbrMetallicRoughness.metallicRoughnessTexture={index:0}
 // Metallic-roughness textures use B for metalness. Keep metalness exactly 1;
 // the PNG uses the spatial variation in G only.
 doc.buffers[0].byteLength=content.length
 let json=Buffer.from(JSON.stringify(doc));json=Buffer.concat([json,Buffer.alloc((-json.length)&3,32)])
 const padded=Buffer.concat([content,Buffer.alloc((-content.length)&3)])
 const header=Buffer.alloc(12);header.writeUInt32LE(0x46546c67);header.writeUInt32LE(2,4);header.writeUInt32LE(28+json.length+padded.length,8)
 const jhead=Buffer.alloc(8),bhead=Buffer.alloc(8);jhead.writeUInt32LE(json.length);jhead.writeUInt32LE(0x4e4f534a,4);bhead.writeUInt32LE(padded.length);bhead.writeUInt32LE(0x004e4942,4)
 return Buffer.concat([header,jhead,json,bhead,padded])
}

const manifests=[]
for(const style of styles){
 const mats=[
  new T.MeshStandardMaterial({name:'Antique gold body',color:style.tone,metalness:1,roughness:style.rough,vertexColors:true}),
  new T.MeshStandardMaterial({name:'Burnished edge gold',color:0xe7c27a,metalness:1,roughness:.25,vertexColors:true}),
  new T.MeshStandardMaterial({name:'Dark recessed engraving',color:0x4c3519,metalness:1,roughness:.64,vertexColors:true}),
  new T.MeshPhysicalMaterial({name:'Crimson garnet',color:0x500713,metalness:.06,roughness:.19,clearcoat:1,clearcoatRoughness:.11,ior:1.76,vertexColors:true}),
 ]
 const buckets=mats.map(()=>[])
 const add=(g,m=0)=>{buckets[m].push(g);return g}
 function tube(points,r=.02,m=1,n=48){return add(new T.TubeGeometry(new T.CatmullRomCurve3(points),n,r,8,false),m)}
 function turned(profile,m=0){return add(new T.LatheGeometry(profile.map(p=>new T.Vector2(...p)),48),m)}
 function bead(r,x,y,z,m=1){const g=new T.SphereGeometry(r,20,12);g.translate(x,y,z);return add(g,m)}
 function ring(r,t,y,m=1){const g=new T.TorusGeometry(r,t,8,48);g.rotateX(Math.PI/2);g.translate(0,y,0);return add(g,m)}
 // Original swept loft, with a deeper folded section and actual recessed flutes.
 function surface(u){const a=Math.abs(u);return Math.sqrt(Math.max(0,1-u*u))*(.78+.22*Math.exp(-u*u*24))-.13*Math.exp(-(((a-.64)/.065)**2))}
 function at(path,width,depth,t,u,face=1){const p=path.getPoint(t),tan=path.getTangent(t),cross=v(tan.y,-tan.x).normalize();return p.addScaledVector(cross,u*width(t)).add(v(0,0,face*depth(t)*surface(u)))}
 function loft(path,width,depth,m=0,n=112,k=48){
  const vertices=[],indices=[]
  for(let i=0;i<=n;i++)for(let j=0;j<=k;j++){
   const a=j/k*Math.PI*2,p=at(path,width,depth,i/n,Math.cos(a),Math.sin(a)>=0?1:-1);vertices.push(p.x,p.y,p.z)
  }
  for(let i=0;i<n;i++)for(let j=0;j<k;j++){const a=i*(k+1)+j,b=a+k+1;indices.push(a,b,a+1,b,b+1,a+1)}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(vertices,3));g.setIndex(indices);g.computeVertexNormals();return add(g,m)
 }
 function decoration(path,w,d,central=false){
  // Flowing recessed channels, with sparse relief rather than repeated scales.
  for(const face of [-1,1]){
   for(const u of [-.64,.64]){
    const pts=[];for(let i=0;i<=90;i++){const t=.055+i/90*.88;pts.push(at(path,w,d,t,u,face))}
    tube(pts,.016,2,90)
   }
   for(const u of [-.9,.9]){
    const pts=[];for(let i=0;i<=90;i++){const t=.035+i/90*.93;pts.push(at(path,w,d,t,u,face))}
    tube(pts,.018,1,90)
   }
   const ridge=[];for(let i=0;i<=90;i++){const t=.035+i/90*.93;ridge.push(at(path,w,d,t,style.motif==='flame'?.14*Math.sin(t*7):0,face).add(v(0,0,face*.008)))}
   tube(ridge,central?.023:.018,1,90)
   const layouts=style.motif==='lotus'?[[.13,.32,-1],[.29,.52,1],[.49,.7,-1]]:style.motif==='spear'?[[.12,.35,-1],[.12,.35,1],[.4,.62,-1],[.4,.62,1]]:[[.15,.45,1],[.38,.68,-1]]
   for(const [start,end,side] of layouts){
    const pts=[];for(let i=0;i<=40;i++){const a=i/40,t=start+(end-start)*a,u=side*.5*Math.sin(Math.PI*a);pts.push(at(path,w,d,t,u,face).add(v(0,0,face*.017)))}
    tube(pts,.025,0,40)
    const inner=[];for(let i=0;i<=30;i++){const a=i/30,t=start+(end-start)*a,u=side*.38*Math.sin(Math.PI*a);inner.push(at(path,w,d,t,u,face).add(v(0,0,face*.01)))}
    tube(inner,.012,2,36)
   }
  }
 }
 const mid=curve(style.middle),mw=t=>.002+style.mw*Math.pow(Math.sin(t*Math.PI),style.motif==='spear'?.9:1.2)*(1-.14*t),md=t=>.005+style.md*Math.pow(Math.sin(t*Math.PI),.7)
 loft(mid,mw,md);decoration(mid,mw,md,true)
 for(const s of [-1,1]){
  const path=curve(style.side.map(([x,y])=>[s*x,y])),w=style.width,d=t=>.006+.33*Math.pow(Math.sin(Math.PI*(.08+t*.92)),.9)
  loft(path,w,d);decoration(path,w,d)
 }
 // Staff/turning vocabulary retained from the original, with fewer purposeful joints.
 turned([[0,0],[.13,0],[.23,.17],[.24,.36],[.16,.62],[.145,1.0],[.145,5.95],[.21,6.25],[.24,6.55],[.19,7.25],[0,7.25]],2)
 for(let i=0;i<8;i++){
  const pts=[];for(let j=0;j<=72;j++){const y=.65+j/72*5.7,angle=i/8*Math.PI*2+(style.motif==='flame'?y*.22:0),r=.159;pts.push(v(Math.cos(angle)*r,y,Math.sin(angle)*r))}
  tube(pts,.018,0,72)
 }
 for(const y of [.58,1.28,4.8,6.25]){
  turned([[.15,y-.15],[.205,y-.1],[.215,y],[.205,y+.1],[.15,y+.15]],0)
  ring(.21,.025,y-.085);ring(.21,.025,y+.085)
 }
 // Real lotus cup: curved petals rotate around the shaft, creating a deep collar.
 for(let j=0;j<8;j++){
  const p=curve([[0,6.38,.18],[0,6.75,.42],[0,7.2,.64],[0,7.43,.5]])
  const petal=loft(p,t=>.005+.19*Math.pow(Math.sin(t*Math.PI),.9),t=>.004+.065*Math.sin(t*Math.PI),j%2?0:1,36,16);petal.rotateY(j/8*Math.PI*2)
 }
 ring(.26,.045,6.48);ring(.23,.025,6.33,2)
 // A five-petal front crest replaces the repeated starburst of the baseline.
 const cy=7.2
 for(let j=0;j<5;j++){
  const angle=(j-2)*.53,ax=Math.sin(angle),ay=Math.cos(angle),len=style.motif==='spear'?.62:.78
  const p=curve([[ax*.08,cy+ay*.08,.26],[ax*.43,cy+ay*.43,.52],[ax*len,cy+ay*len,.32]])
  loft(p,t=>.004+.15*Math.sin(t*Math.PI),t=>.004+.07*Math.sin(t*Math.PI),j%2?0:1,28,16)
 }
 const bezel=new T.TorusGeometry(style.gem+.045,.03,8,48);bezel.scale(1,1.25,1);bezel.translate(0,7.29,.63);add(bezel,1)
 const ruby=new T.SphereGeometry(style.gem,24,16);ruby.scale(1,1.25,.5);ruby.translate(0,7.29,.64);add(ruby,3)
 // Closed bud finial and restrained shoulder leaf, without strings of beads.
 turned([[0,.02],[.18,.08],[.24,.25],[.18,.43],[.12,.51]],0)
 for(let j=0;j<6;j++){
  const a=j/6*Math.PI*2,pts=[];for(let i=0;i<=24;i++){const t=i/24,r=.13+.11*Math.sin(t*Math.PI);pts.push(v(Math.sin(a)*r,.08+t*.38,Math.cos(a)*r))}tube(pts,.014,1,24)
 }
 const root=new T.Group();root.name=style.name;root.userData={author:'SHAKTI project / Codex',source:'scripts/propose-trishul.mjs; derived from scripts/build-trishul.mjs',license:'Original project study; no external assets',status:'Art direction proposal only; not approved or integrated'}
 let triangles=0
 for(let i=0;i<buckets.length;i++){
  const geometries=buckets[i].map(g=>{const a=g.index?g.toNonIndexed():g.clone();a.deleteAttribute('uv');return a})
  const merged=mergeGeometries(geometries),geometry=mergeVertices(merged,1e-5);merged.dispose();triangles+=geometry.index.count/3
  const p=geometry.attributes.position,normal=geometry.attributes.normal,uv=[],colors=[],temp=v(0,0)
  for(let j=0;j<p.count;j++){
   temp.fromBufferAttribute(normal,j);if(temp.lengthSq()<1e-12)temp.set(0,1,0);normal.setXYZ(j,...temp.normalize().toArray())
   const x=p.getX(j),y=p.getY(j),z=p.getZ(j);uv.push((x+5)/10,y/12.6)
   const burn=.91+.045*Math.sin(x*2.6+y*1.2+z*3)+.03*Math.cos(y*4.7-x*.8);colors.push(burn,burn*.994,burn*.978)
  }
  geometry.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geometry.setAttribute('color',new T.Float32BufferAttribute(colors,3))
  const mesh=new T.Mesh(geometry,mats[i]);mesh.name=mats[i].name;root.add(mesh)
  geometries.forEach(g=>g.dispose());buckets[i].forEach(g=>g.dispose())
 }
 root.updateMatrixWorld(true);const bounds=new T.Box3().setFromObject(root)
 const exported=await new GLTFExporter().parseAsync(root,{binary:true,onlyVisible:true}),glb=embedRoughness(exported)
 await writeFile(`${out}/${style.id}.glb`,glb)
 manifests.push({id:style.id,name:style.name,triangles,materials:4,bytes:glb.length,bounds:[bounds.min.toArray(),bounds.max.toArray()],roughness:{body:style.rough,edge:.25,recess:.64,atlas:'256x256, embedded, spatial burnishing'}})
 console.log(JSON.stringify(manifests.at(-1)))
 root.traverse(o=>{if(o instanceof T.Mesh)o.geometry.dispose()});mats.forEach(m=>m.dispose())
}
await writeFile(`${out}/proposals.json`,JSON.stringify(manifests,null,2))
