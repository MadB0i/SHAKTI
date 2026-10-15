import * as T from 'three'
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'
import { flightCamera } from './Summoning'

const smooth=(a:number,b:number,t:number)=>T.MathUtils.smoothstep(t,a,b)
const mix=T.MathUtils.lerp
export const GATE_Z=-156

/** One continuous camera move from the approved 12-second shot. No temporal state. */
export function gatewayCamera(t:number,portrait:boolean,reduced=false){
 const incoming=flightCamera(12,portrait),u=t-12,s=smooth(12,14.1,t)
 const z= incoming.z-7*u*u // zero initial velocity, matching the almost-settled incoming dolly
 const framing={x:portrait?2.2:9,y:portrait?18.5:19.5,z:Math.max(portrait?-108:-114,z),tx:0,ty:portrait?18.3:18.4,tz:GATE_Z-4,fov:portrait?48:46}
 if(reduced)return {x:0,y:18,z:portrait?-98:-103,tx:0,ty:18,tz:GATE_Z,fov:portrait?52:48}
 return {x:mix(incoming.x,framing.x,s),y:mix(incoming.y,framing.y,s),z:framing.z,tx:mix(incoming.tx,framing.tx,s),ty:mix(incoming.ty,framing.ty,s),tz:mix(incoming.tz,framing.tz,s),fov:mix(incoming.fov,framing.fov,s)}
}

