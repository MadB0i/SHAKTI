/** Small user-unlocked resonance cue; no external recording or audio download. */
export class Resonance {
 private context?:AudioContext
 private gain?:GainNode
 private oscillators:OscillatorNode[]=[]
 private enabled=true
 private disposed=false
 private envelope=0
 private capture?:MediaStreamAudioDestinationNode
 unlock(){
  if(this.disposed||!this.enabled)return
  try{
   if(!this.context){
    this.context=new AudioContext();this.gain=this.context.createGain();this.gain.gain.value=0
    const filter=this.context.createBiquadFilter();filter.type='lowpass';filter.frequency.value=240;filter.Q.value=.6;this.gain.connect(filter);filter.connect(this.context.destination)
    this.capture=this.context.createMediaStreamDestination();filter.connect(this.capture)
    for(const [frequency,level] of [[55,.65],[82.5,.24],[110,.11]]){const osc=this.context.createOscillator(),gain=this.context.createGain();osc.type='sine';osc.frequency.value=frequency;gain.gain.value=level;osc.connect(gain);gain.connect(this.gain);osc.start();this.oscillators.push(osc)}
   }
   void this.context.resume().catch(()=>{})
  }catch{/* Graphics remain usable if audio is unavailable or blocked. */}
 }
 setEnabled(enabled:boolean){this.enabled=enabled;if(enabled)this.unlock();this.update(-1,false)}
 update(t:number,playing:boolean){
  const smooth=(a:number,b:number)=>{const p=Math.max(0,Math.min(1,(t-a)/(b-a)));return p*p*(3-2*p)}
  this.envelope=playing&&this.enabled ? .14*smooth(7.3,7.95)*Math.exp(-Math.max(0,t-8.65)*.65)*(1-smooth(11.4,12)) : 0
  if(this.context&&this.gain)this.gain.gain.setTargetAtTime(this.envelope,this.context.currentTime,.025)
 }
 snapshot(){return {enabled:this.enabled,state:this.context?.state??'locked',envelope:this.envelope}}
 get stream(){return this.capture?.stream}
 dispose(){this.disposed=true;this.oscillators.forEach(o=>o.stop());void this.context?.close().catch(()=>{});this.context=undefined}
}
