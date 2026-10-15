import { Experience, type Phase } from './Experience'

export const FILM_DURATION=30
const BASE=import.meta.env.BASE_URL
const REVEAL=17.6,HOLD=27.6
const clips=[{file:'playback/divine-catch.mp4',start:0,offset:16,duration:1.6,crop:[0,0,706,1080]}, {file:'playback/divine-finale.mp4',start:0,offset:REVEAL,duration:10,crop:[0,0,726,1080]}]
const smooth=(a:number,b:number,t:number)=>{const u=Math.max(0,Math.min(1,(t-a)/(b-a)));return u*u*(3-2*u)}
const frame=()=>new Promise<void>(r=>requestAnimationFrame(()=>r()))

/** A media-clock edit after the unchanged 16-second WebGL shot. No video retiming. */
export class Hybrid {
 readonly web:Experience
 readonly ready:Promise<void>
 private videos=clips.map(()=>document.createElement('video'))
 private urls:string[]=[]
 private abort=new AbortController()
 private canvas=document.createElement('canvas')
 private ctx=this.canvas.getContext('2d')!
 private bridge=document.createElement('canvas')
 private bridgeReady=false
 private atmosphere=document.createElement('canvas')
 private observer:ResizeObserver
 private loaded=false
 private disposed=false
 private time=-1
 private phase:Phase='ready'
 private playing=false
 private media=false
 private active=0
 private advancing=false
 private token=0
 private raf=0
 private last=performance.now()
 private frames:number[]=[]
 private mediaFrames:number[]=[]
 private sound=true
 private audio?:AudioContext
 private score?:AudioBuffer
 private scoreSource?:AudioBufferSourceNode
 private scoreGain?:GainNode
 private scoreOrigin=0
 private output?:MediaStreamAudioDestinationNode
 private resonanceConnected=false
 private recording=false
 private cancelRecording?:()=>void
 private reduced=matchMedia('(prefers-reduced-motion: reduce)').matches
 private motionConsent=false
 private visibility=()=>{if(document.hidden&&this.playing)this.pause()}
 private blockEarly=(e:PointerEvent)=>{if(!this.loaded)e.stopImmediatePropagation()}

