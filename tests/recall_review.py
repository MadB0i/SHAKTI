"""Actual browser match-cut proof and native 18–21s recordings. No grip simulation."""
from pathlib import Path
import json,base64,os
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/divine-recall';URL='http://127.0.0.1:5173/evidence/divine-recall/proof.html';CUT=19.12
report={'method':'Isolated 18–21s editorial proof. Stationary opaque hero artwork and real 3D framing/halo/stars. The moving GLB is exclusive with the post-cut illustrated Trishul. Native 30fps silent canvas recording; performance measured separately.','errors':[],'warnings':[],'frames':{},'checks':[],'performance':{}}
def seek(pg,t):
 pg.evaluate('(t)=>window.__RECALL_PROOF__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');s=pg.evaluate('window.__RECALL_PROOF__.snapshot()');s.pop('frameMs');return s
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None)
  pg.goto(URL);pg.wait_for_load_state('networkidle');pg.wait_for_function('window.__RECALL_PROOF__?.snapshot().ready',timeout=60000);pg.evaluate('document.querySelectorAll(".note,button").forEach(e=>e.style.visibility="hidden")')
  report['frames'][name]={}
  for t,label in [(16,'boundary'),(18,'approach'),(18.9,'anticipation'),(19.1,'flash-before'),(19.12,'cut'),(19.16,'flash-after'),(19.4,'reveal'),(20.3,'hero'),(21,'final')]:
   s=seek(pg,t);report['frames'][name][label]=s;pg.locator('canvas').screenshot(path=str(OUT/f'{name}-{label}.png'));assert s['movingTrishulVisible']!=(s['heroVisible']);assert s['movingTrishulVisible']!=(s['bakedTrishulVisible'])
  for i in range(12):
   t=CUT-.1+i/60;s=seek(pg,t);report['frames'][name][f'cut-{i:02}']=s;pg.locator('canvas').screenshot(path=str(OUT/f'{name}-cut-{i:02}.png'))
  assert report['frames'][name]['flash-before']['camera']!=report['frames'][name]['cut']['camera']
  seek(pg,20.3);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-a.png'));seek(pg,16);seek(pg,19.119);seek(pg,21);seek(pg,20.3);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-b.png'));assert ImageChops.difference(Image.open(OUT/f'{name}-seek-a.png'),Image.open(OUT/f'{name}-seek-b.png')).getbbox() is None
  report['checks'].append(name+': exclusive model/artwork visibility across cut; camera cut explicit; deterministic seek pixel-identical')
  if not os.environ.get('SHAKTI_STILLS_ONLY'):
   seek(pg,18)
   encoded=pg.evaluate('''async()=>await new Promise((resolve,reject)=>{
    const stream=document.querySelector('canvas').captureStream(30),chunks=[];const r=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8',videoBitsPerSecond:7000000});r.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};r.onerror=reject;
    r.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const rd=new FileReader();rd.onload=()=>resolve(rd.result.split(',')[1]);rd.readAsDataURL(new Blob(chunks,{type:'video/webm'}))};r.start(100);window.__RECALL_PROOF__.play();
    const poll=setInterval(()=>{if(window.__RECALL_PROOF__.snapshot().time>=21){clearInterval(poll);setTimeout(()=>r.stop(),180)}},20);
   })''');(OUT/f'{name}-divine-recall.webm').write_bytes(base64.b64decode(encoded))
   pg.evaluate('window.__RECALL_PROOF__.replay()');pg.wait_for_function('window.__RECALL_PROOF__.snapshot().time>=21',timeout=15000);s=pg.evaluate('window.__RECALL_PROOF__.snapshot()');f=sorted(s.pop('frameMs'));report['performance'][name]={'frames':len(f),'mean_fps':1000*len(f)/sum(f),'p95_interval_ms':f[int(len(f)*.95)],'renderer':s['renderer'],'draw_calls':s['drawCalls'],'triangles':s['triangles']}
  pg.close();print(name,'rendered',flush=True)
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 for kind,labels,cols in [('sequence',['approach','anticipation','cut','reveal','hero','final'],3),('cut',[f'cut-{i:02}' for i in range(12)],4)]:
  tw=640 if name=='desktop' else 320;th=round(h*tw/w);rows=(len(labels)+cols-1)//cols;sheet=Image.new('RGB',(tw*cols,(th+40)*rows),'#101019');d=ImageDraw.Draw(sheet)
  for i,label in enumerate(labels):
   x=i%cols*tw;y=i//cols*(th+40);im=Image.open(OUT/f'{name}-{label}.png');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+40));d.text((x+10,y+7),f"{report['frames'][name][label]['time']:.4f}s / {label}",font=font,fill='#f1dfbe')
  sheet.save(OUT/f'{name}-{kind}-contact.png')
(OUT/'review.json').write_text(json.dumps(report,indent=2));print(json.dumps({'errors':report['errors'],'warnings':report['warnings'],'checks':report['checks'],'performance':report['performance']},indent=2));assert not report['errors'],report['errors']
