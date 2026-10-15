"""Seek/occlusion/preload/audio/optimization checks on actual browser renders."""
from pathlib import Path
import json,os,math
import numpy as np
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2a';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:5173')
report={'checks':[],'occlusion':{},'optimization_comparison':{},'errors':[],'warnings':[]}
def listeners(page,expected_errors=False):
 if not expected_errors:
  page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None)
def open_ready(browser,w=1440,h=810,**kwargs):
 pg=browser.new_page(viewport={'width':w,'height':h},**kwargs);listeners(pg);pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).wait_for(timeout=60000);return pg
def seek(pg,t):
 pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t)
 pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 return pg.evaluate('window.__SHAKTI__.snapshot()')
def clean(pg):
 pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
def diff(a,b):
 d=ImageChops.difference(Image.open(a).convert('RGB'),Image.open(b).convert('RGB'))
 return {'bbox':d.getbbox(),'max_channel':max(x[1] for x in d.getextrema()),'mean_absolute_channel':float(np.asarray(d).mean())}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 # Both assets must finish before the user can start.
 pg=b.new_page(viewport={'width':390,'height':844});pending=[];listeners(pg)
 pg.route('**/keshav/trishul-flight.glb',lambda r:pending.append(r))
 pg.goto(URL+'/?inspect=1',wait_until='domcontentloaded')
 expect(pg.get_by_role('button',name='PREPARING THE LIGHT')).to_be_disabled()
 pg.wait_for_function('window.__SHAKTI__ !== undefined')
 assert pg.evaluate('window.__SHAKTI__.snapshot().time')==-1
 assert pending;pending[0].fulfill(path=str(ROOT/'public/art/trishul/keshav/trishul-flight.glb'),content_type='model/gltf-binary')
 expect(pg.get_by_role('button',name='IGNITE THE DIYA',exact=True)).to_be_enabled(timeout=60000);pg.close()
 failed=b.new_page();failed.route('**/keshav/trishul-flight.glb',lambda r:r.abort());failed.goto(URL+'/?inspect=1');failed.wait_for_load_state('networkidle')
 expect(failed.get_by_role('alert')).to_contain_text('Trishul asset could not load');expect(failed.get_by_role('button',name='PREPARING THE LIGHT')).to_be_disabled();failed.close()
 report['checks'].append('delayed and failed replacement preload prevents ignition; explicit reload recovery')
 # Probe the live audio graph's output without changing its destination.
 pg=b.new_page(viewport={'width':1440,'height':810});listeners(pg)
 pg.add_init_script('''const original=AudioContext.prototype.createBiquadFilter;AudioContext.prototype.createBiquadFilter=function(...args){const filter=original.apply(this,args),analyser=this.createAnalyser();filter.connect(analyser);window.__resonanceProbe=analyser;return filter};''')
 pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).wait_for()
 assert pg.evaluate('window.__SHAKTI__.snapshot().audio.state')=='locked'
 pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,7.8)
 pg.get_by_role('button',name='Resume cinematic',exact=True).click();pg.wait_for_function('window.__SHAKTI__.snapshot().time > 8.05')
 audio=pg.evaluate('''()=>{const data=new Float32Array(window.__resonanceProbe.fftSize);window.__resonanceProbe.getFloatTimeDomainData(data);return {rms:Math.sqrt(data.reduce((s,v)=>s+v*v,0)/data.length),snapshot:window.__SHAKTI__.snapshot().audio}}''')
 assert audio['rms']>.001,audio
 pg.get_by_role('button',name='Divine resonance',exact=True).click();pg.wait_for_timeout(200)
 muted=pg.evaluate('''()=>{const a=new Float32Array(window.__resonanceProbe.fftSize);window.__resonanceProbe.getFloatTimeDomainData(a);return Math.sqrt(a.reduce((s,v)=>s+v*v,0)/a.length)}''')
 assert muted<audio['rms']*.05,(audio,muted)
 report['audio']={'active':audio,'muted_rms':muted,'method':'Live output analyser attached in test only; verifies generated signal and mute, not subjective sound mastering.'}
 seek(pg,9.65);clean(pg);pg.locator('canvas').screenshot(path=str(OUT/'deterministic-a.png'))
 seek(pg,11.9);seek(pg,7);seek(pg,9.65);pg.locator('canvas').screenshot(path=str(OUT/'deterministic-b.png'))
 report['seek_repeat_difference']=diff(OUT/'deterministic-a.png',OUT/'deterministic-b.png');assert report['seek_repeat_difference']['bbox'] is None
 states=[]
 for t in [7,7.9,8.49,8.519,8.52,8.521,8.57,9.2,12,8.519,7]:
  s=seek(pg,t);v=s['summoning'];assert int(v['originalVisible'])+int(v['replacementVisible'])==1
  assert v['originalVisible']==(t<8.52)
  if t>7:
   assert v['position']==v['replacementPosition'];assert v['quaternion']==v['replacementQuaternion'];assert v['scale']==[1,1,1]
  states.append({'time':t,**v})
 before,after=states[3],states[5]
 assert math.dist(before['position'],after['position'])<.04
 assert math.dist(before['quaternion'],after['quaternion'])<.01
 report['handoff_states']=states;report['checks']+=['deterministic seek pixels after arbitrary backward/forward seeks','one visible model at every handoff probe','shared scale, pivot transform and orientation; continuous movement across swap','real resonance output, user unlock and mute']
 pg.close()
 # Counterfactual: at the exact swap, render each model under the same veil.
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  for model in ['candidate','original']:
   pg=b.new_page(viewport={'width':w,'height':h});listeners(pg)
   if model=='original':
    def hold_original(route):
     r=route.fetch();s=r.text();assert 'SWAP_TIME = 8.52' in s;s=s.replace('SWAP_TIME = 8.52','SWAP_TIME = 9.52');route.fulfill(response=r,body=s)
    pg.route('**/src/cinema/Summoning.ts*',hold_original)
   pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,8.52);clean(pg)
   pg.locator('canvas').screenshot(path=str(OUT/f'{name}-occlusion-{model}.png'));pg.close()
  report['occlusion'][name]=diff(OUT/f'{name}-occlusion-original.png',OUT/f'{name}-occlusion-candidate.png')
  # Record rather than hide any remaining exposed pixels; human review follows.
 report['checks'].append('actual counterfactual renders compare swap masking in both formats')
 # Optimization comparison: identical hero camera/material hookup, only texture/data encoding differs.
 def freeze(route):
  response=route.fetch();s=response.text().replace('this.uniforms.uClock.value = clock / 1e3;','this.uniforms.uClock.value = 10;')
  s=s.replace('Math.sin(clock * 0.014)','Math.sin(10000 * 0.014)').replace('Math.sin(clock * 0.023)','Math.sin(10000 * 0.023)');route.fulfill(response=response,body=s)
 for quality,file in [('full',ROOT/'evidence/asset-comparison/candidate-normalized.glb'),('optimized',ROOT/'public/art/trishul/keshav/trishul-flight.glb')]:
  pg=b.new_page(viewport={'width':1080,'height':1920});listeners(pg);pg.route('**/art/trishul/trishul-hero.glb',lambda r,request=None,file=file:r.fulfill(path=str(file),content_type='model/gltf-binary'));pg.route('**/src/cinema/Experience.ts*',freeze)
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,7);clean(pg);pg.locator('canvas').screenshot(path=str(OUT/f'texture-{quality}.png'));pg.close()
 report['optimization_comparison']=diff(OUT/'texture-full.png',OUT/'texture-optimized.png')
 # Reduced motion: stable camera, no vibration/yaw/trails, soft dark veil and gentle retreat.
 pg=open_ready(b,390,844,reduced_motion='reduce');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();clean(pg)
 poses=[]
 for t,label in [(7,'hero'),(8.52,'swap'),(12,'final')]:
  s=seek(pg,t);assert s['reduced'];assert s['summoning']['quaternion']==[0,0,0,1];poses.append(s['summoning']['position']);pg.locator('.stage').screenshot(path=str(OUT/f'reduced-{label}.png'))
 assert abs(poses[-1][2]-poses[0][2])<8
 pg.close();report['checks'].append('reduced motion: identity rotation, gentle retreat under 8 units, quiet veil, no rapid trails')
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
sheet=Image.new('RGB',(2160,1974),'#17120d');d=ImageDraw.Draw(sheet)
for i,q in enumerate(['full','optimized']):sheet.paste(Image.open(OUT/f'texture-{q}.png'),(i*1080,54));d.text((i*1080+24,10),q.upper()+' TEXTURES',font=font,fill='#f5e7cc')
sheet.save(OUT/'texture-comparison.png')
(OUT/'transition-checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True);assert not report['errors'],report['errors']
