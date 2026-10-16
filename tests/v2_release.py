from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,time,os,subprocess,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/v2/browser';OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4187/SHAKTI').rstrip('/')
r={'errors':[],'http_errors':[],'checks':[],'full_playback':{}}
AUDIT='''(() => {
 const a=window.__audioAudit={starts:[],stops:[],buffers:[],active:new Set(),maxActive:0,meters:[],videoPlays:[]};
 const start=AudioBufferSourceNode.prototype.start, stop=AudioBufferSourceNode.prototype.stop;
 AudioBufferSourceNode.prototype.start=function(...args){ a.active.add(this);a.buffers.push(this.buffer);a.maxActive=Math.max(a.maxActive,a.active.size);a.starts.push({at:this.context.currentTime,offset:args[1]||0,duration:this.buffer?.duration});this.addEventListener('ended',()=>a.active.delete(this));return start.apply(this,args)};
 AudioBufferSourceNode.prototype.stop=function(...args){a.active.delete(this);a.stops.push(this.context.currentTime);return stop.apply(this,args)};
 const connect=AudioNode.prototype.connect;
 AudioNode.prototype.connect=function(dest,...args){const result=connect.call(this,dest,...args);if(dest instanceof AudioDestinationNode){const analyser=this.context.createAnalyser();analyser.fftSize=2048;connect.call(this,analyser);a.meters.push(analyser)}return result};
 a.peak=()=>Math.max(0,...a.meters.map(m=>{const data=new Float32Array(m.fftSize);m.getFloatTimeDomainData(data);return Math.max(...data.map(Math.abs))}));
 const play=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(...args){a.videoPlays.push({muted:this.muted,volume:this.volume});return play.apply(this,args)};
})();'''
def snap(pg):return pg.evaluate('window.__SHAKTI__.snapshot()')
def observe(pg):
 pg.on('pageerror',lambda e:r['errors'].append(str(e)))
 pg.on('console',lambda m:r['errors'].append(m.text) if m.type=='error' else None)
 pg.on('response',lambda resp:r['http_errors'].append(f'{resp.status} {resp.url}') if resp.status>=400 else None)
def openfilm(browser,w,h,touch=False):
 pg=browser.new_page(viewport={'width':w,'height':h},has_touch=touch);observe(pg);pg.add_init_script(AUDIT)
 pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000);return pg
def audit_state(pg):
 s=snap(pg);assert not s['audio']['enabled'] and s['audio']['envelope']==0
 assert abs(s['audioBus']['bufferDuration']-30)<=1/48000+1e-9,s['audioBus']
 a=s['audioBus'];drift=None if a['scoreOffset'] is None else abs(a['scoreOffset']-s['time'])
 assert drift is None or drift<.19,(s['time'],drift)
 return {'film_time':s['time'],'audio_offset':a['scoreOffset'],'drift':drift,'peak':pg.evaluate('window.__audioAudit.peak()')}