 constructor(private host:HTMLElement,private onChange:(p:Phase,playing:boolean)=>void,private onProgress:(t:number)=>void,private onError:(message:string)=>void){
  host.addEventListener('pointerup',this.blockEarly,true)
  this.web=new Experience(host,(p,play)=>{
   if(!this.media){if(play){this.advancing=true;this.unlock()}this.phase=p==='complete'?'opening':p;this.playing=play;this.emit()}
  },t=>{
   if(t>=15.8&&this.web){
    const source=this.web.canvas
    this.bridge.width=source.width;this.bridge.height=source.height
    this.bridge.getContext('2d')!.drawImage(source,0,0);this.bridgeReady=true
   }
   if(this.media)return
   this.time=this.web.snapshot().time
   this.onProgress(t)
   if(t>=16&&this.advancing){this.advancing=false;void this.enterMedia(0,!this.reduced||this.motionConsent)}
  },onError)
  this.atmosphere.width=4;this.atmosphere.height=6
  this.canvas.className='film-canvas';this.canvas.setAttribute('aria-hidden','true');this.canvas.hidden=true;host.append(this.canvas)
  this.observer=new ResizeObserver(()=>this.resize());this.observer.observe(host);this.resize()
  let loadTimer:ReturnType<typeof setTimeout>
  const timeout=new Promise<never>((_,reject)=>{loadTimer=setTimeout(()=>{this.abort.abort();reject(new Error('Film loading timed out'))},90000)})
  this.ready=Promise.race([Promise.all([this.web.ready,this.load()]),timeout]).then(()=>{this.loaded=true}).finally(()=>clearTimeout(loadTimer))
  document.addEventListener('visibilitychange',this.visibility)
  if(new URLSearchParams(location.search).has('inspect'))window.__SHAKTI__={seek:t=>this.seek(t),snapshot:()=>this.snapshot(),replay:()=>this.replay()}
  if(window.__SHAKTI__)Object.assign(window.__SHAKTI__,{record:()=>this.record(),toggle:()=>this.toggle(),setSound:(value:boolean)=>this.setSound(value)})
  this.raf=requestAnimationFrame(this.tick)
 }
 private async load(){
  await Promise.all(clips.map(async(c,i)=>{
   const response=await fetch(BASE+'videos/'+c.file,{signal:this.abort.signal})
   if(!response.ok)throw new Error(`${c.file}: HTTP ${response.status}`)
   const blob=await response.blob();if(this.disposed)return
   const v=this.videos[i];v.playsInline=true;v.preload='auto';v.controls=false
   const url=URL.createObjectURL(blob);this.urls.push(url)
   await new Promise<void>((resolve,reject)=>{v.onloadeddata=()=>resolve();v.onerror=()=>reject(new Error(`${c.file}: unsupported or damaged video`));v.src=url;v.load()})
   if(Math.abs(v.duration-c.duration)>.1)throw new Error(`${c.file}: duration changed; review the 30-second edit before playback`)
   v.onerror=()=>this.fail('A film clip could not decode. Reload to retry.')
   await this.position(v,c.start)
  }))
  const response=await fetch(BASE+'audio/shakti-original.m4a',{signal:this.abort.signal})
  if(!response.ok)throw new Error('Score could not load')
  this.score=await new OfflineAudioContext(2,1,48000).decodeAudioData(await response.arrayBuffer())
  await Promise.all([document.fonts.load('700 64px Cinzel'),document.fonts.load('600 48px "Noto Serif Bengali"','শুভ দুর্গাপূজা')])
  if(!document.fonts.check('600 48px "Noto Serif Bengali"','শুভ দুর্গাপূজা'))throw new Error('Bengali font unavailable')
 }
 private resize(){const r=this.host.getBoundingClientRect();this.canvas.width=Math.round(r.width);this.canvas.height=Math.round(r.height);if(this.media)this.draw()}
 private async position(v:HTMLVideoElement,t:number){
  if(Math.abs(v.currentTime-t)<.002&&v.readyState>=2)return
  await new Promise<void>((resolve,reject)=>{
   const timer=setTimeout(()=>{cleanup();reject(new Error('Video seek timed out'))},15000)
   const cleanup=()=>{clearTimeout(timer);v.removeEventListener('seeked',done);v.removeEventListener('error',error)}
   const done=()=>{cleanup();resolve()};const error=()=>{cleanup();reject(new Error('Video seek failed'))}
   v.addEventListener('seeked',done);v.addEventListener('error',error);v.currentTime=t
  })
  await frame()
 }
 private unlock(){
  try{
   if(!this.audio){
    this.audio=new AudioContext();this.output=this.audio.createMediaStreamDestination()
    const limiter=this.audio.createDynamicsCompressor();limiter.threshold.value=-3;limiter.knee.value=0;limiter.ratio.value=12;limiter.attack.value=.003;limiter.release.value=.1
    limiter.connect(this.audio.destination);limiter.connect(this.output)
    this.scoreGain=this.audio.createGain();this.scoreGain.gain.value=0;this.scoreGain.connect(limiter)
   }
   void this.audio.resume().catch(()=>{})
   if(!this.resonanceConnected&&this.web.audioStream&&this.output){this.audio.createMediaStreamSource(this.web.audioStream).connect(this.output);this.resonanceConnected=true}
  }catch{this.fail('Sound could not start. Try reloading, or use Sound off.')}
 }
 ignite(){if(!this.loaded)return;this.web.ignite();this.unlock()}
 replay(){if(!this.loaded)return;this.cancelRecording?.();this.token++;this.videos.forEach(v=>v.pause());this.media=false;this.canvas.hidden=true;this.web.setSuspended(false);this.time=0;this.advancing=true;this.frames=[];this.mediaFrames=[];this.web.replay();this.unlock();void Promise.all(this.videos.map((v,i)=>this.position(v,clips[i].start))).catch(e=>this.fail(String(e)))}
 private emit(){this.onChange(this.phase,this.playing)}
 private fail(message:string){if(this.disposed)return;this.pause();this.onError(message)}
 private async enterMedia(i:number,play:boolean){
  const id=++this.token;this.media=true;this.advancing=false;this.playing=false;this.web.setSuspended(true)
  const v=this.videos[i];this.videos.forEach(other=>{if(other!==v)other.pause()})
  try{
   await this.position(v,clips[i].start);if(id!==this.token||this.disposed)return
   this.active=i;this.time=clips[i].offset;this.phase=i===0?'catch':'reveal';this.canvas.hidden=false;this.draw();this.emit();this.onProgress(this.time)
   if(play)await this.playMedia()
  }catch(e){this.fail(`The next shot could not start. ${String(e)}`)}
 }
 private async playMedia(){
  const id=this.token
  this.unlock();this.motionConsent=true
  try{if(this.time<HOLD)await this.videos[this.active].play();if(id!==this.token||this.disposed)return;this.playing=true;this.last=performance.now();this.emit()}catch{if(id!==this.token||this.disposed)return;this.playing=false;this.emit();this.onError('Playback was blocked. Reload and press Ignite to allow video playback.')}
 }
 pause(){this.cancelRecording?.();this.token++;this.advancing=false;if(this.media){this.videos.forEach(v=>v.pause());this.playing=false;this.updateAudio();this.emit()}else{if(this.web.snapshot().playing)this.web.toggle();this.playing=false}}
 toggle(){if(!this.loaded)return;this.cancelRecording?.();if(this.time>=30)return this.replay();if(this.media){if(this.playing)this.pause();else void this.playMedia()}else{this.web.toggle();this.unlock()}}
 setSound(value:boolean){this.sound=value;this.web.setSound(value);this.updateAudio()}
 async seek(t:number){
  if(!this.loaded)return
  this.cancelRecording?.()
  const id=++this.token;this.advancing=false;this.playing=false;this.videos.forEach(v=>v.pause());this.time=Math.max(-1,Math.min(30,t));this.media=this.time>=16
  this.web.setSuspended(false);this.web.seek(Math.min(this.time,16))
  // Render the outgoing gateway before freezing it, including on a direct seek.
  if(this.media){await frame();if(id!==this.token)return;this.web.setSuspended(true)}
  this.updateAudio()
  if(this.media){
   const i=this.time<REVEAL?0:1;this.active=i
   try{await this.position(this.videos[i],Math.min(clips[i].duration-.001,clips[i].start+this.time-clips[i].offset));if(id!==this.token)return;this.canvas.hidden=false;this.draw()}catch(e){this.fail(String(e))}
  }else this.canvas.hidden=true
  if(id!==this.token)return
  this.phase=this.time>=30?'complete':this.time>=26?'greeting':this.time>=REVEAL?'reveal':this.time>=16?'catch':this.web.snapshot().phase
  this.emit();this.onProgress(this.time)
 }
 private updateAudio(){
  if(!this.audio||!this.score||!this.scoreGain)return
  const t=Math.max(0,this.time),enabled=this.playing&&t<30
  if(this.scoreSource&&(!enabled||Math.abs(this.audio.currentTime-this.scoreOrigin-t)>.18)){this.scoreSource.stop();this.scoreSource.disconnect();this.scoreSource=undefined}
  if(enabled&&!this.scoreSource){const source=this.audio.createBufferSource();source.buffer=this.score;source.connect(this.scoreGain);source.start(0,t);this.scoreSource=source;this.scoreOrigin=this.audio.currentTime-t}
  this.scoreGain.gain.setTargetAtTime(this.sound&&enabled?1:0,this.audio.currentTime,.012)
 }
 private tick=(now:number)=>{
  if(this.disposed)return
  const dt=now-this.last;this.last=now
  if(this.playing&&!document.hidden){this.frames.push(dt);if(this.frames.length>2400)this.frames.shift();if(this.media)this.mediaFrames.push(dt)}
  if(this.media){
   const v=this.videos[this.active]
   if(this.playing){
    if(this.active===1&&this.time>=HOLD)this.time=Math.min(30,this.time+dt/1000)
    else this.time=Math.min(30,clips[this.active].offset+v.currentTime-clips[this.active].start)
    if(this.time>=30){this.playing=false;this.phase='complete';v.pause();this.emit()}
    else if(v.ended||v.currentTime>=clips[this.active].duration-.001){
     if(this.active===0){this.playing=false;void this.enterMedia(1,true)}
     else{this.time=Math.max(HOLD,this.time);v.pause();if(this.phase!=='greeting'){this.phase='greeting';this.emit()}}
    }else{const phase=this.time>=26?'greeting':this.active===0?'catch':'reveal';if(phase!==this.phase){this.phase=phase;this.emit()}}
   }
   this.draw();this.onProgress(this.time)
  }
  this.updateAudio()
  this.raf=requestAnimationFrame(this.tick)
 }
 /** Same code-rendered composition is displayed and recorded; no baked titles. */
 private draw(){
  const c=this.ctx,w=this.canvas.width,h=this.canvas.height;if(!w||!h)return
  const portrait=w/h<.85,t=this.time,i=this.active,[sx,sy,sw,sh]=clips[i].crop,v=this.videos[i]
  c.clearRect(0,0,w,h)
  const bg=c.createRadialGradient(w*.57,h*.4,0,w*.5,h*.5,w*.85);bg.addColorStop(0,'#17120f');bg.addColorStop(.55,'#080a12');bg.addColorStop(1,'#020305');c.fillStyle=bg;c.fillRect(0,0,w,h)
  if(!portrait&&v.readyState>=2){const a=this.atmosphere.getContext('2d')!;a.drawImage(v,sx,sy,sw,sh,0,0,4,6);c.save();c.globalAlpha=.20;c.drawImage(this.atmosphere,0,0,w,h);c.restore()}
  for(let n=0;n<80;n++){const x=((Math.sin(n*129.7)*43758.5)%1+1)%1*w,y=((Math.sin(n*59.3)*9631.5)%1+1)%1*h;c.fillStyle=`rgba(214,188,135,${.05+(n%5)*.015})`;c.fillRect(x,y,n%7===0?1.5:1,1)}
  const compact=portrait&&w<360
  const title=smooth(24,25,t),reframe=this.reduced?title:smooth(22.8,25.2,t)
  const vh=portrait?Math.min(w*sh/sw,h*.91)*(1-reframe*(compact?.26:.22)):h
  const vw=vh*sw/sh,cx=portrait?w*.47:w*(.5+.19*reframe),y=portrait?h*.028:0,x=cx-vw/2
  if(v.readyState>=2)c.drawImage(v,sx,sy,sw,sh,x,y,vw,vh)
  // Feather only the shot edges into the dark surround, never over the central subject.
  const edge=Math.min(28,vw*.035)
  for(const left of [true,false]){const ex=left?x:x+vw-edge,g=c.createLinearGradient(ex,0,ex+edge,0);g.addColorStop(0,left?'#080a12':'#080a1200');g.addColorStop(1,left?'#080a1200':'#080a12');c.fillStyle=g;c.fillRect(ex,y,edge,vh)}
  if(portrait){const g=c.createLinearGradient(0,y+vh-20,0,y+vh+30);g.addColorStop(0,'#080a1200');g.addColorStop(1,'#080a12');c.fillStyle=g;c.fillRect(x,y+vh-20,vw,50)}
  // A six-frame editorial dissolve softens the format change without adding light.
  if(t<16.2&&this.bridgeReady&&!this.reduced){c.globalAlpha=1-smooth(16,16.2,t);c.drawImage(this.bridge,0,0,w,h);c.globalAlpha=1}
  if(t<24)return
  const tx=portrait?w*.47:w*.26,scale=portrait?w/1080:h/810,ty=portrait?h*(compact?.69:.725):h*.40
  c.save();c.textAlign='center';c.textBaseline='middle'
  const sweep=this.reduced?0:Math.sin((t-24)*.7)*.08
  const gold=c.createLinearGradient(tx-200*scale,ty-50*scale,tx+220*scale,ty+110*scale);gold.addColorStop(0,'#b48a45');gold.addColorStop(.36+sweep,'#f4dc9a');gold.addColorStop(.54+sweep,'#d0a55f');gold.addColorStop(.72+sweep,'#ffe9b0');gold.addColorStop(1,'#99713b')
  c.globalAlpha=title;c.fillStyle=gold;c.shadowColor='#000';c.shadowBlur=4*scale;c.font=`700 ${portrait?90*scale:76*scale}px Cinzel`;c.fillText('SHAKTI',tx,ty)
  c.shadowBlur=0;c.fillStyle='#d9bc7e';c.font=`500 ${19*scale}px Cinzel`;c.fillText('T H E   A W A K E N I N G',tx,ty+55*scale)
  const oy=ty+93*scale;c.strokeStyle='#a47b3d';c.lineWidth=scale*.7;c.beginPath();c.moveTo(tx-95*scale,oy);c.lineTo(tx-12*scale,oy);c.moveTo(tx+12*scale,oy);c.lineTo(tx+95*scale,oy);c.moveTo(tx,oy-5*scale);c.lineTo(tx+5*scale,oy);c.lineTo(tx,oy+5*scale);c.lineTo(tx-5*scale,oy);c.closePath();c.stroke()
  c.globalAlpha=smooth(25.8,26.6,t);c.font=`600 ${portrait?48*scale:38*scale}px "Noto Serif Bengali"`;c.fillStyle='#edcd87';c.fillText('শুভ দুর্গাপূজা',tx,ty+145*scale)
  c.globalAlpha=smooth(26.8,27.6,t);c.font=`400 ${portrait?29*scale:24*scale}px Cinzel`;c.fillStyle='#d8c59f';c.fillText('Happy Durga Puja',tx,ty+205*scale)
  if(!this.reduced)for(let n=0;n<12;n++){const a=(n*2.399+t*.025),r=(145+n*12)*scale;c.globalAlpha=title*.12*(.5+.5*Math.sin(t*.5+n));c.fillStyle='#f1cf86';c.beginPath();c.arc(tx+Math.cos(a)*r,ty+70*scale+Math.sin(a)*r*.6,(n%3+1)*scale*.45,0,Math.PI*2);c.fill()}
  c.restore()
 }
 snapshot(){const quality=this.videos.map(v=>{const q=v.getVideoPlaybackQuality();return {totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames}});return {...this.web.snapshot(),time:this.time,phase:this.phase,playing:this.playing,duration:30,frameMs:[...this.frames],mediaFrameMs:[...this.mediaFrames],media:this.media?{clip:clips[this.active].file,sourceTime:this.videos[this.active].currentTime,readyState:this.videos[this.active].readyState,quality:quality[this.active],scoreGain:this.scoreGain?.gain.value}:null,videoQuality:quality,audioBus:{state:this.audio?.state,sampleRate:this.audio?.sampleRate,baseLatency:this.audio?.baseLatency,outputLatency:this.audio?.outputLatency},recording:this.recording,fonts:document.fonts.check('600 48px "Noto Serif Bengali"','শুভ দুর্গাপূজা')}}
 async record():Promise<Blob>{
  if(this.recording)throw new Error('A recording is already running')
  if(!this.loaded)throw new Error('Wait for the film to finish loading')
  this.recording=true;this.motionConsent=true;this.replay();this.unlock()
  const out=document.createElement('canvas');out.width=this.canvas.width;out.height=this.canvas.height;const ctx=out.getContext('2d')!,stream=out.captureStream(30)
  this.output?.stream.getAudioTracks().forEach(track=>stream.addTrack(track.clone()))
  const mime=['video/webm;codecs=vp9,opus','video/webm;codecs=vp8,opus'].find(type=>MediaRecorder.isTypeSupported(type));if(!mime)throw new Error('This browser cannot record WebM')
  return new Promise<Blob>((resolve,reject)=>{
   const chunks:Blob[]=[];const recorder=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:12000000,audioBitsPerSecond:192000});let raf=0,cancelled=false
   const timer=setTimeout(()=>this.cancelRecording?.(),90000)
   const finish=()=>{clearTimeout(timer);cancelAnimationFrame(raf);stream.getTracks().forEach(track=>track.stop());this.recording=false;this.cancelRecording=undefined}
   this.cancelRecording=()=>{cancelled=true;if(recorder.state!=='inactive')recorder.stop()}
   recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};recorder.onerror=()=>{finish();reject(new Error('Recording failed'))};recorder.onstop=()=>{finish();if(cancelled)reject(new Error('Recording cancelled. Keep playback running without seeking to record the full film.'));else resolve(new Blob(chunks,{type:mime}))}
   const copy=()=>{ctx.drawImage(this.media?this.canvas:this.web.canvas,0,0,out.width,out.height);if(this.time>=30){setTimeout(()=>recorder.stop(),80);return}raf=requestAnimationFrame(copy)}
   recorder.start(200);raf=requestAnimationFrame(copy)
  })
 }
 dispose(){this.cancelRecording?.();this.disposed=true;this.abort.abort();cancelAnimationFrame(this.raf);this.observer.disconnect();document.removeEventListener('visibilitychange',this.visibility);this.host.removeEventListener('pointerup',this.blockEarly,true);this.videos.forEach(v=>{v.pause();v.removeAttribute('src');v.load()});this.urls.forEach(url=>URL.revokeObjectURL(url));void this.audio?.close();this.web.dispose();this.canvas.remove()}
}
