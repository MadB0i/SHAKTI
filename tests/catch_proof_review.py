"""Actual isolated 16–20s readiness renders; does NOT assert that a hand catch succeeds."""
from pathlib import Path
import json,base64
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2c';URL='http://127.0.0.1:5173/evidence/phase2c/proof.html'
report={'method':'Isolated raw-asset WebGL diagnostic, not integrated into active 0–16s film. Native 30fps silent canvas recording, not still-frame animation. No alpha cleanup, finger invention, contact pulse or validated grip.','errors':[],'warnings':[],'frames':{},'performance':{},'checks':[]}
def seek(pg,t):
 pg.evaluate('(t)=>window.__CATCH_PROOF__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');s=pg.evaluate('window.__CATCH_PROOF__.snapshot()');s.pop('frameMs');return s
def freeze_before_screenshot(pg):pg.evaluate('document.querySelectorAll(".note,button").forEach(e=>e.style.visibility="hidden")')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None)
  pg.goto(URL);pg.wait_for_load_state('networkidle');pg.wait_for_function('window.__CATCH_PROOF__?.snapshot().ready',timeout=60000);freeze_before_screenshot(pg)
  report['frames'][name]={}
  for t,label in [(16,'boundary'),(17.35,'silhouette-attempt'),(18.45,'approach'),(19.3,'contact-attempt'),(20,'post-contact-attempt')]:
   s=seek(pg,t);report['frames'][name][label]=s;pg.locator('canvas').screenshot(path=str(OUT/f'{name}-{label}.png'))
   assert not s['gripValidated'] and not s['contactPulse']
  assert report['frames'][name]['contact-attempt']['distance']<1e-6
  # Identical mathematical target at both formats. This only verifies alignment.
  seek(pg,19.3);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-a.png'));seek(pg,16);seek(pg,20);seek(pg,19.3);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-b.png'));assert ImageChops.difference(Image.open(OUT/f'{name}-seek-a.png'),Image.open(OUT/f'{name}-seek-b.png')).getbbox() is None
  report['checks'].append(name+': deterministic alignment target reached; visual grip and pulse deliberately remain unvalidated/off')
  seek(pg,16)
  encoded=pg.evaluate('''async()=>await new Promise((resolve,reject)=>{
   const stream=document.querySelector('canvas').captureStream(30),chunks=[];
   const r=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8',videoBitsPerSecond:7000000});r.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};r.onerror=reject;
   r.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const rd=new FileReader();rd.onload=()=>resolve(rd.result.split(',')[1]);rd.readAsDataURL(new Blob(chunks,{type:'video/webm'}))};r.start(100);window.__CATCH_PROOF__.play();
   const poll=setInterval(()=>{if(window.__CATCH_PROOF__.snapshot().time>=20){clearInterval(poll);setTimeout(()=>r.stop(),180)}},20);
  })''');(OUT/f'{name}-catch-diagnostic.webm').write_bytes(base64.b64decode(encoded))
  # Separate warm measurement excludes capture overhead.
  pg.evaluate('window.__CATCH_PROOF__.replay()');pg.wait_for_function('window.__CATCH_PROOF__.snapshot().time>=20',timeout=15000);s=pg.evaluate('window.__CATCH_PROOF__.snapshot()');f=sorted(s.pop('frameMs'));report['performance'][name]={'frames':len(f),'mean_fps':1000*len(f)/sum(f),'p95_interval_ms':f[int(len(f)*.95)],'renderer':s['renderer'],'draw_calls':s['drawCalls'],'triangles':s['triangles']};pg.close();print(name,'diagnostic rendered and recorded',flush=True)
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
labels=[('silhouette-attempt','17.35s / silhouette unavailable'),('approach','18.45s / Trishul approach'),('contact-attempt','19.30s / alignment, no grip'),('post-contact-attempt','20.00s / catch NOT validated')]
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 tw=720 if name=='desktop' else 360;th=round(h*tw/w);sheet=Image.new('RGB',(tw*2,(th+58)*2),'#11111a');d=ImageDraw.Draw(sheet)
 for i,(label,caption) in enumerate(labels):
  x=i%2*tw;y=i//2*(th+58);im=Image.open(OUT/f'{name}-{label}.png');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+58));d.text((x+10,y+8),caption,font=font,fill='#efdfbe')
 sheet.save(OUT/f'{name}-contact-sheet.png')
(OUT/'review.json').write_text(json.dumps(report,indent=2));print(json.dumps({'checks':report['checks'],'performance':report['performance'],'errors':report['errors'],'warnings':report['warnings']},indent=2));assert not report['errors'],report['errors']
