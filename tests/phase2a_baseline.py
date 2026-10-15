"""Freeze actual Phase 1 frames before extending the runtime."""
from pathlib import Path
import re,urllib.request
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parents[1]/'evidence/phase2a';URL='http://127.0.0.1:5173'
body=urllib.request.urlopen(URL+'/src/cinema/Experience.ts').read().decode()
(OUT/'rollback/phase1-module.js').write_text(body,encoding='utf-8')
def freeze(route):
 s=body.replace('this.uniforms.uClock.value = now / 1e3;','this.uniforms.uClock.value = 10;')
 s=s.replace('Math.sin(now * 0.014)','Math.sin(10000 * 0.014)').replace('Math.sin(now * 0.023)','Math.sin(10000 * 0.023)')
 route.fulfill(body=s,content_type='application/javascript')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.route('**/src/cinema/Experience.ts*',freeze)
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10})
  for t,label in [(.8,'flame'),(3.25,'lamps'),(5.1,'formation'),(7,'hero')]:
   pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.wait_for_timeout(1200);pg.locator('canvas').screenshot(path=str(OUT/f'before-{name}-{label}.png'))
  pg.close()
 b.close()
print('Frozen Phase 1 visual baselines saved.')
