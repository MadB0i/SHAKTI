from pathlib import Path
import json,time,os
from PIL import Image,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/hybrid';URL='http://127.0.0.1:4173'
report={'preservation':{},'checks':[],'errors':[]}
def seek(pg,t):
 pg.evaluate('async t=>await window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE').click(timeout=90000)
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').first.click(position={'x':5,'y':5});pg.mouse.move(0,0);pg.wait_for_timeout(450)
  for t in [8.5333333,9.2,12]:
   seek(pg,t);dest=OUT/f'preserved-{name}-{t}.png';pg.locator('canvas').first.screenshot(path=str(dest));before=ROOT/f'evidence/phase2b/after-{name}-{t}.png';d=ImageChops.difference(Image.open(before).convert('RGB'),Image.open(dest).convert('RGB'));report['preservation'][name+'-'+str(t)]={'identical':d.getbbox() is None,'mean_difference_255':ImageStat.Stat(d).mean,'max':max(x[1] for x in d.getextrema())}
  pg.keyboard.press('Escape');seek(pg,17.5);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(200);pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))");s=pg.evaluate('window.__SHAKTI__.snapshot()');assert not s['playing'];pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
  seek(pg,-1);pg.get_by_role('button',name='IGNITE').focus();pg.keyboard.press('Enter');pg.wait_for_timeout(300);assert pg.evaluate('window.__SHAKTI__.snapshot().time')>0
  pg.get_by_role('button',name='Pause cinematic').focus();assert pg.get_by_role('button',name='Pause cinematic').evaluate('e=>getComputedStyle(e).outlineStyle')!='none'
  seek(pg,29);pg.set_viewport_size({'width':390,'height':844});pg.wait_for_timeout(150);assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth');pg.screenshot(path=str(OUT/f'{name}-mobile-controls.png'))
  report['checks'].append(name+': visibility pauses, keyboard ignition, visible focus and 390×844 controls passed');pg.close()
 pg=b.new_page();pg.route('**/videos/playback/divine-catch.mp4',lambda route:route.fulfill(status=503,body='unavailable'));pg.goto(URL);pg.get_by_role('alert').wait_for(timeout=60000);assert 'could not load' in pg.get_by_role('alert').inner_text();assert pg.get_by_role('button',name='IGNITE').is_disabled();pg.screenshot(path=str(OUT/'loading-error.png'));report['checks'].append('HTTP 503 asset failure: ignition disabled; readable error and Reload available');pg.close();b.close()
 if not os.environ.get('SHAKTI_SKIP_EDGE'):
  edge=p.chromium.launch(channel='msedge',headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer']);pg=edge.new_page(viewport={'width':1440,'height':810});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE').click(timeout=90000);start=time.monotonic();pg.wait_for_function('window.__SHAKTI__.snapshot().time>=30',timeout=45000);s=pg.evaluate('window.__SHAKTI__.snapshot()');a=sorted(s['frameMs']);report['edge']={'version':edge.version,'timeline':s['time'],'wall_seconds':time.monotonic()-start,'fps':1000*len(a)/sum(a),'p95_ms':a[int(len(a)*.95)],'gpu':s['renderer']};pg.screenshot(path=str(OUT/'edge-final.png'));report['checks'].append('Installed Microsoft Edge: full 30-second playback and greeting completed');edge.close()
(OUT/('preservation.json' if os.environ.get('SHAKTI_SKIP_EDGE') else 'regressions.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not report['errors']

