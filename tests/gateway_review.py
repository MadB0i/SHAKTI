"""Actual browser frames, native real-time recordings and analytic continuity checks."""
from pathlib import Path
import json,base64,os
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2b';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:5173')
def seek(pg,t):
 pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 s=pg.evaluate('window.__SHAKTI__.snapshot()')
 for k in ['frameMs','transitionFrameMs','gatewayFrameMs']:s.pop(k,None)
 return s
def diff(a,b):
 d=ImageChops.difference(Image.open(a).convert('RGB'),Image.open(b).convert('RGB'));return {'bbox':d.getbbox(),'max_channel':max(x[1] for x in d.getextrema())}
report={'errors':[],'warnings':[],'frames':{},'preservation':{},'checks':[]}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=browser.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None)
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click(timeout=60000);seek(pg,12)
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  report['frames'][name]={}
  for t in [8.5166667,8.5333333,9.2,11.9833333,12]:
   seek(pg,t);path=OUT/f'after-{name}-{t}.png';pg.locator('canvas').screenshot(path=str(path));report['preservation'][name+'-'+str(t)]=diff(path,OUT/f'before-{name}-{t}.png')
  for t,label in [(12,'continuity'),(12.0166667,'entry'),(12.5,'cosmic'),(13.3,'approach'),(14.5,'closed'),(15.25,'half-open'),(16,'open')]:
   report['frames'][name][label]=seek(pg,t);pg.locator('.stage').screenshot(path=str(OUT/f'{name}-{label}.png'))
  seek(pg,15.25);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-a.png'));seek(pg,16);seek(pg,7);seek(pg,12);seek(pg,15.25);pg.locator('canvas').screenshot(path=str(OUT/f'{name}-seek-b.png'));assert diff(OUT/f'{name}-seek-a.png',OUT/f'{name}-seek-b.png')['bbox'] is None
  for label in ['closed','half-open','open']:
   s=report['frames'][name][label]['gateway'];assert s['hinges']==[[-9.2,0,-156],[9.2,0,-156]];assert s['doorAngles'][0]==-s['doorAngles'][1]
  assert report['frames'][name]['closed']['gateway']['opening']==0 and report['frames'][name]['open']['gateway']['opening']==1
  report['checks'].append(name+': seek is pixel-identical, hinges fixed and doors move symmetrically from 0 to 78 degrees')
  if not os.environ.get('SHAKTI_STILLS_ONLY'):
   seek(pg,12)
   encoded=pg.evaluate('''async()=>await new Promise((resolve,reject)=>{
    const stream=document.querySelector('canvas').captureStream(30),chunks=[];
    const recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp8',videoBitsPerSecond:7000000});
    recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};recorder.onerror=reject;
    recorder.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(new Blob(chunks,{type:'video/webm'}))};
    recorder.start(100);document.querySelector('.controls button').click();
    const poll=setInterval(()=>{if(window.__SHAKTI__.snapshot().time>=16){clearInterval(poll);setTimeout(()=>recorder.stop(),160)}},20);
   })''');(OUT/f'{name}-gateway.webm').write_bytes(base64.b64decode(encoded))
  pg.close();print(name,'rendered',flush=True)
 browser.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 labels=['continuity','cosmic','approach','closed','half-open','open'];tw=640 if name=='desktop' else 300;th=round(h*tw/w);sheet=Image.new('RGB',(tw*3,(th+40)*2),'#101019');d=ImageDraw.Draw(sheet)
 for i,label in enumerate(labels):
  x=i%3*tw;y=i//3*(th+40);im=Image.open(OUT/f'{name}-{label}.png');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+40));d.text((x+12,y+6),f"{report['frames'][name][label]['time']:.2f}s / {label}",font=font,fill='#f5e7cc')
 sheet.save(OUT/f'{name}-contact.png')
(OUT/'review.json').write_text(json.dumps(report,indent=2));print(json.dumps({'errors':report['errors'],'warnings':report['warnings'],'preservation':report['preservation'],'checks':report['checks']},indent=2));assert not report['errors'],report['errors']
