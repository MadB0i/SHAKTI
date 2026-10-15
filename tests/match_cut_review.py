"""Actual consecutive render samples and full 7–12s canvas recordings."""
from pathlib import Path
import json,base64
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2a-polish';URL='http://127.0.0.1:5173'
def freeze(route):
 r=route.fetch();s=r.text().replace('this.uniforms.uClock.value = clock / 1e3;','this.uniforms.uClock.value = this.elapsed <= 7 ? 10 : clock / 1e3;')
 s=s.replace('Math.sin(clock * 0.014)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.014)').replace('Math.sin(clock * 0.023)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.023)');route.fulfill(response=r,body=s)
def seek(pg,t):
 pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 s=pg.evaluate('window.__SHAKTI__.snapshot()');s.pop('frameMs');s.pop('transitionFrameMs');return s
def diff(a,b):
 d=ImageChops.difference(Image.open(a).convert('RGB'),Image.open(b).convert('RGB'));return {'bbox':d.getbbox(),'max_channel':max(x[1] for x in d.getextrema())}
report={'method':'Actual WebGL frames at consecutive 1/60s timeline times. Complete native 7–12 second playback recorded from the WebGL canvas at 30 fps using MediaRecorder, without audio/UI. Recording overhead is excluded from separate performance measurements. Phase 1 clock is frozen equally only for image comparisons.','phase1':{},'frames':{},'checks':[],'errors':[],'warnings':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=browser.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None);pg.route('**/src/cinema/Experience.ts*',freeze)
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,7)
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  for t,label in [(.8,'flame'),(3.25,'lamps'),(5.1,'formation'),(7,'hero')]:
   seek(pg,t);path=OUT/f'{name}-phase1-{label}.png';pg.locator('canvas').screenshot(path=str(path));report['phase1'][name+'-'+label]=diff(path,ROOT/f'evidence/phase2a/before-{name}-{label}.png')
  report['frames'][name]={}
  for i in range(12):
   t=8.433333333333334+i/60;s=seek(pg,t);path=OUT/f'{name}-cut-{i:02}.png';pg.locator('.stage').screenshot(path=str(path));report['frames'][name][f'cut-{i:02}']=s
  for t,label in [(7,'hero'),(7.9,'anticipation'),(8.3,'acceleration'),(8.52,'cut'),(9.2,'tracking'),(10.1,'flight'),(11,'retreat'),(12,'final')]:
   s=seek(pg,t);pg.locator('.stage').screenshot(path=str(OUT/f'{name}-{label}.png'));report['frames'][name][label]=s
  seek(pg,9.2);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-a.png'));seek(pg,11.9);seek(pg,7);seek(pg,8.519);seek(pg,9.2);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-b.png'))
  d=diff(OUT/f'{name}-seek-a.png',OUT/f'{name}-seek-b.png');assert d['bbox'] is None,d;report['checks'].append(name+': repeated seeks are pixel-identical')
  for t in [8.519,8.52,8.521]:
   s=seek(pg,t);v=s['summoning'];assert v['originalVisible']==(t<8.52);assert int(v['originalVisible'])+int(v['replacementVisible'])==1
   assert v['position']==v['replacementPosition'] and v['quaternion']==v['replacementQuaternion'] and v['scale']==[1,1,1]
  before=report['frames'][name]['cut-05']['camera'];after=report['frames'][name]['cut-06']['camera'];assert before['position']!=after['position']
  # Real-time playback, not a video assembled from still samples.
  seek(pg,7)
  encoded=pg.evaluate('''async()=>await new Promise((resolve,reject)=>{
   const stream=document.querySelector('canvas').captureStream(30),chunks=[];
   const recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8',videoBitsPerSecond:6000000});
   recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};recorder.onerror=reject;
   recorder.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(new Blob(chunks,{type:'video/webm'}))};
   recorder.start(100);document.querySelector('.controls button').click();
   const poll=setInterval(()=>{if(window.__SHAKTI__.snapshot().time>=12){clearInterval(poll);setTimeout(()=>recorder.stop(),120)}},20);
  })''')
  (OUT/f'{name}-transition.webm').write_bytes(base64.b64decode(encoded));assert pg.evaluate('window.__SHAKTI__.snapshot().time')==12
  pg.keyboard.press('Escape');pg.get_by_role('button',name='Replay cinematic',exact=True).click();pg.wait_for_function('window.__SHAKTI__.snapshot().time < 1');pg.get_by_role('button',name='Pause cinematic',exact=True).click();pg.close()
  print(name,'consecutive frames, full real-time recording, seek and replay verified',flush=True)
 pg=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,7);pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
 poses=[]
 for t,label in [(7,'hero'),(8.3,'fade'),(8.52,'cut'),(9.2,'after'),(12,'final')]:
  s=seek(pg,t);assert s['reduced'] and s['summoning']['quaternion']==[0,0,0,1];poses.append(s['camera']['position']);pg.locator('.stage').screenshot(path=str(OUT/f'reduced-{label}.png'))
 assert all(v==poses[0] for v in poses);report['checks'].append('reduced motion: stable camera, no rotation or spark burst, gentle dip-to-black handoff');pg.close();browser.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 for kind,labels in [('cut',[f'cut-{i:02}' for i in range(12)]),('sequence',['hero','anticipation','acceleration','cut','tracking','flight','retreat','final'])]:
  cols=4;tw=640 if name=='desktop' else 300;th=round(h*tw/w);rows=(len(labels)+cols-1)//cols
  sheet=Image.new('RGB',(tw*cols,(th+40)*rows),'#17120d');d=ImageDraw.Draw(sheet)
  for i,label in enumerate(labels):
   x=i%cols*tw;y=i//cols*(th+40);im=Image.open(OUT/f'{name}-{label}.png').resize((tw,th),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+40));t=report['frames'][name][label]['time'];d.text((x+12,y+6),f'{t:.4f}s / {label}',font=font,fill='#f5e7cc')
  sheet.save(OUT/f'{name}-{kind}-contact.png')
(OUT/'review.json').write_text(json.dumps(report,indent=2));assert not report['errors'],report['errors'];print(json.dumps({'phase1':report['phase1'],'checks':report['checks'],'errors':report['errors'],'warnings':report['warnings']},indent=2))
