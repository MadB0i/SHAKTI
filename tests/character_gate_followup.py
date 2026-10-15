"""Read public previews and visible download gates; never bypass login/payment."""
from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/character-asset-gate';report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,uid in [('durga-nioma','cbfb01cfed7645c99876748b6492e4bd'),('lion-lehipo','52c58169b3354c02a66008ed3a98309e')]:
  pg=b.new_page(viewport={'width':1440,'height':1000});pg.goto('https://sketchfab.com/models/'+uid,wait_until='domcontentloaded');pg.wait_for_selector('text=Download 3D Model',timeout=30000)
  report[name]={'license_links':pg.locator('a[href*="creativecommons.org"]').evaluate_all('(xs)=>xs.map(x=>({text:x.innerText,url:x.href}))')}
  pg.get_by_text('Download 3D Model',exact=True).first.click()
  try:pg.locator('[role="dialog"]').first.wait_for(state='visible',timeout=12000)
  except Exception:pass
  report[name]['license_urls']=sorted(set(re.findall(r'https?[^\s\"<>]*creativecommons[^\s\"<>]*',pg.content())))
  pg.screenshot(path=str(OUT/f'{name}-download-gate.png'));report[name]['download_dialog']=pg.locator('body').inner_text()[:15000];pg.close();(OUT/'followup.json').write_text(json.dumps(report,indent=2));print(name,'download gate inspected',flush=True)
 for name,url in [('lion-wildmesh','https://sketchfab.com/3d-models/lion-realistic-3d-model-678e161ce0b44d6cbae5f03bc4541116')]:
  pg=b.new_page(viewport={'width':1440,'height':1000})
  try:
   r=pg.goto(url,wait_until='domcontentloaded',timeout=45000)
   try:pg.wait_for_load_state('networkidle',timeout=10000)
   except Exception:pass
   report[name]={'url':url,'status':r.status if r else None,'body':pg.locator('body').inner_text()[:16000],'images':pg.locator('img').evaluate_all('(xs)=>xs.map(x=>({alt:x.alt,src:x.currentSrc,width:x.naturalWidth,height:x.naturalHeight})).filter(x=>x.width>400&&x.height>200).slice(0,30)')};pg.screenshot(path=str(OUT/f'{name}-listing.png'))
  except Exception as e:report[name]={'error':str(e)}
  pg.close();(OUT/'followup.json').write_text(json.dumps(report,indent=2));print(name,'preview inspected',flush=True)
 # A creator's actual catalogue pictures, not our renders or mesh inspection.
 pg=b.new_page(viewport={'width':1440,'height':1000})
 all_images=json.loads((OUT/'market-pages.json').read_text())['lion-promax']['images']
 for label,term in [('side','side view'),('face','head with polygonal'),('wireframe','Head Close Up With Polygonal Mane Wireframe')]:
  match=next((x for x in all_images if term.lower() in x['alt'].lower()),None)
  if match:
   pg.goto(match['src'],wait_until='load');pg.screenshot(path=str(OUT/f'lion-promax-{label}-catalogue.png'));report['promax-'+label]=match
 pg.close();b.close()
(OUT/'followup.json').write_text(json.dumps(report,indent=2));print('Public inspection complete',flush=True)