type Buckets=Map<T.Material,T.BufferGeometry[]>
export class Gateway {
 readonly root=new T.Group()
 readonly ready:Promise<void>
 private architecture=new T.Group()
 private leaves=[new T.Group(),new T.Group()]
 private resources:(T.BufferGeometry|T.Material)[]=[]
 private textures:T.Texture[]=[]
 private metallic:T.MeshStandardMaterial[]=[]
 private key:T.SpotLight
 private fill:T.PointLight
 private inner:T.PointLight
 private reveal={value:0}
 private time={value:12}
 private opening={value:0}
 private dpr={value:1}
 private disposed=false
 constructor(private scene:T.Scene,private reduced:boolean){
  this.root.name='Cosmic gateway — Phase 2B only';this.root.visible=false;scene.add(this.root)
  this.architecture.position.z=GATE_Z;this.root.add(this.architecture)
  const material=(color:number,metalness:number,roughness:number)=>{
   const m=new T.MeshStandardMaterial({color,metalness,roughness,envMapIntensity:.72});this.resources.push(m);this.metallic.push(m)
   m.onBeforeCompile=shader=>{
    shader.uniforms.uGatewayReveal=this.reveal
    shader.vertexShader='varying vec3 vCarving;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvCarving=position;')
    shader.fragmentShader='uniform float uGatewayReveal;varying vec3 vCarving;\n'+shader.fragmentShader
    shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
     float grain=fract(sin(dot(floor(vCarving*65.),vec3(12.989,78.233,37.719)))*43758.5453);
     roughnessFactor=clamp(roughnessFactor+.12*(grain-.5)+.07*sin(vCarving.y*1.4+vCarving.x*2.3),.22,.95);`)
    shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>','outgoingLight*=uGatewayReveal;\n#include <opaque_fragment>')
   };m.customProgramCacheKey=()=> 'gateway-antique-gold-v1';return m
  }
  const gold=material(0x9f7031,.88,.48),edge=material(0xd2a45c,.91,.34),recess=material(0x2d231c,.76,.52),stone=material(0x141c2b,.35,.55),crimson=material(0x380b12,.15,.78)
  const fixed:Buckets=new Map(),doorBuckets=[new Map(),new Map()] as Buckets[]
  const add=(b:Buckets,g:T.BufferGeometry,m:T.Material,x=0,y=0,z=0,rx=0,ry=0,rz=0,sx=1,sy=1,sz=1)=>{
   g.applyMatrix4(new T.Matrix4().compose(new T.Vector3(x,y,z),new T.Quaternion().setFromEuler(new T.Euler(rx,ry,rz)),new T.Vector3(sx,sy,sz)))
   // Unified, unindexed attributes permit heterogeneous relief to share draw calls.
   const a=g.index?g.toNonIndexed():g;if(a!==g)g.dispose();a.deleteAttribute('uv');if(!b.has(m))b.set(m,[]);b.get(m)!.push(a)
  }
  const box=(b:Buckets,m:T.Material,x:number,y:number,z:number,w:number,h:number,d:number)=>add(b,new T.BoxGeometry(w,h,d),m,x,y,z)
  const ring=(b:Buckets,m:T.Material,x:number,y:number,z:number,r:number,tube:number)=>add(b,new T.TorusGeometry(r,tube,6,48),m,x,y,z)
  const curve=(b:Buckets,m:T.Material,pts:number[][],r:number)=>add(b,new T.TubeGeometry(new T.CatmullRomCurve3(pts.map(p=>new T.Vector3(...p as [number,number,number]))),32,r,6,false),m)
  const petalShape=new T.Shape();petalShape.moveTo(0,0);petalShape.bezierCurveTo(-.6,.5,-.45,1.2,0,1.65);petalShape.bezierCurveTo(.45,1.2,.6,.5,0,0)
  const petal=new T.ExtrudeGeometry(petalShape,{depth:.16,bevelEnabled:true,bevelSize:.08,bevelThickness:.08,bevelSegments:2,curveSegments:8})
  const lotus=(b:Buckets,x:number,y:number,z:number,r:number)=>{
   ring(b,edge,x,y,z,r*.95,.065);ring(b,gold,x,y,z,r*1.12,.09)
   for(let i=0;i<12;i++)add(b,petal.clone(),gold,x,y,z+.08,0,0,i*Math.PI/6,r*.58,r*.58,1)
   add(b,new T.SphereGeometry(r*.29,16,8),edge,x,y,z+.22,0,0,0,1,1,.45)
   ring(b,recess,x,y,z+.25,r*.34,.035)
  }
  // Heavy stepped plinth and actual dark stone threshold, with inset gold rails.
  for(let i=0;i<4;i++){box(fixed,stone,0,-.65-i*.6,4+i*1.5,38+i*3,.65,16+i*3);box(fixed,gold,0,-.32-i*.6,10+i*3,38+i*3,.12,.18)}
  box(fixed,stone,0,-.22,-20,31,.4,40)
  for(const x of [-9.8,9.8])box(fixed,gold,x,14,0,.65,28,3.2)
  // Paired, staggered shafts establish deep jambs rather than a flat picture frame.
  for(const side of [-1,1])for(let tier=0;tier<2;tier++){
   const x=side*(11.6+tier*3.2),z=1.3-tier*2
   box(fixed,stone,x,14,z-1,2.8,28,2.5)
   for(const [y,r,h] of [[.5,2.2,1],[1.4,1.8,.65],[3,1.5,1.4],[24.6,1.6,1.3],[26,2.05,1.1],[27.2,2.5,1.2]])add(fixed,new T.CylinderGeometry(r*.9,r,h,8),gold,x,y,z)
   add(fixed,new T.CylinderGeometry(1.03,1.28,20,32),gold,x,14,z+.5)
   // Fluted, narrow gold arrises; recessed stone remains visible between them.
   for(let k=0;k<16;k++){const a=k/16*Math.PI*2;add(fixed,new T.CylinderGeometry(.045,.07,19,6),recess,x+Math.cos(a)*1.17,14,z+.5+Math.sin(a)*1.17)}
   for(const y of [4,5.1,23.1,24.1])add(fixed,new T.CylinderGeometry(1.39,1.39,.23,16),edge,x,y,z+.5)
   // A single sculpted lotus capital; no repeated ornament blanket.
   for(let k=0;k<8;k++)add(fixed,petal.clone(),gold,x+Math.cos(k*Math.PI/4)*1.1,24.5,z+Math.sin(k*Math.PI/4)*1.1,0,k*Math.PI/4,Math.PI,1.1,1.5,1.4)
   for(const y of [2.8,25.7])lotus(fixed,x,y,z+2.05,.63)
  }
  // A solid, bevelled torana has real depth; the ribs are mouldings on it.
  const arch=new T.Shape()
  for(let i=0;i<=48;i++){const a=Math.PI-i/48*Math.PI,x=Math.cos(a)*12.5,y=27+Math.sin(a)*10.1;if(i===0)arch.moveTo(x,y);else arch.lineTo(x,y)}
  for(let i=0;i<=48;i++){const a=i/48*Math.PI;arch.lineTo(Math.cos(a)*10.1,27+Math.sin(a)*7.65)}
  arch.closePath()
  add(fixed,new T.ExtrudeGeometry(arch,{depth:2.3,bevelEnabled:true,bevelSize:.16,bevelThickness:.16,bevelSegments:2,curveSegments:48}),gold,0,0,-1.8)
  // Scalloped inner lip and distinct lotus medallions accent the curve.
  const lip:number[][]=[]
  for(let i=0;i<=96;i++){const a=i/96*Math.PI,r=.16*(1-Math.cos(a*14));lip.push([Math.cos(a)*(10.1-r),27+Math.sin(a)*(7.65-r),.85])}
  curve(fixed,edge,lip,.105)
  for(const a of [.35,.75,1.15,1.99,2.39,2.79]){
   const x=Math.cos(a)*11.25,y=27+Math.sin(a)*8.8
   lotus(fixed,x,y,.72,.5)
   curve(fixed,edge,[[x-.55,y-.5,.78],[x-1,y+.1,.78],[x-.65,y+.6,.78],[x+.4,y+.75,.78]],.065)
  }
  // Curved torana ribs and stepped, rising cornices. Opening is genuinely hollow.
  for(let layer=0;layer<4;layer++){
   const pts:number[][]=[];for(let i=0;i<=32;i++){const a=i/32*Math.PI;pts.push([Math.cos(a)*(10.1+layer*.6),27+Math.sin(a)*(7.7+layer*.55),.8-layer*.42])}
   curve(fixed,layer%2?edge:gold,pts,layer===3?.4:.23)
  }
  for(const side of [-1,1]){
   curve(fixed,gold,[[0,36,-1],[side*5,35,-1],[side*10,31.8,-1],[side*17,29,-1],[side*20,31,-1]],.48)
   curve(fixed,edge,[[0,37,-1.4],[side*5,36,-1.4],[side*11,33,-1.4],[side*18,30.7,-1.4],[side*20,32,-1.4]],.18)
   // Carved inward-facing scrolls at the shoulders.
   for(let j=0;j<3;j++)curve(fixed,gold,[[side*(11+j*.9),28.2,.7],[side*(12+j*.9),29.8,.7],[side*(11.9+j*.9),31,.7],[side*(10.8+j*.9),30.2,.7]],.12)
   box(fixed,crimson,side*16.5,19,-.2,1.7,9,.14);lotus(fixed,side*16.5,19,.03,.55)
  }
  lotus(fixed,0,35.2,1.0,1.6)
  // Kalasha finial, with a pinched pot profile and lotus crown.
  add(fixed,new T.LatheGeometry([[0,0],[.8,0],[1.05,.5],[1.1,1.1],[.55,1.8],[.4,2.1],[.7,2.25],[.15,2.8],[0,3.7]].map(p=>new T.Vector2(...p as [number,number])),32),gold,0,37,-1)
  // Thick double leaves, their hinges remain fixed at +/-9.2 in world space.
  this.leaves.forEach((leaf,i)=>{
   const side=i===0?-1:1,b=doorBuckets[i],cx=-side*4.6
   leaf.position.set(side*9.2,0,0);this.architecture.add(leaf)
   box(b,recess,cx,13.6,-.38,9.2,27.2,.95)
   // Raised rails over dark recessed panels, with beveled nested fillets.
   for(const dx of [-4.28,4.28])for(let k=0;k<3;k++)box(b,k===1?recess:gold,cx+dx+Math.sign(dx)*k*.095,13.6,.22-k*.08,.15,26.6,.18)
   for(const y of [.4,8.4,18.4,26.8]){box(b,gold,cx,y,.26,8.5,.24,.25);box(b,edge,cx,y+.25,.2,8.2,.055,.1)}
   // Interlocking incised borders and corner tendrils, kept subordinate to the three panels.
   for(const dx of [-3.75,3.75]){
    const pts:number[][]=[];for(let j=0;j<=45;j++)pts.push([cx+dx+Math.sin(j*Math.PI/2)*.11,1+j*.56,.36])
    curve(b,gold,pts,.045)
   }
   for(const y of [4.4,22.6]){
    lotus(b,cx,y,.25,2.65)
    // Spokes with genuinely recessed channels, front and side relief.
    for(let k=0;k<24;k++){const a=k*Math.PI/12;add(b,new T.BoxGeometry(.065,.55,.12),edge,cx+Math.sin(a)*2.35,y+Math.cos(a)*2.35,.48,0,0,-a)}
    for(const sx of [-1,1])for(const sy of [-1,1])curve(b,gold,[[cx+sx*3.6,y+sy*3.3,.3],[cx+sx*2.5,y+sy*3.1,.3],[cx+sx*2.7,y+sy*2.5,.4],[cx+sx*3.3,y+sy*2.7,.4]],.075)
   }
   // Central climbing stem and asymmetric leaves: deliberate floral panel.
   curve(b,gold,[[cx,9.1,.3],[cx-1.3,11.7,.3],[cx+.8,14,.3],[cx-.3,17.7,.3]],.1)
   for(let k=0;k<6;k++){
    const sign=k%2?-1:1,y=10+k*1.2,x=cx+Math.sin(k*1.4)*.8
    add(b,petal.clone(),gold,x,y,.36,0,0,sign*.95,.75,.9,1)
    curve(b,edge,[[x,y,.5],[x+sign*.9,y+.5,.5],[x+sign*1.7,y+1,.42]],.035)
   }
   ring(b,edge,cx-side*3.05,13.2,.53,.36,.075)
   for(const y of [2,13.5,25]){add(b,new T.CylinderGeometry(.22,.22,1.4,12),edge,0,y,.12);box(b,gold,-side*.5,y,.15,1.1,.24,.26)}
   // Outer edge and rear rails remain substantial when the leaf turns.
   for(const y of [.7,13.6,26.4])box(b,gold,cx,y,-.9,8.9,.24,.13)
  })
  const build=(b:Buckets,parent:T.Group)=>b.forEach((gs,m)=>{const merged=mergeGeometries(gs,false);gs.forEach(g=>g.dispose());if(!merged)throw new Error('Gateway relief merge failed');this.resources.push(merged);const mesh=new T.Mesh(merged,m);mesh.castShadow=mesh.receiveShadow=true;parent.add(mesh)})
  build(fixed,this.architecture);doorBuckets.forEach((b,i)=>build(b,this.leaves[i]));petal.dispose()
  this.key=new T.SpotLight(0xffe0a4,2200,110,Math.PI*.3,.8,2);this.key.position.set(-9,35,GATE_Z+30);this.key.target.position.set(0,15,GATE_Z);this.key.castShadow=true;this.key.shadow.mapSize.set(1024,1024);this.key.shadow.bias=-.0004;this.key.shadow.normalBias=.06
  this.fill=new T.PointLight(0x5266c9,300,80,2);this.fill.position.set(21,24,GATE_Z+8)
  this.inner=new T.PointLight(0xffc974,0,65,2);this.inner.position.set(0,17,GATE_Z-12)
  this.root.add(this.key,this.key.target,this.fill,this.inner)
  this.makeStars();this.makeEnergy()
  this.ready=new T.TextureLoader().loadAsync(`${import.meta.env.BASE_URL}art/cosmic-background.png`).then(tex=>{
   if(this.disposed){tex.dispose();return}this.textures.push(tex);tex.colorSpace=T.SRGBColorSpace
   // Supplied file is an asset-sheet atlas. UVs ONLY sample the isolated
   // upper-right nebula panel, above its caption (x 890..1530, y 8..350).
   const mat=this.shader(`uniform sampler2D uNebula;varying vec2 vUv;uniform float uReveal;
    void main(){vec2 atlas=vec2(mix(890./1536.,1530./1536.,vUv.x),mix(674./1024.,1016./1024.,vUv.y));vec3 c=texture2D(uNebula,atlas).rgb;
     gl_FragColor=vec4(c*vec3(.09,.11,.17)*uReveal,1.);#include <tonemapping_fragment>
     #include <colorspace_fragment>}`,{side:T.BackSide,uniforms:{uNebula:{value:tex},uReveal:this.reveal}})
   // A broad curved cyclorama uses the modest source panel as low-frequency
   // colour, while geometry stars supply sharp independent depth cues.
   const g=new T.PlaneGeometry(410,260,48,24),p=g.attributes.position
   for(let j=0;j<p.count;j++)p.setZ(j,Math.cos(p.getX(j)/270)*-60)
   mat.side=T.DoubleSide;this.resources.push(g);const sky=new T.Mesh(g,mat);sky.position.set(0,50,GATE_Z-210);this.root.add(sky)
  })
 }
 private shader(fragmentShader:string,extra:T.ShaderMaterialParameters={}){
  const m=new T.ShaderMaterial({vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:fragmentShader.replace(';#include',';\n#include'),...extra});this.resources.push(m);return m
 }
 private makeStars(){
  const n=3300,p=new Float32Array(n*3),sizes=new Float32Array(n),colors=new Float32Array(n*3);let seed=731
  const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}
  for(let i=0;i<n;i++){p.set([(rand()-.5)*310,rand()*160-30,-85-rand()*300],i*3);sizes[i]=.6+rand()*1.7;const c=new T.Color().setRGB(.45+rand()*.55,.5+rand()*.4,.72+rand()*.28);colors.set(c.toArray(),i*3)}
  const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(p,3));g.setAttribute('aSize',new T.BufferAttribute(sizes,1));g.setAttribute('color',new T.BufferAttribute(colors,3));this.resources.push(g)
  const m=this.shader(`varying vec3 vColor;uniform float uReveal;void main(){float d=length(gl_PointCoord-.5);float a=exp(-d*d*24.);gl_FragColor=vec4(vColor,a*uReveal*.85);}`,{vertexShader:'attribute float aSize;attribute vec3 color;varying vec3 vColor;uniform float uDpr;void main(){vColor=color;vec4 mv=modelViewMatrix*vec4(position,1.);gl_PointSize=clamp(aSize*160./-mv.z,1.,4.)*uDpr;gl_Position=projectionMatrix*mv;}',uniforms:{uReveal:this.reveal,uDpr:this.dpr},transparent:true,depthWrite:false,blending:T.AdditiveBlending})
  const stars=new T.Points(g,m);stars.frustumCulled=false;this.root.add(stars)
 }
 private makeEnergy(){
  // Layered, curved nebula wisps are spatial geometry, with no temple imagery.
  for(let i=0;i<3;i++){
   const g=new T.PlaneGeometry(130,70,32,16),p=g.attributes.position
   for(let j=0;j<p.count;j++)p.setZ(j,Math.sin(p.getX(j)/45+i)*12);g.computeVertexNormals();this.resources.push(g)
   const m=this.shader(`varying vec2 vUv;uniform float uReveal;uniform float uTime;
    void main(){float ridge=vUv.y-.48-.18*sin(vUv.x*6.+uTime*.035);float a=exp(-ridge*ridge*70.)*pow(max(0.,sin(vUv.x*3.14159)),2.);
     gl_FragColor=vec4(.10,.055,.22,a*.15*uReveal);}`,{uniforms:{uReveal:this.reveal,uTime:this.time},transparent:true,depthWrite:false,side:T.DoubleSide,blending:T.AdditiveBlending})
   const cloud=new T.Mesh(g,m);cloud.position.set((i-1)*15,34+i*8,GATE_Z-45-i*42);cloud.rotation.z=(i-1)*.3;this.root.add(cloud)
  }
  // Light fan starts behind the physical leaves: depth testing masks it while closed.
  const g=new T.PlaneGeometry(1,1);this.resources.push(g)
  const m=this.shader(`varying vec2 vUv;uniform float uOpen;uniform float uReveal;
   void main(){float a=exp(-pow((vUv.x-.5)*7.,2.))*pow(max(0.,sin(vUv.y*3.14159)),.8);gl_FragColor=vec4(2.2,1.1,.26,a*uOpen*uReveal*.055);}`,{uniforms:{uOpen:this.opening,uReveal:this.reveal},transparent:true,depthWrite:false,blending:T.AdditiveBlending,side:T.DoubleSide})
  for(let i=0;i<7;i++){const ray=new T.Mesh(g,m);ray.position.set((i-3)*2,17,GATE_Z-4);ray.rotation.y=(i-3)*.13;ray.rotation.z=(i-3)*.07;ray.scale.set(2.5,29,1);this.root.add(ray)}
 }
 setEnvironment(texture:T.Texture){for(const m of this.metallic)m.envMap=texture}
 initTextures(renderer:T.WebGLRenderer){this.textures.forEach(t=>renderer.initTexture(t))}
 update(t:number,dpr:number){
  this.root.visible=t>12;this.reveal.value=smooth(12,13.25,t);this.time.value=t;this.dpr.value=dpr
  const o=smooth(14.5,16,t);this.opening.value=o
  this.leaves[0].rotation.y=-o*1.36;this.leaves[1].rotation.y=o*1.36
  this.key.intensity=2200*this.reveal.value;this.fill.intensity=300*this.reveal.value;this.inner.intensity=850*o*this.reveal.value
 }
 snapshot(){return {visible:this.root.visible,reveal:this.reveal.value,opening:this.opening.value,doorAngles:this.leaves.map(l=>l.rotation.y),hinges:this.leaves.map(l=>l.getWorldPosition(new T.Vector3()).toArray()),thresholdZ:GATE_Z}}
 dispose(){this.disposed=true;this.root.removeFromParent();this.resources.forEach(r=>r.dispose());this.textures.forEach(t=>t.dispose());this.key.shadow.dispose();this.key.dispose();this.fill.dispose();this.inner.dispose()}
}
