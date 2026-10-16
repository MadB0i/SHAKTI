import * as T from 'three'
import { gsap } from 'gsap'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js'
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { diyaGeometry, floorPattern, sampleSurface } from './geometry'
import * as S from './shaders'
import { Summoning, summoningPose, flightCamera, SWAP_TIME, DURATION } from './Summoning'
import { Resonance } from './Resonance'
import { Gateway, gatewayCamera } from './Gateway'

export type Phase='ready'|'flame'|'awakening'|'transformation'|'hero'|'summoning'|'flight'|'cosmic'|'gateway'|'opening'|'catch'|'reveal'|'greeting'|'complete'
export interface Snapshot { time:number; phase:Phase; playing:boolean; quality:number; lamps:number; particles:number; drawCalls:number; triangles:number; renderer:string; frameMs:number[]; transitionFrameMs:number[]; gatewayFrameMs:number[];width:number; height:number; summoning?:ReturnType<Summoning['snapshot']>;gateway:ReturnType<Gateway['snapshot']>;audio:ReturnType<Resonance['snapshot']>;reduced:boolean;camera:{position:number[];quaternion:number[];fov:number};fade:number }
export interface Inspection { seek:(time:number)=>void; snapshot:()=>Snapshot; replay:()=>void }
declare global {interface Window {__SHAKTI__?:Inspection}}
const phaseAt=(t:number):Phase=>t<0?'ready':t<1.5?'flame':t<3.5?'awakening':t<7?'transformation':t<7.35?'hero':t<8.82?'summoning':t<=12?'flight':t<13?'cosmic':t<14.5?'gateway':t<DURATION?'opening':'complete'

export class Experience {
 private scene=new T.Scene()
 private camera=new T.PerspectiveCamera(44,1,.06,120)
 private renderer:T.WebGLRenderer
 private composer:EffectComposer
 private bloom:UnrealBloomPass
 private fade:ShaderPass
 private env:T.WebGLRenderTarget
 private resources:(T.BufferGeometry|T.Material)[]=[]
 private textures=new Set<T.Texture>()
 private uniforms={uTime:{value:-1},uClock:{value:0},uDpr:{value:1},uEye:{value:new T.Vector3()}}
 readonly ready:Promise<void>
 private heroEnv?:T.WebGLRenderTarget
 private heroLight:T.PointLight
 private riseLight:T.PointLight
 private heroHit:T.Mesh
 private floor?:T.Mesh
 private trident=new T.Group()
 private replacement=new T.Group()
 private summoning?:Summoning
 private gateway:Gateway
 private resonance=new Resonance()
 private timeline:gsap.core.Timeline
 private motion={x:1.75,y:1.9,z:11,tx:0,ty:.45,tz:7.3,fov:44}
 private observer:ResizeObserver
 private raf=0
 private last=0
 private elapsed=-1
 private playbackClock?:()=>number|undefined
 private playing=false
 private portrait=false
 private reduced=matchMedia('(prefers-reduced-motion: reduce)').matches
 private ratio=Math.min(devicePixelRatio,1.65)
 private frames:number[]=[]
 private transitionFrames:number[]=[]
 private gatewayFrames:number[]=[]
 private slowFrames=0
 private width=1
 private height=1
 private disposed=false
 private suspended=false
 private heroLoaded=false
 private pointer=new T.Vector2()
 private rays=new T.Raycaster()
 private rendererName='Unavailable'
 private lastPhase:Phase='ready'
 private lamps=floorPattern()
 private particleCount=6000
 private listeners: (()=>void)[]=[]

