/** Original SHAKTI hero model. Rebuild: node scripts/build-trishul.mjs
 * All surfaces, chased relief, inlays and turning profiles are modeled here.
 * No downloaded assets, image planes, or textures are embedded in the GLB.
 */
import * as T from 'three'
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js'
import { mergeGeometries, mergeVertices } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { mkdir, writeFile } from 'node:fs/promises'

globalThis.FileReader=class {
 readAsArrayBuffer(blob){blob.arrayBuffer().then(result=>{this.result=result;this.onloadend?.()})}
 readAsDataURL(blob){blob.arrayBuffer().then(result=>{this.result=`data:application/octet-stream;base64,${Buffer.from(result).toString('base64')}`;this.onloadend?.()})}
}
const materials=[
 new T.MeshStandardMaterial({name:'Burnished gold',color:0xd4a64e,metalness:1,roughness:.26}),
 new T.MeshStandardMaterial({name:'Polished raised edges',color:0xf4d38a,metalness:1,roughness:.19}),
 new T.MeshStandardMaterial({name:'Antique recessed gold',color:0x795126,metalness:.96,roughness:.38}),
 new T.MeshPhysicalMaterial({name:'Deep ruby cabochons',color:0x700b14,emissive:0x80091a,emissiveIntensity:.08,metalness:.14,roughness:.14,clearcoat:1,clearcoatRoughness:.08,ior:1.76}),
]
const buckets=materials.map(()=>[])
function add(g,mat=0){buckets[mat].push(g);return g}
function tube(points,r=.025,mat=1,segments=64){const path=new T.CatmullRomCurve3(points);return add(new T.TubeGeometry(path,segments,r,6,false),mat)}
const v=(x,y,z=0)=>new T.Vector3(x,y,z)
function ring(r,t,x,y,z,mat=1){const g=new T.TorusGeometry(r,t,8,48);g.translate(x,y,z);return add(g,mat)}
function bead(r,x,y,z,mat=1){const g=new T.SphereGeometry(r,12,8);g.translate(x,y,z);return add(g,mat)}
function turned(profile,mat=0){return add(new T.LatheGeometry(profile.map(p=>new T.Vector2(...p)),64),mat)}
function loft(curve,width,depth,mat=0,n=90,k=12){
 const vertices=[],indices=[],temp=new T.Vector3()
 for(let i=0;i<=n;i++){
  const t=i/n,p=curve.getPoint(t),tangent=curve.getTangent(t),cross=temp.set(tangent.y,-tangent.x,0).normalize().clone()
  for(let j=0;j<=k;j++){
   const a=j/k*Math.PI*2,c=Math.cos(a),s=Math.sin(a)
   const q=p.clone().addScaledVector(cross,c*width(t));q.z+=Math.sign(s)*Math.pow(Math.abs(s),.72)*depth(t)
   vertices.push(q.x,q.y,q.z)
  }
 }
 for(let i=0;i<n;i++)for(let j=0;j<k;j++){const a=i*(k+1)+j,b=a+k+1;indices.push(a,b,a+1,b,b+1,a+1)}
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(vertices,3));g.setIndex(indices);g.computeVertexNormals();return add(g,mat)
}

// Tapered, convex blades: the silhouette is carved in three dimensions.
const middle=new T.CatmullRomCurve3([v(0,7.45),v(0,9.25),v(0,10.7),v(0,12.55)])
loft(middle,t=>.015+.60*Math.pow(Math.sin(Math.PI*t),1.35)*(1-.2*t),t=>.015+.22*Math.pow(Math.sin(Math.PI*t),.7))
for(const s of [-1,1]){
 const path=new T.CatmullRomCurve3([v(s*.2,6.95),v(s*1.8,7.25),v(s*3.1,8.1),v(s*3.65,9.6),v(s*3.55,11.75)])
 const width=t=>.012+.40*Math.pow(Math.sin(Math.PI*(.13+t*.87)),1.2)
 const depth=t=>.012+.24*Math.pow(Math.sin(Math.PI*(.08+t*.92)),1.2)
 loft(path,width,depth)
 // Parallel raised borders with dark channels between them.
 for(const side of [-1,1])for(const inset of [.66,.84]){
  const points=[]
  for(let i=0;i<=96;i++){const t=i/96,p=path.getPoint(t),tan=path.getTangent(t);p.addScaledVector(v(tan.y,-tan.x).normalize(),side*width(t)*inset);p.z=depth(t)*.8;points.push(p)}
  tube(points,inset===.84?.022:.012,inset===.84?1:2,96)
 }
 // Chased herringbone leaves follow the tine; relief has actual thickness.
 for(let i=0;i<27;i++){
  const t=.05+i*.031,p=path.getPoint(t),tan=path.getTangent(t).normalize(),normal=v(tan.y,-tan.x)
  for(const side of [-1,1]){
   const w=width(t)*.62,leaf=[]
   for(let j=0;j<=20;j++){const a=j/20,point=p.clone().addScaledVector(normal,side*w*Math.sin(a*Math.PI)).addScaledVector(tan,(a-.5)*.25);point.z=depth(t)*.93+Math.sin(a*Math.PI)*.035;leaf.push(point)}
   tube(leaf,.014,1,24)
  }
 }
}
// Central spear: folded median ridge, inset channels and a symmetrical vine.
for(const s of [-1,1]){
 const border=[],spine=[]
 for(let i=0;i<=90;i++){const t=i/90,y=7.45+t*5.1,w=.015+.60*Math.pow(Math.sin(Math.PI*t),1.35)*(1-.2*t),d=.015+.22*Math.pow(Math.sin(Math.PI*t),.7);border.push(v(s*w*.8,y,d*.8));spine.push(v(s*.045*Math.sin(t*Math.PI),y,d+.015))}
 tube(border,.02,1,96);tube(spine,.018,2,96)
 for(let i=0;i<16;i++){
  const t=.14+i*.042,y=7.45+t*5.1,w=.60*Math.pow(Math.sin(Math.PI*t),1.35)*(1-.2*t),d=.015+.22*Math.pow(Math.sin(Math.PI*t),.7)
  tube([v(s*.035,y-.11,d+.02),v(s*w*.40,y-.04,d+.045),v(s*w*.67,y+.10,d*.85)],.015,1,24)
 }
}

