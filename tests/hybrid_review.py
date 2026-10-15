"""Production-browser playback, decoded frame evidence and native audiovisual capture."""
from pathlib import Path
import os,json,base64,time
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/hybrid';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4173')
report={'errors':[],'checks':[],'frames':{},'runtime':{}}
def seek(pg,t):
 pg.evaluate('async t=>await window.__SHAKTI__.seek(t)',t)
 pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 return pg.evaluate('window.__SHAKTI__.snapshot()')
def stats(values):
 a=sorted(values);return {'samples':len(a),'median_ms':a[len(a)//2] if a else None,'p95_ms':a[int(len(a)*.95)] if a else None,'mean_fps':1000/(sum(a)/len(a)) if a else None}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  print('starting',name,flush=True)
  pg=browser.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)))
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE',exact=True).wait_for(state='visible',timeout=90000)
  pg.get_by_role('button',name='IGNITE',exact=True).click(timeout=90000)
  pg.get_by_role('button',name='Hide controls for capture').click();pg.mouse.move(0,0);pg.locator('canvas').first.click(position={'x':5,'y':5})
  report['frames'][name]={}
  for t,label in [(7,'hero'),(15.9667,'gateway'),(16,'cut-in'),(16.1,'catch'),(19.9667,'catch-end'),(20,'finale-in'),(20.1,'finale'),(24.8,'title'),(26.7,'bengali'),(29.5,'greeting'),(30,'final')]:
   s=seek(pg,t);report['frames'][name][label]={k:v for k,v in s.items() if k not in ['frameMs','mediaFrameMs','transitionFrameMs','gatewayFrameMs']}
   pg.locator('.stage').screenshot(path=str(OUT/f'{name}-{label}.png'))
  seek(pg,28.4);pg.locator('.film-canvas').screenshot(path=str(OUT/f'{name}-seek-a.png'));seek(pg,17);seek(pg,6);seek(pg,28.4);pg.locator('.film-canvas').screenshot(path=str(OUT/f'{name}-seek-b.png'))
  assert ImageChops.difference(Image.open(OUT/f'{name}-seek-a.png'),Image.open(OUT/f'{name}-seek-b.png')).getbbox() is None
  report['checks'].append(name+': deterministic decoded-video and title seeking is pixel-identical')
  if not os.environ.get('SHAKTI_STILLS_ONLY'):
   start=time.monotonic()
   encoded=pg.evaluate('''async()=>{const blob=await window.__SHAKTI__.record();return await new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.slice(f.result.indexOf('base64,')+7));f.readAsDataURL(blob)})}''')
   (OUT/f'{name}-complete.webm').write_bytes(base64.b64decode(encoded));wall=time.monotonic()-start
   s=pg.evaluate('window.__SHAKTI__.snapshot()');report['runtime'][name]={'wall_seconds_with_encoding':wall,'timeline':s['time'],'all':stats(s['frameMs']),'video_section':stats(s['mediaFrameMs']),'gpu':s['renderer'],'quality':s['quality'],'media':s['media']}
   assert s['time']==30 and s['phase']=='complete' and not s['playing']
   pg.evaluate('window.__SHAKTI__.replay()');pg.wait_for_function('window.__SHAKTI__.snapshot().time>=30',timeout=45000)
   s=pg.evaluate('window.__SHAKTI__.snapshot()');report['runtime'][name]['warm_without_recording']={'all':stats(s['frameMs']),'video':stats(s['mediaFrameMs']),'gateway':stats(s['gatewayFrameMs']),'quality':s['quality'],'media':s['media']}
  seek(pg,30);pg.keyboard.press('Escape');pg.get_by_role('button',name='Replay cinematic').click();pg.wait_for_timeout(400);assert pg.evaluate('window.__SHAKTI__.snapshot().time')<2
  seek(pg,23);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(400);pg.get_by_role('button',name='Pause cinematic').click();a=pg.evaluate('window.__SHAKTI__.snapshot().time');pg.wait_for_timeout(300);b=pg.evaluate('window.__SHAKTI__.snapshot().time');assert abs(a-b)<.05
  pg.get_by_role('button',name='Cinematic sound').click();assert pg.get_by_role('button',name='Cinematic sound').get_attribute('aria-pressed')=='false'
  pg.get_by_role('slider',name='Film position in seconds').fill('29');pg.wait_for_timeout(200);assert abs(pg.evaluate('window.__SHAKTI__.snapshot().time')-29)<.01
  report['checks'].append(name+': replay, pause/resume, mute, native seeking, clean capture and full completion passed')
  pg.close();print(name,'verified',flush=True)
 pg=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE',exact=True).click(timeout=90000);seek(pg,15.8);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(700);s=pg.evaluate('window.__SHAKTI__.snapshot()');assert s['time']==16 and not s['playing'];pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(300);assert pg.evaluate('window.__SHAKTI__.snapshot().time')>16;report['checks'].append('390×844 reduced motion: explicit consent at video boundary; responsive playback works');pg.close()
 browser.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 labels=['gateway','cut-in','catch-end','finale-in','title','greeting'];tw=480 if name=='desktop' else 270;th=round(h*tw/w);sheet=Image.new('RGB',(tw*3,(th+34)*2),'#0b0c12');d=ImageDraw.Draw(sheet)
 for i,label in enumerate(labels):
  x=i%3*tw;y=i//3*(th+34);sheet.paste(Image.open(OUT/f'{name}-{label}.png').resize((tw,th)),(x,y+34));d.text((x+8,y+5),label,font=font,fill='#e5c990')
 sheet.save(OUT/f'{name}-contact.jpg')
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({'checks':report['checks'],'errors':report['errors'],'runtime':report['runtime']},indent=2));assert not report['errors']
