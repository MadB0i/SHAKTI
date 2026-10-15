from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2b'
report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.goto('http://127.0.0.1:5173/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();pg.evaluate('window.__SHAKTI__.seek(7)');pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  report[name]={}
  for t in [7,8.5166667,8.5333333,9.2,11.9833333,12]:
   pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');pg.locator('canvas').screenshot(path=str(OUT/f'before-{name}-{t}.png'));s=pg.evaluate('window.__SHAKTI__.snapshot()');s.pop('frameMs');s.pop('transitionFrameMs');report[name][str(t)]=s
  pg.close()
 b.close()
(OUT/'baseline.json').write_text(json.dumps(report,indent=2));print('Both baseline camera formats captured through 12 seconds')
