import * as T from 'three'

export const DURATION=16
export const SWAP_TIME=8.52
const smooth=(a:number,b:number,t:number)=>T.MathUtils.smoothstep(t,a,b)

/** Analytic pose, not accumulated physics: replay and arbitrary seeks agree. */
export function summoningPose(t:number,reduced=false):{x:number;y:number;z:number;rx:number;ry:number;rz:number;distance:number;shake:number}{
 if(t>12){
  const p=summoningPose(12,reduced),u=t-12
  // The incoming velocity is 14 + 2.6*(12-8.18). Continue it exactly,
  // then let the weapon ease toward the threshold rather than overshooting.
  const travel=(23.932*u-u*u)*(reduced?.1:1)
  return {...p,z:p.z-travel,distance:p.distance+travel}
 }
 const u=Math.max(0,t-8.18),distance=(14*(u-.18*(1-Math.exp(-u/.18)))+1.3*u*u)*(reduced?.1:1)
 const call=smooth(7.35,7.8,t)*(1-smooth(8.12,8.36,t))
 return {x:reduced?0:1.4*smooth(8.18,12,t),y:8.3+(reduced?.2:2.4)*(1-Math.exp(-u/.8)),z:-1.2-distance,
  rx:reduced?0:-1.08*smooth(7.98,8.52,t)-.06*smooth(9,12,t),ry:reduced?0:.35*smooth(7.98,8.52,t)+.12*smooth(9,12,t)+Math.sin(t*73)*.007*call,
  rz:reduced?0:.1*smooth(8.15,9.2,t)+Math.sin(t*91)*.003*call,distance,
  shake:reduced?0:Math.sin(t*97)*.018*call}
}

/** Deliberate second shot: no temporal smoothing across the editorial cut. */
export function flightCamera(t:number,portrait:boolean){
 const pose=summoningPose(t),q=new T.Quaternion().setFromEuler(new T.Euler(pose.rx,pose.ry,pose.rz))
 const settle=smooth(SWAP_TIME,9.7,t)
 const target=new T.Vector3(0,3.8-settle*.9,0).applyQuaternion(q).add(new T.Vector3(pose.x,pose.y,pose.z))
 const offsetZ=portrait?13+3*settle:9+4*settle
 const cameraZ=t<=10.25?pose.z+offsetZ:summoningPose(10.25).z+(portrait?16:13)-8*(1-Math.exp(-(t-10.25)*2))
 return {x:pose.x+(portrait?16:17),y:pose.y+12,z:cameraZ,
  tx:target.x,ty:target.y,tz:target.z,fov:portrait?36.5+5.5*settle:39+5*settle}
}

const vertex=`varying vec3 vLocal;varying vec3 vNormal;varying vec3 vEye;varying vec2 vUv;
void main(){vLocal=position;vUv=uv;vec4 mv=modelViewMatrix*vec4(position,1.);vEye=-mv.xyz;vNormal=normalMatrix*normal;gl_Position=projectionMatrix*mv;}`

export class Summoning {
 private root=new T.Group()
 private burst:T.InstancedMesh
 private sparks:T.Points
 private sparkGeometry=new T.BufferGeometry()
 private sparkSeeds:{seed:number;origin:T.Vector3;velocity:T.Vector3;delay:number}[]=[]
 private trailGeometry=new T.BufferGeometry()
 private dust:T.Points
 private shafts=new T.Group()
 private resources:(T.BufferGeometry|T.Material)[]=[]
 private uniforms={uTime:{value:-1},uBurst:{value:0},uDpr:{value:1}}
 private quaternion=new T.Quaternion()
 private euler=new T.Euler()
 private offset=new T.Vector3()
 private center=new T.Vector3()
 private p=new T.Vector3()
 private q=new T.Vector3()
 private tangent=new T.Vector3()
 private side=new T.Vector3()
 private oldQ=new T.Quaternion()
 private segments=42
 private trails:T.Mesh
 // Measured tip extrema of the normalized, unchanged Keshav geometry, minus pivot Y.
 private anchors=[new T.Vector3(-2.192121,4.840644,-.009810),new T.Vector3(.046045,6.349363,-.016189),new T.Vector3(2.327198,4.878753,-.006166)]

