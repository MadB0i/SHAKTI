"""Public listing inspection only. No authentication, purchases or model downloads."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/character-asset-gate'
pages=[
 ('durga-nioma','https://sketchfab.com/3d-models/hindu-goddess-durga-cbfb01cfed7645c99876748b6492e4bd'),
 ('lion-lehipo','https://sketchfab.com/3d-models/royal-lion-realistic-3d-character-52c58169b3354c02a66008ed3a98309e'),
 ('durga-cgtrader','https://www.cgtrader.com/3d-models/various/various-models/durga-statue-model'),
 ('lion-promax','https://www.promax3d.com/products/lion-3d-model-rigged'),
 ('lion-promax-pbr','https://www.promax3d.com/products/game-ready-lion-3d-model-pbr'),
 ('durga-sukanta','https://sukantamondal.artstation.com/projects/5enRXz'),
 ('durga-keshto','https://www.fab.com/listings/5d92c928-9d3f-41f1-8c88-f5b2758783c0'),
]
report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,url in pages:
  pg=b.new_page(viewport={'width':1440,'height':1000});entry={'url':url,'errors':[]}
  try:
   r=pg.goto(url,wait_until='domcontentloaded',timeout=45000);entry['status']=r.status if r else None
   try:pg.wait_for_load_state('networkidle',timeout=15000)
   except Exception:pass
   entry['title']=pg.title();entry['body']=pg.locator('body').inner_text(timeout=5000)[:24000]
   entry['images']=pg.locator('img').evaluate_all('(xs)=>xs.map(x=>({alt:x.alt,src:x.currentSrc,width:x.naturalWidth,height:x.naturalHeight})).filter(x=>x.width>400&&x.height>200).slice(0,35)')
   pg.screenshot(path=str(OUT/f'{name}-listing.png'))
   entry['links']=pg.locator('a').evaluate_all('(xs)=>xs.map(x=>({text:x.innerText,url:x.href})).filter(x=>/download|license|buy/i.test(x.text)).slice(0,20)')
  except Exception as e:entry['errors'].append(str(e))
  report[name]=entry;pg.close();(OUT/'market-pages.json').write_text(json.dumps(report,indent=2));print(name,entry.get('status'),entry.get('title'),flush=True)
 b.close()
