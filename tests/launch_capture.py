from pathlib import Path
import os,json,base64
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/launch/after'
URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4185')
OUT.mkdir(parents=True,exist_ok=True)
report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920),('mobile',390,844)]:
  pg=b.new_page(viewport={'width':w,'height':h});errors=[]
  pg.on('pageerror',lambda e: errors.append(str(e)))
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle')
  pg.get_by_role('button',name='IGNITE',exact=True).click(timeout=90000)
  awaitable='async t=>await window.__SHAKTI__.seek(t)'
  if name!='mobile':
   print('Recording full 1x playback',name,flush=True)
   encoded=pg.evaluate('''async()=>{const blob=await window.__SHAKTI__.record();return await new Promise(r=>{const f=new FileReader();f.onload=()=>r(f.result.slice(f.result.indexOf('base64,')+7));f.readAsDataURL(blob)})}''')
   (OUT/f'{name}-complete.webm').write_bytes(base64.b64decode(encoded))
   report[name]=pg.evaluate('window.__SHAKTI__.snapshot()')
  pg.evaluate(awaitable,29.5);pg.screenshot(path=str(OUT/f'{name}-with-controls.png'))
  report[name+'-styles']=pg.evaluate('''()=>({overflow:document.documentElement.scrollWidth>innerWidth,title:getComputedStyle(document.querySelector('h1')).fontSize,controls:getComputedStyle(document.querySelector('.controls')).flexDirection})''')
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').first.click(position={'x':5,'y':5});pg.mouse.move(0,0)
  for t in [0,1,3,5,7,8.5,9,11,12,13,14,15.5,15.967,16,16.2,17,17.567,17.6,17.8,19.6,20.2,21,23.6,24.5,26.7,29.5,30]:
   if name=='mobile' and t not in [0,7,16,17.6,29.5]:continue
   pg.evaluate(awaitable,t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
   pg.locator('.stage').screenshot(path=str(OUT/f'{name}-{t}.png'))
  pg.keyboard.press('Escape');pg.evaluate(awaitable,-1);pg.screenshot(path=str(OUT/f'{name}-landing.png'))
  report[name+'-errors']=errors;pg.close();print('Done',name,flush=True)
 b.close()
(OUT/'playback.json').write_text(json.dumps(report,indent=2))

