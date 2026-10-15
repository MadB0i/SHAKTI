"""Pixel verification of the unchanged opening shots, with frozen comparison clock."""
from pathlib import Path
import json
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2b'
def freeze(route):
 r=route.fetch();s=r.text().replace('this.uniforms.uClock.value = clock / 1e3;','this.uniforms.uClock.value = this.elapsed <= 7 ? 10 : clock / 1e3;')
 s=s.replace('Math.sin(clock * 0.014)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.014)').replace('Math.sin(clock * 0.023)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.023)');route.fulfill(response=r,body=s)
report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.route('**/src/cinema/Experience.ts*',freeze);pg.goto('http://127.0.0.1:5173/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();pg.evaluate('window.__SHAKTI__.seek(16)')
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  for t,label in [(.8,'flame'),(3.25,'lamps'),(5.1,'formation'),(7,'hero')]:
   pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');path=OUT/f'{name}-preserved-{label}.png';pg.locator('canvas').screenshot(path=str(path));d=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(ROOT/f'evidence/phase2a-polish/{name}-phase1-{label}.png').convert('RGB'));report[name+'-'+label]={'bbox':d.getbbox(),'max_channel':max(x[1] for x in d.getextrema())};assert report[name+'-'+label]['max_channel']<=1
  pg.close()
 b.close()
(OUT/'preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