with sync_playwright() as p:
 b=p.chromium.launch(channel='msedge',headless=True,ignore_default_args=['--mute-audio'],args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,900),('mobile',390,844)]:
  pg=openfilm(b,w,h,name=='mobile');pg.screenshot(path=str(OUT/f'{name}-landing.png'))
  pg.get_by_role('button',name='IGNITE',exact=True).click();started=time.monotonic();samples=[]
  for cue in [1,4,8,12,15.8,16.1,17.7,20,24,27,29.7,30]:
   pg.wait_for_function('c=>window.__SHAKTI__.snapshot().time>=c',arg=cue,timeout=45000)
   samples.append(audit_state(pg))
  completed=time.monotonic()-started
  s=snap(pg);audit=pg.evaluate('({starts:__audioAudit.starts,stops:__audioAudit.stops,maxActive:__audioAudit.maxActive,videoPlays:__audioAudit.videoPlays})')
  browser_pcm=np.array(pg.evaluate('Array.from(__audioAudit.buffers[0].getChannelData(0).slice(0,96000))'))
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'public/audio/shakti-original.m4a'),'-t','2','-f','f32le','-'])
  reference=np.frombuffer(raw,dtype='<f4').reshape(-1,2)[:,0]
  pcm_corr=float(np.corrcoef(browser_pcm,reference)[0,1]);assert pcm_corr>.9999,pcm_corr
  assert audit['maxActive']==1 and all(v['muted'] and v['volume']==0 for v in audit['videoPlays'])
  assert len(audit['starts'])==1,('Unexpected soundtrack restart during normal playback',audit)
  assert all(q['corruptedVideoFrames']==0 and q['totalVideoFrames']>0 for q in s['videoQuality'])
  r['full_playback'][name]={'wall_seconds':completed,'samples':samples,'audio_audit':audit,'video_quality':s['videoQuality'],'time':s['time'],'decoded_buffer_duration':s['audioBus']['bufferDuration'],'browser_source_first_2s_correlation':pcm_corr,'AAC_rounding_note':'Browser decoder reports one sample less than 30 seconds; film clock and MP4/M4A metadata remain exactly 30 seconds. Opening PCM correlation verifies no inserted start delay.'}
  print('Full playback passed:',name,round(r['full_playback'][name]['wall_seconds'],2),flush=True)
  for cue in [16.1,20,29.7]:
   pg.evaluate('async t=>await __SHAKTI__.seek(t)',cue);pg.screenshot(path=str(OUT/f'{name}-cue-{cue}.png'))
  # Actual audible-output meter checks for the middle and both directions of seeking.
  for t in [3,7,15.9,16.1,18,24,28,6]:
   pg.evaluate('async t=>await __SHAKTI__.seek(t)',t);assert snap(pg)['time']==t and not snap(pg)['playing']
   pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_function('t=>__SHAKTI__.snapshot().time>t+.12',arg=t)
   audit_state(pg);pg.get_by_role('button',name='Pause cinematic').click()
   pg.wait_for_function('!__SHAKTI__.snapshot().audioBus.scorePlaying')
  pg.evaluate('async()=>await __SHAKTI__.seek(8)');pg.get_by_role('button',name='Resume cinematic').click()
  pg.wait_for_function('__audioAudit.peak()>.01');pg.get_by_role('button',name='Cinematic sound').click()
  pg.wait_for_function('__audioAudit.peak()<.0001');assert not snap(pg)['audioBus']['sound']
  pg.get_by_role('button',name='Cinematic sound').click();pg.wait_for_function('__audioAudit.peak()>.01')
  pg.get_by_role('button',name='Pause cinematic').click();frozen=snap(pg)['time'];pg.wait_for_function('__audioAudit.peak()<.0001');assert snap(pg)['time']==frozen
  pg.evaluate('async()=>await __SHAKTI__.seek(30)');pg.get_by_role('button',name='Replay cinematic').click();pg.wait_for_function('__SHAKTI__.snapshot().time>.1');assert snap(pg)['time']<2
  audit_state(pg);assert pg.evaluate('__audioAudit.maxActive')==1
  r['checks'].append(name+': normal full playback, one audio buffer at a time, no resonance output, muted video clips, forward/backward seeks, actual-output mute/unmute, pause silence and replay passed')
  (OUT/'v2-audio-playback.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
  pg.close()
 # Owner-final MP4 plays completely with its embedded audio; no renderer involved.
 pg=b.new_page(viewport={'width':1080,'height':1000});observe(pg)
 pg.goto((ROOT/'docs/media/shakti-cinematic.mp4').as_uri());v=pg.locator('video');v.wait_for();pg.wait_for_function('document.querySelector("video").readyState>=2')
 v.evaluate('v=>{v.currentTime=0;v.muted=false;v.playbackRate=1;return v.play()}');started=time.monotonic()
 pg.wait_for_function('document.querySelector("video").ended',timeout=45000)
 r['owner_movie_playback']=v.evaluate('v=>({duration:v.duration,time:v.currentTime,width:v.videoWidth,height:v.videoHeight,rate:v.playbackRate,muted:v.muted,error:v.error,quality:v.getVideoPlaybackQuality().toJSON?v.getVideoPlaybackQuality().toJSON():{total:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames,corrupted:v.getVideoPlaybackQuality().corruptedVideoFrames}})')
 r['owner_movie_playback']['wall_seconds']=time.monotonic()-started
 assert r['owner_movie_playback']['duration']==30 and not r['owner_movie_playback']['error']
 pg.screenshot(path=str(OUT/'owner-film-complete.png'));pg.close();b.close()
r['passed']=not(r['errors'] or r['http_errors']);(OUT/'v2-audio-playback.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
assert r['passed'],r
print(json.dumps({'passed':r['passed'],'checks':r['checks'],'owner_movie':r['owner_movie_playback']},indent=2))
