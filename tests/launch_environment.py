from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/launch';URL='http://127.0.0.1:4186/SHAKTI/'
(OUT/'after').mkdir(parents=True,exist_ok=True)
r={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 pg=b.new_page(viewport={'width':768,'height':1024},has_touch=True);bad=[];pg.on('response',lambda response:bad.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
 start=time.monotonic();pg.goto(URL+'?inspect=1');expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=30000)
 r['tablet']={'ready_seconds_local':time.monotonic()-start,'initial_resource_bytes':pg.evaluate('performance.getEntriesByType("resource").reduce((sum,e)=>sum+e.encodedBodySize,0)'),'overflow':pg.evaluate('document.documentElement.scrollWidth>innerWidth'),'failed_requests':bad}
 pg.get_by_role('button',name='IGNITE',exact=True).tap();pg.evaluate('async()=>await window.__SHAKTI__.seek(29.5)');pg.screenshot(path=str(OUT/'after/tablet-greeting.png'))
 cdp=pg.context.new_cdp_session(pg);heaps=[]
 for i in range(5):
  pg.evaluate('()=>window.__SHAKTI__.replay()');pg.wait_for_timeout(200)
  for t in [15.9,16.2,17.6,27.6,30]:pg.evaluate('async t=>await window.__SHAKTI__.seek(t)',t)
  cdp.send('HeapProfiler.collectGarbage');heaps.append(cdp.send('Runtime.getHeapUsage'))
 r['memory']={'method':'Chromium Runtime.getHeapUsage after GC; five replay/seek cycles, not total process or GPU memory','samples':heaps}
 r['media_http']={}
 for path in ['videos/playback/divine-catch.mp4','videos/playback/divine-finale.mp4','media/shakti-film.mp4','audio/shakti-original.m4a','credits.html','social/shakti-social.jpg']:
  response=pg.request.get(URL+path,headers={'Range':'bytes=0-1023'});r['media_http'][path]={'status':response.status,'type':response.headers.get('content-type'),'range':response.headers.get('content-range')};assert response.status in [200,206]
 # The final teaser and small preview must decode too.
 pg.goto((ROOT/'launch-assets/review.html').as_uri());pg.get_by_role('button',name='Play final teaser').click();pg.wait_for_function("document.getElementById('teaser').ended",timeout=15000)
 r['teaser']=pg.locator('#teaser').evaluate('v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error,rate:v.playbackRate})')
 r['gif']=pg.locator('img[src$="gif"]').evaluate('e=>({complete:e.complete,width:e.naturalWidth,height:e.naturalHeight})');pg.close();b.close()
 try:
  w=p.webkit.launch(headless=True);pg=w.new_page(viewport={'width':390,'height':844},has_touch=True);errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  pg.goto(URL+'?inspect=1');pg.wait_for_function("document.querySelector('[role=alert]') || document.querySelector('.ignite:not(:disabled)')",timeout=35000)
  r['webkit']={'engine':w.version,'errors':errors,'actual_safari':False}
  if pg.get_by_role('alert').count():r['webkit']['limitation']=pg.get_by_role('alert').inner_text()
  else:
   pg.get_by_role('button',name='IGNITE',exact=True).tap();pg.evaluate('async()=>await window.__SHAKTI__.seek(26)');pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_function('window.__SHAKTI__.snapshot().time===30',timeout=10000);r['webkit']['finale']=pg.evaluate('window.__SHAKTI__.snapshot()');pg.screenshot(path=str(OUT/'after/webkit-greeting.png'))
  w.close()
 except Exception as e:r['webkit']={'unavailable':str(e),'actual_safari':False}
(OUT/'environment.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