 constructor(private scene:T.Scene,private original:T.Group,private replacement:T.Group,private reduced:boolean){
  const material=(fragment:string,extra:T.ShaderMaterialParameters={})=>{
   const m=new T.ShaderMaterial({vertexShader:vertex,fragmentShader:fragment,uniforms:this.uniforms,transparent:true,depthWrite:false,...extra});this.resources.push(m);return m
  }
  // Camera-facing ribbons stretch along the weapon's axis, never close around it.
  const rayGeometry=new T.PlaneGeometry(1,1);this.resources.push(rayGeometry)
  const rayMaterial=material(`uniform float uBurst;uniform float uTime;varying vec2 vUv;
   void main(){float x=abs(vUv.x-.5)*2.;float edge=exp(-x*x*12.);float ends=pow(max(0.,sin(vUv.y*3.14159)),.65);
    float rush=.6+.4*sin(vUv.y*22.-uTime*70.);gl_FragColor=vec4(4.,1.9,.42,uBurst*edge*ends*rush*.7);}`,{blending:T.AdditiveBlending,side:T.DoubleSide,forceSinglePass:true})
  rayMaterial.vertexShader=`varying vec2 vUv;void main(){vUv=uv;
   vec4 a=modelViewMatrix*instanceMatrix*vec4(0.,0.,0.,1.);vec4 b=modelViewMatrix*instanceMatrix*vec4(0.,1.,0.,1.);
   vec2 along=normalize(b.xy-a.xy+vec2(.00001));vec2 side=vec2(-along.y,along.x);
   vec4 p=a+(b-a)*(uv.y-.5);p.xy+=side*(uv.x-.5)*length(instanceMatrix[0].xyz);gl_Position=projectionMatrix*p;}`
  this.burst=new T.InstancedMesh(rayGeometry,rayMaterial,7);this.burst.frustumCulled=false
  const matrix=new T.Matrix4(),orientation=new T.Quaternion()
  for(let i=0;i<7;i++){const seed=(i*.61803398875)%1;matrix.compose(new T.Vector3((seed-.5)*3.7,1.3+(i%3)*.5,Math.sin(i*3.2)*.5),orientation,new T.Vector3(i===3?.18:.035+seed*.065,8+seed*10,1));this.burst.setMatrixAt(i,matrix)}
  this.root.add(this.burst)
  // Thirty-six deterministic, one-shot sparks emitted into the wake.
  const sparkPositions=new Float32Array(36*3),sparkAlpha=new Float32Array(36)
  for(let i=0;i<36;i++){const seed=(i*.61803398875)%1;this.sparkSeeds.push({seed,origin:new T.Vector3((seed-.5)*3.7,3+((i*.4142)%1)*3,.15),velocity:new T.Vector3(Math.sin(i*17)*2.2,.6+seed,4+seed*7),delay:8.36+seed*.16})}
  this.sparkGeometry.setAttribute('position',new T.BufferAttribute(sparkPositions,3).setUsage(T.DynamicDrawUsage));this.sparkGeometry.setAttribute('aAlpha',new T.BufferAttribute(sparkAlpha,1).setUsage(T.DynamicDrawUsage));this.resources.push(this.sparkGeometry)
  const sparkMaterial=new T.ShaderMaterial({uniforms:this.uniforms,transparent:true,depthWrite:false,blending:T.AdditiveBlending,
   vertexShader:`attribute float aAlpha;uniform float uDpr;varying float vAlpha;void main(){vAlpha=aAlpha;vec4 mv=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(48.*uDpr/-mv.z,1.,3.5);}`,
   fragmentShader:`varying float vAlpha;void main(){float r=length(gl_PointCoord-.5)*2.;gl_FragColor=vec4(3.,1.2,.18,exp(-r*r*5.)*vAlpha);}`})
  this.resources.push(sparkMaterial);this.sparks=new T.Points(this.sparkGeometry,sparkMaterial);this.sparks.frustumCulled=false;scene.add(this.sparks)
  const positions=new Float32Array(this.anchors.length*this.segments*6*3),uv=new Float32Array(this.anchors.length*this.segments*6*2)
  let i=0
  for(let a=0;a<this.anchors.length;a++)for(let j=0;j<this.segments;j++)for(const [s,k] of [[-1,j],[1,j],[-1,j+1],[1,j],[1,j+1],[-1,j+1]]){uv[i++]=(s+1)/2;uv[i++]=k/this.segments}
  this.trailGeometry.setAttribute('position',new T.BufferAttribute(positions,3).setUsage(T.DynamicDrawUsage));this.trailGeometry.setAttribute('uv',new T.BufferAttribute(uv,2));this.resources.push(this.trailGeometry)
  this.trails=new T.Mesh(this.trailGeometry,material(`varying vec2 vUv;uniform float uTime;
   void main(){float width=pow(max(0.,1.-abs(vUv.x-.5)*2.),1.5);float fade=pow(1.-vUv.y,1.5)*smoothstep(8.54,8.9,uTime);gl_FragColor=vec4(3.,1.25,.2,width*fade*.6);}`,{blending:T.AdditiveBlending,side:T.DoubleSide}))
  this.trails.frustumCulled=false;scene.add(this.trails)
  const dustGeometry=new T.BufferGeometry(),dustPositions=[],seeds=[]
  let seed=849;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}
  for(let j=0;j<340;j++){dustPositions.push((rand()-.5)*35,1+rand()*24,-6-rand()*72);seeds.push(rand())}
  dustGeometry.setAttribute('position',new T.Float32BufferAttribute(dustPositions,3));dustGeometry.setAttribute('aSeed',new T.Float32BufferAttribute(seeds,1));this.resources.push(dustGeometry)
  const dustMaterial=new T.ShaderMaterial({uniforms:this.uniforms,transparent:true,depthWrite:false,blending:T.AdditiveBlending,
   vertexShader:`attribute float aSeed;uniform float uTime;uniform float uDpr;varying float vSeed;
    void main(){vSeed=aSeed;vec3 p=position+vec3(sin(uTime*.3+aSeed*30.),cos(uTime*.25+aSeed*12.),0.)*.12;vec4 mv=modelViewMatrix*vec4(p,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp((15.+aSeed*25.)*uDpr/-mv.z,.6,3.);}`,
   fragmentShader:`varying float vSeed;uniform float uTime;void main(){float r=length(gl_PointCoord-.5)*2.;gl_FragColor=vec4(.9,.63,.26,exp(-r*r*6.)*.16*smoothstep(8.5,9.2,uTime));}`})
  this.resources.push(dustMaterial);this.dust=new T.Points(dustGeometry,dustMaterial);this.dust.frustumCulled=false;scene.add(this.dust)
  const cone=new T.ConeGeometry(5,25,32,1,true);this.resources.push(cone)
  const shaftMaterial=material(`varying vec2 vUv;varying vec3 vNormal;varying vec3 vEye;uniform float uTime;
   void main(){float rim=pow(abs(dot(normalize(vNormal),normalize(vEye))),.8);float a=sin(vUv.y*3.14159)*rim*.018*smoothstep(8.65,9.5,uTime);gl_FragColor=vec4(.65,.50,.28,a);}`,{blending:T.AdditiveBlending,side:T.DoubleSide})
  for(const [x,y,z,r] of [[-9,13,-23,-.3],[10,15,-47,.24],[-8,13,-70,-.18]]){const mesh=new T.Mesh(cone,shaftMaterial);mesh.position.set(x,y,z);mesh.rotation.z=r;this.shafts.add(mesh)}
  scene.add(this.root,this.shafts)
  this.root.visible=this.trails.visible=this.dust.visible=this.shafts.visible=this.sparks.visible=false
 }
 prewarm(){this.root.visible=this.burst.visible=this.trails.visible=this.dust.visible=this.shafts.visible=this.sparks.visible=true}
 update(t:number,camera:T.Camera,dpr:number){
  const pose=summoningPose(t,this.reduced)
  this.uniforms.uTime.value=t;this.uniforms.uDpr.value=dpr
  this.uniforms.uBurst.value=this.reduced?0:Math.exp(-Math.pow((t-8.515)/.085,2))
  this.original.visible=t>4.15&&t<SWAP_TIME;this.replacement.visible=t>=SWAP_TIME
  this.root.visible=this.uniforms.uBurst.value>.001;this.trails.visible=t>SWAP_TIME&&!this.reduced;this.dust.visible=this.shafts.visible=t>8.5;this.sparks.visible=!this.reduced&&t>8.36&&t<9.15
  if(t<=7){this.original.position.set(0,2.1,-1.2);this.original.rotation.set(0,0,0);this.original.scale.setScalar(1)}
  else{
   this.quaternion.setFromEuler(this.euler.set(pose.rx,pose.ry,pose.rz));this.center.set(pose.x+pose.shake,pose.y,pose.z)
   this.offset.set(0,6.2,0).applyQuaternion(this.quaternion)
   for(const model of [this.original,this.replacement]){model.position.copy(this.center).sub(this.offset);model.quaternion.copy(this.quaternion);model.scale.setScalar(1)}
  }
  this.root.position.set(pose.x,pose.y,pose.z);this.root.quaternion.setFromEuler(this.euler.set(pose.rx,pose.ry,pose.rz))
  if(this.sparks.visible){const positions=this.sparkGeometry.attributes.position as T.BufferAttribute,alpha=this.sparkGeometry.attributes.aAlpha as T.BufferAttribute;this.sparkSeeds.forEach((spark,i)=>{const life=t-spark.delay;this.pointAt(spark.delay,spark.origin,this.p);this.p.addScaledVector(spark.velocity,Math.max(0,life));this.p.y-=Math.max(0,life)*Math.max(0,life)*.8;positions.setXYZ(i,this.p.x,this.p.y,this.p.z);alpha.setX(i,life>0&&life<.6?Math.sin(life/.6*Math.PI)*.8:0)});positions.needsUpdate=alpha.needsUpdate=true}
  if(this.trails.visible)this.updateTrails(t,camera)
 }
 private pointAt(t:number,anchor:T.Vector3,out:T.Vector3){const pose=summoningPose(t,this.reduced);this.oldQ.setFromEuler(this.euler.set(pose.rx,pose.ry,pose.rz));return out.copy(anchor).applyQuaternion(this.oldQ).add(this.center.set(pose.x,pose.y,pose.z))}
 private updateTrails(t:number,camera:T.Camera){
  const pos=this.trailGeometry.attributes.position as T.BufferAttribute;let index=0
  for(const anchor of this.anchors)for(let j=0;j<this.segments;j++){
   const age=j/this.segments*.75,next=(j+1)/this.segments*.75
   this.pointAt(Math.max(SWAP_TIME,t-age),anchor,this.p);this.pointAt(Math.max(SWAP_TIME,t-next),anchor,this.q)
   this.tangent.subVectors(this.q,this.p).normalize();this.side.subVectors(camera.position,this.p).cross(this.tangent).normalize().multiplyScalar(.048*(1-j/this.segments*.7))
   for(const [sign,k] of [[-1,0],[1,0],[-1,1],[1,0],[1,1],[-1,1]]){const p=k?this.q:this.p;pos.setXYZ(index++,p.x+this.side.x*sign,p.y+this.side.y*sign,p.z+this.side.z*sign)}
  }
  pos.needsUpdate=true
 }
 get burstStrength(){return this.reduced?0:this.uniforms.uBurst.value}
 snapshot(){return {originalVisible:this.original.visible,replacementVisible:this.replacement.visible,burst:this.uniforms.uBurst.value,position:this.original.position.toArray(),replacementPosition:this.replacement.position.toArray(),quaternion:this.original.quaternion.toArray(),replacementQuaternion:this.replacement.quaternion.toArray(),scale:this.original.scale.toArray()}}
 dispose(){this.resources.forEach(r=>r.dispose());this.root.removeFromParent();this.trails.removeFromParent();this.dust.removeFromParent();this.shafts.removeFromParent();this.sparks.removeFromParent()}
}