// Turned staff; dark recesses make the gold ribs legible under moving light.
turned([[0,0],[.16,0],[.20,.14],[.22,.32],[.17,.5],[.13,.7],[.13,6.5],[.22,6.65],[.27,6.95],[.21,7.3],[0,7.3]],2)
for(let side=0;side<12;side++){
 const angle=side/12*Math.PI*2,points=[]
 for(let i=0;i<=48;i++){const y=.65+i/48*5.8,r=.145+.006*Math.sin(y*22);points.push(v(Math.cos(angle)*r,y,Math.sin(angle)*r))}
 tube(points,.021,0,64)
}
for(const y of [.45,.62,1.5,1.62,3.1,3.22,4.8,4.92,6.25,6.4,6.65]){
 const g=new T.TorusGeometry(y>6?.23:.19,.045,8,48);g.rotateX(Math.PI/2);g.translate(0,y,0);add(g,1)
 for(let j=0;j<16;j++){const a=j/16*Math.PI*2;bead(.025,Math.cos(a)*.225,y,Math.sin(a)*.225,0)}
}
for(const y of [1.9,3.55,5.2]){
 turned([[.14,y-.2],[.2,y-.17],[.2,y+.17],[.14,y+.2]],0)
 for(let i=0;i<20;i++){const a=i/20*Math.PI*2,g=new T.OctahedronGeometry(.048,0);g.scale(1,2,1);g.translate(Math.cos(a)*.21,y,Math.sin(a)*.21);add(g,1)}
}

// Lotus boss: layered petal relief, a ruby and granular gold setting.
for(const [n,radius,length,z] of [[12,.38,.55,.29],[8,.23,.37,.42]]){
 for(let i=0;i<n;i++){
  const a=i/n*Math.PI*2,axis=v(Math.sin(a),Math.cos(a)),curve=new T.CatmullRomCurve3([v(axis.x*.1,7.05+axis.y*.1,z),v(axis.x*radius,7.05+axis.y*radius,z+.10),v(axis.x*(radius+length),7.05+axis.y*(radius+length),z)])
  loft(curve,t=>.006+.13*Math.pow(Math.sin(t*Math.PI),1.1),t=>.008+.065*Math.sin(t*Math.PI),i%2?0:1,24,8)
  tube([v(axis.x*.15,7.05+axis.y*.15,z+.07),v(axis.x*radius,7.05+axis.y*radius,z+.17),v(axis.x*(radius+length)*.9,7.05+axis.y*(radius+length)*.9,z+.03)],.012,2,24)
 }
}
ring(.31,.055,0,7.05,.62,1);ring(.39,.02,0,7.05,.53,2)
const ruby=new T.SphereGeometry(.255,32,20);ruby.scale(1,1.13,.48);ruby.translate(0,7.05,.67);add(ruby,3)
for(let i=0;i<20;i++){const a=i/20*Math.PI*2;bead(.032,Math.cos(a)*.34,7.05+Math.sin(a)*.34,.65)}
// Pendant finial echoes the lotus without introducing a second focal point.
for(let i=0;i<8;i++){const a=i/8*Math.PI*2,g=new T.SphereGeometry(.11,12,8);g.scale(1,2.4,.55);g.rotateZ(a);g.translate(Math.sin(a)*.16,.24+Math.cos(a)*.16,.03);add(g,0)}
bead(.15,0,.2,.15,1)

const root=new T.Group();root.name='SHAKTI ornate Trishul — original modeled asset'
root.userData={author:'SHAKTI project / Codex',source:'scripts/build-trishul.mjs',license:'Original project asset; no external source',version:1}
let triangles=0
for(let i=0;i<buckets.length;i++){
 const normalized=buckets[i].map(g=>{const copy=g.index?g.toNonIndexed():g.clone();copy.deleteAttribute('uv');return copy})
 const merged=mergeGeometries(normalized),geometry=mergeVertices(merged,1e-5);merged.dispose();triangles+=geometry.index.count/3
 const normals=geometry.attributes.normal,normal=new T.Vector3()
 for(let j=0;j<normals.count;j++){normal.fromBufferAttribute(normals,j);if(normal.lengthSq()<1e-12)normal.set(0,1,0);else normal.normalize();normals.setXYZ(j,normal.x,normal.y,normal.z)}
 const mesh=new T.Mesh(geometry,materials[i]);mesh.name=materials[i].name;root.add(mesh)
 normalized.forEach(g=>g.dispose());buckets[i].forEach(g=>g.dispose())
}
const data=await new GLTFExporter().parseAsync(root,{binary:true,onlyVisible:true})
await mkdir('public/art/trishul',{recursive:true})
await writeFile('public/art/trishul/trishul-hero.glb',Buffer.from(data))
console.log(JSON.stringify({file:'public/art/trishul/trishul-hero.glb',bytes:data.byteLength,triangles,materials:materials.length},null,2))