 constructor(private host:HTMLElement,private onChange:(phase:Phase,playing:boolean)=>void,private onProgress:(time:number)=>void,private onError:(message:string)=>void) {
  this.renderer=new T.WebGLRenderer({antialias:true,powerPreference:'high-performance',alpha:false})
  this.renderer.setClearColor(0x000000);this.renderer.toneMapping=T.ACESFilmicToneMapping;this.renderer.toneMappingExposure=.92
  this.renderer.outputColorSpace=T.SRGBColorSpace
  this.renderer.info.autoReset=false
  this.renderer.shadowMap.type=T.PCFSoftShadowMap
  this.host.appendChild(this.renderer.domElement)
  this.renderer.domElement.setAttribute('aria-label','Interactive 3D diya and Trishul. Use the Ignite button to begin.')
  this.renderer.domElement.setAttribute('role','img')
  const gl=this.renderer.getContext(),debug=gl.getExtension('WEBGL_debug_renderer_info')
  if(debug)this.rendererName=String(gl.getParameter(debug.UNMASKED_RENDERER_WEBGL))
  const pmrem=new T.PMREMGenerator(this.renderer),room=new RoomEnvironment()
  this.env=pmrem.fromScene(room,.04);this.scene.environment=this.env.texture;room.dispose();pmrem.dispose()
  this.scene.add(new T.HemisphereLight(0x667895,0x301006,.18))
  const rim=new T.DirectionalLight(0xfbb15e,1.6);rim.position.set(-4,10,-5);this.scene.add(rim)
  this.heroLight=new T.PointLight(0xffa340,.08,10,2);this.heroLight.position.set(0,1.1,7.8);this.scene.add(this.heroLight)
  this.riseLight=new T.PointLight(0xffa83e,0,22,2);this.riseLight.position.set(-2,9,4);this.scene.add(this.riseLight)
  this.makeFloor();this.makeLamps();this.makeFlames();this.makePools();this.makeSmoke()
  this.trident.position.set(0,2.1,-1.2);this.scene.add(this.trident,this.replacement)
  this.gateway=new Gateway(this.scene,this.reduced)
  this.ready=this.loadHero()
  this.heroHit=new T.Mesh(this.keep(new T.SphereGeometry(.95,12,8)),this.keep(new T.MeshBasicMaterial({visible:false})));this.heroHit.position.set(0,.4,7.2);this.scene.add(this.heroHit)
  this.composer=new EffectComposer(this.renderer)
  this.composer.addPass(new RenderPass(this.scene,this.camera))
  this.bloom=new UnrealBloomPass(new T.Vector2(1,1),.42,.48,1.05);this.composer.addPass(this.bloom);this.composer.addPass(new OutputPass())
  this.fade=new ShaderPass({uniforms:{tDiffuse:{value:null},uFade:{value:0}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D tDiffuse;uniform float uFade;varying vec2 vUv;void main(){vec4 col=texture2D(tDiffuse,vUv);gl_FragColor=vec4(col.rgb*(1.-uFade),col.a);}'})
  this.fade.enabled=false;this.composer.addPass(this.fade)
  this.timeline=this.createTimeline()
  this.observer=new ResizeObserver(()=>this.resize());this.observer.observe(host);this.resize()
  const onPointer=(e:PointerEvent)=>{if(this.elapsed>=0)return;const rect=this.host.getBoundingClientRect();this.pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);this.rays.setFromCamera(this.pointer,this.camera);if(this.rays.intersectObject(this.heroHit).length)this.ignite()}
  const contextLost=(e:Event)=>{e.preventDefault();this.playing=false;this.onError('The graphics connection was interrupted. Reload to restore the scene.')}
  const visibility=()=>{this.last=performance.now();if(document.hidden)this.resonance.update(-1,false)}
  this.renderer.domElement.addEventListener('pointerup',onPointer);this.renderer.domElement.addEventListener('webglcontextlost',contextLost);document.addEventListener('visibilitychange',visibility)
  this.listeners.push(()=>this.renderer.domElement.removeEventListener('pointerup',onPointer),()=>this.renderer.domElement.removeEventListener('webglcontextlost',contextLost),()=>document.removeEventListener('visibilitychange',visibility))
  if(new URLSearchParams(location.search).has('inspect'))window.__SHAKTI__={seek:t=>this.seek(t),snapshot:()=>this.snapshot(),replay:()=>this.replay()}
  this.last=performance.now();this.raf=requestAnimationFrame(this.frame)
 }
 private keep<G extends T.BufferGeometry|T.Material>(resource:G):G {this.resources.push(resource);return resource}
 private async loadHero(){
  const loader=new GLTFLoader(),assets=await Promise.allSettled([
   loader.loadAsync(`${import.meta.env.BASE_URL}art/trishul/trishul-hero.glb`),
   loader.loadAsync(`${import.meta.env.BASE_URL}art/trishul/keshav/trishul-flight.glb`),
  ])
  if(this.disposed||assets.some(a=>a.status==='rejected')){
   for(const asset of assets)if(asset.status==='fulfilled')asset.value.scene.traverse(obj=>{if(obj instanceof T.Mesh){obj.geometry.dispose();for(const m of (Array.isArray(obj.material)?obj.material:[obj.material])){for(const value of Object.values(m))if(value instanceof T.Texture){value.dispose();if(value.image instanceof ImageBitmap)value.image.close()}m.dispose()}}})
   if(!this.disposed)throw new Error('Both Trishul assets must preload before ignition.')
   return
  }
  const loaded=(assets[0] as PromiseFulfilledResult<Awaited<ReturnType<GLTFLoader['loadAsync']>>>).value
  const flight=(assets[1] as PromiseFulfilledResult<Awaited<ReturnType<GLTFLoader['loadAsync']>>>).value
  await this.gateway.ready
  this.heroEnv=this.createHeroEnvironment()
  this.gateway.setEnvironment(this.heroEnv.texture)
  const positions:number[]=[]
  loaded.scene.updateMatrixWorld(true)
  loaded.scene.traverse(obj=>{
   if(!(obj instanceof T.Mesh))return
   this.keep(obj.geometry)
   const g=obj.geometry,index=g.index,p=g.attributes.position,temp=new T.Vector3()
   for(let i=0;i<(index?.count??p.count);i++){temp.fromBufferAttribute(p,index?index.getX(i):i).applyMatrix4(obj.matrixWorld);positions.push(temp.x,temp.y,temp.z)}
   for(const material of (Array.isArray(obj.material)?obj.material:[obj.material])){
    const m=material as T.MeshStandardMaterial;this.keep(m);m.envMap=this.heroEnv!.texture;m.envMapIntensity=1.05
    m.onBeforeCompile=shader=>{
     shader.uniforms.uTime=this.uniforms.uTime
     shader.vertexShader='varying vec3 vLocal;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvLocal=position;')
     shader.fragmentShader='uniform float uTime;varying vec3 vLocal;\n'+S.noise+shader.fragmentShader
     shader.fragmentShader=shader.fragmentShader.replace('#include <clipping_planes_fragment>',`#include <clipping_planes_fragment>
      float assemble=clamp((uTime-4.15)/1.35,0.,1.);float h=vLocal.y/12.6;
      if(assemble<1. && assemble<h+noise2(vLocal.xy*32.)*.025)discard;`)
     shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
      roughnessFactor*=.88+.24*noise2(vLocal.xy*180.);`)
     shader.fragmentShader=shader.fragmentShader.replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
      float edge=(1.-smoothstep(0.,.045,assemble-h))*(1.-smoothstep(5.5,5.85,uTime));
      totalEmissiveRadiance+=vec3(2.,.75,.12)*edge;`)
    }
   }
  })
  this.trident.add(loaded.scene)
  flight.scene.traverse(obj=>{if(obj instanceof T.Mesh){this.keep(obj.geometry);obj.frustumCulled=false;for(const mat of (Array.isArray(obj.material)?obj.material:[obj.material])){const m=mat as T.MeshStandardMaterial;this.keep(m);for(const value of Object.values(m))if(value instanceof T.Texture)this.textures.add(value);m.envMap=this.heroEnv!.texture;m.envMapIntensity=1.05}}})
  this.replacement.add(flight.scene)
  this.summoning=new Summoning(this.scene,this.trident,this.replacement,this.reduced)
  const sample=this.keep(new T.BufferGeometry());sample.setAttribute('position',new T.Float32BufferAttribute(positions,3));this.makeParticles(sample)
  this.trident.visible=this.replacement.visible=true;this.summoning.prewarm()
  this.textures.forEach(texture=>this.renderer.initTexture(texture))
  this.gateway.initTextures(this.renderer)
  await this.renderer.compileAsync(this.scene,this.camera)
  // Compile the post-12 light/shadow variants before user interaction.
  this.gateway.update(16,this.ratio);this.renderer.shadowMap.enabled=true
  await this.renderer.compileAsync(this.scene,this.camera)
  const warmTarget=new T.WebGLRenderTarget(1,1),warmPrevious=this.renderer.getRenderTarget(),warmCamera=this.camera.clone(),gm=gatewayCamera(16,this.portrait)
  warmCamera.position.set(gm.x,gm.y,gm.z);warmCamera.lookAt(gm.tx,gm.ty,gm.tz);warmCamera.far=900;warmCamera.updateProjectionMatrix()
  this.renderer.setRenderTarget(warmTarget);this.renderer.render(this.scene,warmCamera);this.renderer.setRenderTarget(warmPrevious);warmTarget.dispose()
  this.gateway.update(-1,this.ratio);this.renderer.shadowMap.enabled=false
  if(this.disposed)return
  // Warm buffers and effect programs before the clock can begin, offscreen.
  this.trident.visible=this.replacement.visible=true;this.summoning.prewarm()
  const target=new T.WebGLRenderTarget(1,1),previous=this.renderer.getRenderTarget()
  this.renderer.setRenderTarget(target);this.renderer.render(this.scene,this.camera);this.renderer.setRenderTarget(previous);target.dispose()
  this.summoning.update(-1,this.camera,this.ratio)
  if(!this.disposed)this.heroLoaded=true
 }
 private createHeroEnvironment(){
  const studio=new T.Scene();studio.background=new T.Color(.012,.015,.021)
  const panels:[number,number,number,number,number,number,number,number][]=[[-4,5,6,2.2,11,5,4.5,3.8],[5,4,2,1,10,2.4,3.2,4.4],[0,10,-3,8,1.2,4,2.3,.8],[-5,2,-4,2,7,1.8,.8,.2],[0,5,8,7,8,.65,.58,.43]]
  for(const [x,y,z,w,h,r,g,b] of panels){const mesh=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({color:new T.Color(r,g,b),side:T.DoubleSide}));mesh.position.set(x,y,z);mesh.lookAt(0,4,0);studio.add(mesh)}
  const pmrem=new T.PMREMGenerator(this.renderer),target=pmrem.fromScene(studio,.04,.1,50)
  studio.traverse(obj=>{if(obj instanceof T.Mesh){obj.geometry.dispose();obj.material.dispose()}});pmrem.dispose();return target
 }
 private shader(vertexShader:string,fragmentShader:string,extra:Partial<T.ShaderMaterialParameters>={}) {
  return this.keep(new T.ShaderMaterial({vertexShader,fragmentShader,uniforms:this.uniforms,...extra}))
 }
 private makeFloor(){
  const floor=new T.Mesh(this.keep(new T.PlaneGeometry(160,160)),this.shader(S.floorVertex,S.floorFragment));floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;this.scene.add(floor)
  this.floor=floor
 }
 private makeLamps(){
  const clay=this.keep(new T.MeshStandardMaterial({color:0x69301c,roughness:.92,metalness:.02,envMapIntensity:.18}))
  clay.onBeforeCompile=shader=>{
   shader.uniforms.uTime=this.uniforms.uTime
   shader.vertexShader='varying vec3 vClay;varying vec3 vLamp;\n'+shader.vertexShader.replace('#include <begin_vertex>',`#include <begin_vertex>
    vClay=position;
    vec4 center=vec4(0.,0.,0.,1.);
    #ifdef USE_INSTANCING
     center=instanceMatrix*center;
    #endif
    vLamp=(modelMatrix*center).xyz;`)
   shader.fragmentShader='uniform float uTime;varying vec3 vClay;varying vec3 vLamp;\n'+S.noise+shader.fragmentShader
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\ndiffuseColor.rgb*=.76+.18*noise2(vClay.xz*160.)+.04*sin(vClay.y*180.);')
   shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',`float distanceFromFirst=length(vLamp.xz-vec2(0.,7.));
    float delay=1.5+distanceFromFirst/17.5*1.8;
    float lightLevel=distanceFromFirst<.8 ? .20+.8*smoothstep(0.,.6,uTime) : .002+.18*smoothstep(delay,delay+.3,uTime);
    outgoingLight*=lightLevel;
    #include <opaque_fragment>`)
  }
  const bowl=this.keep(diyaGeometry(32)),matrix=new T.Matrix4(),scale=new T.Vector3(.43,.43,.43),q=new T.Quaternion()
  const instances=new T.InstancedMesh(bowl,clay,this.lamps.length);instances.castShadow=false
  this.lamps.forEach((lamp,i)=>{q.setFromAxisAngle(new T.Vector3(0,1,0),lamp.seed*6.28);matrix.compose(lamp.position,q,scale);instances.setMatrixAt(i,matrix)})
  this.scene.add(instances)
  const hero=new T.Group();hero.position.set(0,-.116,7);hero.scale.setScalar(1.8)
  const heroBowl=new T.Mesh(this.keep(diyaGeometry(96)),clay);heroBowl.castShadow=true;hero.add(heroBowl)
  const oilMaterial=this.shader(`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`,`varying vec2 vUv;uniform float uTime;uniform float uClock;${S.noise}
   void main(){float glow=smoothstep(0.,.4,uTime);float x=(vUv.x-.5)*6.;float y=vUv.y;
   float reflection=exp(-x*x*16.)*pow(y,4.)*(.8+.2*sin(y*60.+uClock*2.));
   vec3 col=vec3(.009,.004,.001)+vec3(1.4,.45,.06)*reflection*glow;
   gl_FragColor=vec4(col,1.);
   #include <tonemapping_fragment>
   #include <colorspace_fragment>
   }`)
  const oil=new T.Mesh(this.keep(new T.CircleGeometry(.335,64)),oilMaterial);oil.rotation.x=-Math.PI/2;oil.position.y=.28;hero.add(oil)
  const wickPath=new T.CatmullRomCurve3([new T.Vector3(0,.285,.2),new T.Vector3(0,.32,.45),new T.Vector3(0,.39,.63),new T.Vector3(0,.44,.71)])
  const wick=new T.Mesh(this.keep(new T.TubeGeometry(wickPath,24,.017,8,false)),this.keep(new T.MeshStandardMaterial({color:0x796446,roughness:1,envMapIntensity:0})));hero.add(wick)
  const tip=new T.Mesh(this.keep(new T.SphereGeometry(.017,12,8)),this.keep(new T.MeshStandardMaterial({color:0x080402,emissive:0xff3800,emissiveIntensity:.03})));tip.position.set(0,.44,.71);hero.add(tip)
  const contact=new T.Mesh(this.keep(new T.PlaneGeometry(1.8,1.8)),this.shader(S.floorVertex,`varying vec3 vWorld;void main(){float d=length((vWorld.xz-vec2(0.,7.))*.9);gl_FragColor=vec4(0.,0.,0.,exp(-d*d*6.)*.7);}`,{transparent:true,depthWrite:false}));contact.rotation.x=-Math.PI/2;contact.position.set(0,.016,7);this.scene.add(contact)
  this.scene.add(hero)
 }
 private makeFlames(){
  const g=this.keep(new T.PlaneGeometry(1,1,1,8)),count=this.lamps.length+1
  const delays=new Float32Array(count),seeds=new Float32Array(count),sizes=new Float32Array(count)
  const flames=new T.InstancedMesh(g,this.shader(S.flameVertex,S.flameFragment,{transparent:true,depthWrite:false,blending:T.AdditiveBlending}),count)
  const mat=new T.Matrix4()
  delays[0]=0;seeds[0]=.3;sizes[0]=.72;flames.setMatrixAt(0,mat.makeTranslation(0,.68,8.278))
  this.lamps.forEach((l,i)=>{delays[i+1]=l.delay;seeds[i+1]=l.seed;sizes[i+1]=.27+l.seed*.09;flames.setMatrixAt(i+1,mat.makeTranslation(l.position.x,.19,l.position.z))})
  g.setAttribute('aDelay',new T.InstancedBufferAttribute(delays,1));g.setAttribute('aSeed',new T.InstancedBufferAttribute(seeds,1));g.setAttribute('aSize',new T.InstancedBufferAttribute(sizes,1));flames.frustumCulled=false;this.scene.add(flames)
 }
 private makePools(){
  const g=this.keep(new T.PlaneGeometry(1,1));g.rotateX(-Math.PI/2)
  const count=this.lamps.length+1,delays=new Float32Array(count),pools=new T.InstancedMesh(g,this.shader(S.poolVertex,S.poolFragment,{transparent:true,depthWrite:false,blending:T.AdditiveBlending}),count),matrix=new T.Matrix4(),q=new T.Quaternion()
  pools.setMatrixAt(0,matrix.compose(new T.Vector3(0,.013,7.8),q,new T.Vector3(4,1,4)));delays[0]=0
  this.lamps.forEach((l,i)=>{delays[i+1]=l.delay;pools.setMatrixAt(i+1,matrix.compose(new T.Vector3(l.position.x,.012,l.position.z),q,new T.Vector3(1.2,1,1.2)))})
  g.setAttribute('aDelay',new T.InstancedBufferAttribute(delays,1));pools.frustumCulled=false;this.scene.add(pools)
 }
 private makeSmoke(){
  const g=this.keep(new T.PlaneGeometry(1,1)),n=18,seeds=new Float32Array(n),smoke=new T.InstancedMesh(g,this.shader(S.smokeVertex,S.smokeFragment,{transparent:true,depthWrite:false}),n),matrix=new T.Matrix4()
  for(let i=0;i<n;i++){seeds[i]=i/n;smoke.setMatrixAt(i,matrix)}g.setAttribute('aSeed',new T.InstancedBufferAttribute(seeds,1));smoke.frustumCulled=false;this.scene.add(smoke)
 }
 private makeParticles(geometry:T.BufferGeometry){
  const n=this.particleCount,g=this.keep(new T.BufferGeometry()),source=new Float32Array(n*3),seeds=new Float32Array(n),delays=new Float32Array(n)
  for(let i=0;i<n;i++){const l=this.lamps[i%this.lamps.length];source.set([l.position.x,.25,l.position.z],i*3);seeds[i]=(i*.61803398875)%1;delays[i]=seeds[i]*.24}
  g.setAttribute('position',new T.BufferAttribute(source,3));g.setAttribute('aTarget',new T.BufferAttribute(sampleSurface(geometry,n),3));g.setAttribute('aSeed',new T.BufferAttribute(seeds,1));g.setAttribute('aDelay',new T.BufferAttribute(delays,1))
  const points=new T.Points(g,this.shader(S.particleVertex,S.particleFragment,{transparent:true,depthWrite:false,blending:T.AdditiveBlending}));points.frustumCulled=false;this.scene.add(points)
 }
 private createTimeline(){
  const m=this.motion,tl=gsap.timeline({paused:true})
  Object.assign(m,{x:1.75,y:1.9,z:11,tx:0,ty:.45,tz:7.3,fov:44})
  if(this.reduced){Object.assign(m,{x:0,y:this.portrait?12:15,z:this.portrait?29:27,tx:0,ty:5,tz:-1,fov:44});tl.to(m,{duration:DURATION},0);return tl}
  tl.to(m,{x:1.2,y:2.3,z:11.5,ty:.3,tz:7,duration:1.5,ease:'power1.inOut'},0)
  tl.to(m,{x:this.portrait?0:1.2,y:this.portrait?22:21,z:this.portrait?17:15,tx:0,ty:0,tz:-.8,fov:this.portrait?48:48,duration:2.15,ease:'power2.inOut'},1.35)
  tl.to(m,{x:this.portrait?3.5:7.5,y:10,z:this.portrait?27:25,tx:this.portrait?0:2.2,ty:this.portrait?6.7:6.6,tz:-1.2,fov:this.portrait?41:37,duration:2.1,ease:'power2.inOut'},3.5)
  tl.to(m,{x:this.portrait?2.8:6.8,y:this.portrait?9.6:9.8,z:this.portrait?26.5:24.5,duration:.4,ease:'sine.out'},5.6)
  tl.to(m,{duration:1},6)
  tl.to(m,{duration:DURATION-7},7)
  return tl
 }
 private resize(){
  this.width=this.host.clientWidth;this.height=this.host.clientHeight
  const portrait=this.width/this.height<.85
  if(portrait!==this.portrait){this.portrait=portrait;this.timeline?.kill();this.timeline=this.createTimeline();if(this.elapsed>=0)this.timeline.time(this.elapsed)}
  this.camera.aspect=this.width/this.height;this.camera.updateProjectionMatrix()
  this.renderer.setPixelRatio(this.ratio);this.renderer.setSize(this.width,this.height)
  this.composer.setPixelRatio(this.ratio);this.composer.setSize(this.width,this.height);this.uniforms.uDpr.value=this.ratio
 }
 ignite(){if(this.heroLoaded&&this.elapsed<0){this.resonance.unlock();this.elapsed=0;this.playing=true;this.frames=[];this.transitionFrames=[];this.gatewayFrames=[];this.slowFrames=0;this.last=performance.now();this.notify()}}
 replay(){if(!this.heroLoaded)return;this.resonance.unlock();this.elapsed=0;this.playing=true;this.frames=[];this.transitionFrames=[];this.gatewayFrames=[];this.last=performance.now();this.timeline.time(0);this.notify()}
 toggle(){if(this.elapsed<0)return this.ignite();if(this.elapsed>=DURATION)return this.replay();this.playing=!this.playing;if(this.playing)this.resonance.unlock();this.last=performance.now();this.notify()}
 setSound(enabled:boolean){this.resonance.setEnabled(enabled)}
 setPlaybackClock(clock:()=>number|undefined){this.playbackClock=clock}
 setSuspended(value:boolean){this.suspended=value;this.last=performance.now()}
 get canvas(){return this.renderer.domElement}
 get audioStream(){return this.resonance.stream}
 seek(t:number){this.elapsed=Math.max(-1,Math.min(DURATION,t));this.playing=false;this.resonance.update(this.elapsed,false);this.timeline.time(Math.max(0,this.elapsed));this.notify()}
 private notify(){this.lastPhase=phaseAt(this.elapsed);this.onChange(this.lastPhase,this.playing)}
 private frame=(now:number)=>{
  if(this.disposed)return
  const dt=Math.min((now-this.last)/1000,.5);this.last=now
   if(!document.hidden&&!this.suspended){
   if(this.playing){this.elapsed=Math.min(DURATION,this.playbackClock?.()??this.elapsed+dt);if(this.elapsed>=DURATION)this.playing=false;const phase=phaseAt(this.elapsed);if(phase!==this.lastPhase)this.notify()}
   const clock=this.elapsed<=7?now:this.elapsed*1000
   this.uniforms.uTime.value=this.elapsed;this.uniforms.uClock.value=clock/1000
   this.timeline.time(Math.max(0,this.elapsed))
   let m=this.motion
   if(!this.reduced&&this.elapsed>8.1){
    if(this.elapsed>=SWAP_TIME)m=flightCamera(this.elapsed,this.portrait)
    else{const s=T.MathUtils.smoothstep(this.elapsed,8.1,SWAP_TIME),pose=summoningPose(this.elapsed),lerp=T.MathUtils.lerp;m={x:lerp(m.x,this.portrait?2.2:4.8,s),y:lerp(m.y,10.4,s),z:lerp(m.z,this.portrait?24:22,s),tx:lerp(m.tx,pose.x+1.3,s),ty:lerp(m.ty,8.6,s),tz:lerp(m.tz,pose.z,s),fov:m.fov}}
   }
   if(this.elapsed>12&&(!this.reduced||this.elapsed>=12.3))m=gatewayCamera(this.elapsed,this.portrait,this.reduced)
   this.camera.far=this.elapsed>12?900:120
   this.camera.position.set(m.x,m.y,m.z);this.camera.fov=m.fov;this.camera.lookAt(m.tx,m.ty,m.tz);this.camera.updateProjectionMatrix();this.uniforms.uEye.value.copy(this.camera.position)
   const fade=this.reduced?Math.max(T.MathUtils.smoothstep(this.elapsed,8.12,8.45)*(1-T.MathUtils.smoothstep(this.elapsed,8.61,8.94)),T.MathUtils.smoothstep(this.elapsed,12,12.28)*(1-T.MathUtils.smoothstep(this.elapsed,12.32,12.65))):0
   this.fade.enabled=fade>0;this.fade.uniforms.uFade.value=fade
   this.heroLight.intensity=this.elapsed<0?.08:(10.5+Math.sin(clock*.014)*.65+Math.sin(clock*.023)*.4)*Math.min(1,this.elapsed*5)
   this.riseLight.intensity=T.MathUtils.smoothstep(this.elapsed,4.15,5.8)*10
   this.riseLight.position.set(3.5,10,5);this.riseLight.color.set(0xffdda0);this.riseLight.distance=22
   if(this.elapsed>8.18){const pose=summoningPose(this.elapsed,this.reduced);this.riseLight.position.set(pose.x+3.5,pose.y+2,pose.z+6);this.riseLight.intensity=16}
   if(this.elapsed>=SWAP_TIME&&!this.reduced){const pose=summoningPose(this.elapsed),q=new T.Quaternion().setFromEuler(new T.Euler(pose.rx,pose.ry,pose.rz)),head=new T.Vector3(1.5,5.3,2.5).applyQuaternion(q);this.riseLight.position.set(pose.x+head.x,pose.y+head.y,pose.z+head.z);this.riseLight.distance=7;this.riseLight.intensity=22}
   if(this.summoning){this.summoning.update(this.elapsed,this.camera,this.ratio);this.riseLight.intensity+=this.summoning.burstStrength*12}
   else this.trident.visible=this.replacement.visible=false
   this.gateway.update(this.elapsed,this.ratio);this.renderer.shadowMap.enabled=this.elapsed>12
   if(this.floor)this.floor.visible=this.elapsed<=12
   this.resonance.update(this.elapsed,this.playing)
   this.renderer.info.reset();this.composer.render()
   this.onProgress(Math.max(0,this.elapsed))
   if(this.playing&&dt>0){this.frames.push(dt*1000);if(this.frames.length>1200)this.frames.shift();if(this.elapsed>7)this.transitionFrames.push(dt*1000);if(this.transitionFrames.length>650)this.transitionFrames.shift();if(this.elapsed>12)this.gatewayFrames.push(dt*1000);if(dt>.035)this.slowFrames++;if(this.slowFrames>12&&this.ratio>.65){this.ratio=Math.max(.65,this.ratio*.8);this.slowFrames=0;this.resize()}}
  }
  this.raf=requestAnimationFrame(this.frame)
 }
 snapshot():Snapshot{return {time:this.elapsed,phase:phaseAt(this.elapsed),playing:this.playing,quality:this.ratio,lamps:this.lamps.length+1,particles:this.particleCount,drawCalls:this.renderer.info.render.calls,triangles:this.renderer.info.render.triangles,renderer:this.rendererName,frameMs:[...this.frames],transitionFrameMs:[...this.transitionFrames],gatewayFrameMs:[...this.gatewayFrames],width:this.width,height:this.height,summoning:this.summoning?.snapshot(),gateway:this.gateway.snapshot(),audio:this.resonance.snapshot(),reduced:this.reduced,camera:{position:this.camera.position.toArray(),quaternion:this.camera.quaternion.toArray(),fov:this.camera.fov},fade:this.fade.uniforms.uFade.value}}
 dispose(){this.disposed=true;cancelAnimationFrame(this.raf);this.observer.disconnect();this.timeline.kill();this.listeners.forEach(fn=>fn());this.summoning?.dispose();this.gateway.dispose();this.resonance.dispose();this.resources.forEach(r=>r.dispose());this.textures.forEach(texture=>{texture.dispose();if(texture.image instanceof ImageBitmap)texture.image.close()});this.heroLight.shadow.dispose();this.env.dispose();this.heroEnv?.dispose();this.scene.traverse(obj=>{if(obj instanceof T.Light)obj.dispose()});this.composer.passes.forEach(p=>p.dispose());this.composer.dispose();this.renderer.dispose();this.renderer.domElement.remove();delete window.__SHAKTI__}
}
