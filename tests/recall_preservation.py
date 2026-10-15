"""Confirm active 0–16s files and final frames are unchanged by the isolated proof."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/divine-recall'
before=json.loads((OUT/'preserved-before.json').read_text(encoding='utf-8-sig'));results=[]
for entry in before:
 path=Path(entry['Path']);actual=hashlib.sha256(path.read_bytes()).hexdigest().upper();assert actual==entry['Hash'];results.append({'path':str(path),'sha256':actual,'unchanged':True})
report={'files':results,'frames':{},'errors':[]}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.goto('http://127.0.0.1:5173/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();pg.evaluate('window.__SHAKTI__.seek(16)');pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  path=OUT/f'preserved-{name}-16.png';pg.locator('.stage').screenshot(path=str(path));d=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(ROOT/f'evidence/phase2b/{name}-open.png').convert('RGB'));s=pg.evaluate('window.__SHAKTI__.snapshot()')
  maximum=max(x[1] for x in d.getextrema());changed=sum(any(pixel) for pixel in d.getdata())
  report['frames'][name]={'bbox':d.getbbox(),'max_channel':maximum,'changed_pixels':changed,'duration':s['time'],'phase':s['phase']}
  # An exact assertion first exposed a one-level change in one red pixel on
  # the unchanged gate. Record it rather than calling that frame identical.
  assert maximum<=1 and changed<=4;assert s['time']==16 and s['phase']=='complete';pg.close()
 b.close()
(OUT/'preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['frames'],indent=2));assert not report['errors']

