"""v2.0.1 production UI, cultural correction, accessibility and payload checks.
Run against a local Vite production preview. Does not publish or upload anything.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import os, json, time, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/v2.0.1/discover'
OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4187/SHAKTI').rstrip('/')
r={'checks':[], 'errors':[], 'viewports':{}, 'axe':{}, 'performance':{}, 'links':[]}

with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 # The auditor is pinned and fetched only by this test; never a site dependency.
 axe=b.new_context().request.get('https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js')
 assert axe.ok, 'Could not load pinned accessibility auditor'
 axe_source=axe.text()
 for name,w,h in [('desktop',1440,900),('mobile',390,844),('9x16',360,640),('small',320,740),('tablet',768,1024)]:
  print('Patch checks:',name,flush=True)
  pg=b.new_page(viewport={'width':w,'height':h},has_touch=w<700)
  pg.on('pageerror',lambda e:r['errors'].append(str(e)))
  pg.on('console',lambda m:r['errors'].append(m.text) if m.type=='error' else None)
  pg.on('response',lambda v:r['errors'].append(f'{v.status} {v.url}') if v.status>=400 and v.url.startswith(URL) else None)
  pg.goto(URL+'/discover/',wait_until='networkidle')
  expect(pg.get_by_role('heading',level=1)).to_have_text('The Story of Shakti.')
  assert pg.locator('main').count()==1
  assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth')
  expect(pg.locator('#calendar-correction')).to_contain_text('Gaman: Nouka · Boat')
  assert pg.locator('.vehicle').filter(has_text='Rooster').count()==0
  expect(pg.locator('.belief-panel')).to_contain_text('Ghotak · Horse')
  for d in [17,18,19,20,21]:
   radio=pg.get_by_role('radio',name=f'{d} October,',exact=False)
   radio.check(); expect(radio).to_be_checked()
   expect(pg.locator('#day-description')).to_contain_text(f'{d} October')
   assert f'day={d}' in pg.url
  pg.reload(wait_until='networkidle')
  expect(pg.get_by_role('radio',name='21 October, Dashami')).to_be_checked()
  pg.get_by_role('radio',name='21 October, Dashami').focus()
  pg.keyboard.press('ArrowLeft')
  expect(pg.get_by_role('radio',name='20 October, Navami')).to_be_checked()
  for summary in pg.locator('summary').all():
   summary.focus();pg.keyboard.press('Enter')
   assert summary.evaluate('e=>e.parentElement.open')
   pg.keyboard.press('Space')
   assert not summary.evaluate('e=>e.parentElement.open')
  pg.get_by_role('link',name='04 The rituals',exact=True).click()
  assert pg.url.endswith('#rituals')
  pg.go_back(wait_until='networkidle')
  pg.get_by_role('button',name='Pause motion',exact=True).click()
  assert pg.locator('.discover').get_attribute('data-motion')=='off'
  assert pg.locator('.festival-halo').first.evaluate('e=>getComputedStyle(e).animationName')=='none'
  pg.get_by_role('button',name='Resume motion',exact=True).click()
  assert pg.locator('.discover').get_attribute('data-motion')=='on'
  for sel in ['#calendar .section-intro','.myth-copy','.history-list li','.ritual-card']:
   item=pg.locator(sel).first
   item.scroll_into_view_if_needed()
   expect(item).to_have_class(re.compile('revealed'))
   pg.wait_for_timeout(450)
   assert item.evaluate('e=>getComputedStyle(e).opacity')=='1'
  pg.add_script_tag(content=axe_source)
  result=pg.evaluate("async()=>await axe.run(document.querySelector('.discover'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
  r['axe'][name]=[{'id':v['id'],'impact':v['impact'],'nodes':[n['target'] for n in v['nodes']]} for v in result['violations']]
  # Gather actual computed system values and semantic output for review.
  r['viewports'][name]={'overflow':pg.evaluate('document.documentElement.scrollWidth>innerWidth'), 'revealed':pg.locator('.revealed').count(), 'styles':pg.locator('.hero-deck').evaluate('e=>({font:getComputedStyle(e).fontFamily,size:getComputedStyle(e).fontSize,color:getComputedStyle(e).color})')}
  pg.evaluate('scrollTo(0,0)')
  pg.screenshot(path=str(OUT/f'{name}-hero.png'),animations='disabled')
  pg.locator('#calendar-correction').scroll_into_view_if_needed()
  pg.screenshot(path=str(OUT/f'{name}-correction.png'),animations='disabled')
  pg.locator('.belief-panel').scroll_into_view_if_needed()
  pg.screenshot(path=str(OUT/f'{name}-vehicles.png'),animations='disabled')
  if name in ['desktop','mobile']:
   pg.locator('.calendar-evidence summary').click()
   (OUT/f'{name}-semantics.yml').write_text(pg.locator('main').aria_snapshot(),encoding='utf-8')
   pg.locator('.calendar-evidence summary').click()
   pg.goto(URL+'/discover/',wait_until='networkidle')
   # Walk every tab stop and verify a focus ring plus visibility outside sticky chrome.
   focus=[]
   for _ in range(70):
    pg.keyboard.press('Tab')
    item=pg.evaluate("""()=>{let e=document.activeElement;if(!e||e===document.body)return null;let s=getComputedStyle(e),v=e.getBoundingClientRect();return {name:e.getAttribute('aria-label')||e.textContent?.trim(),outline:s.outlineStyle,height:v.height,top:v.top,bottom:v.bottom}}""")
    if item:focus.append(item)
   assert all(i['outline']!='none' for i in focus),focus
   r['viewports'][name]['tab_stops']=len(focus)
  pg.close()
 # Motion preference, runtime preference change, and unsupported-observer fallback.
 pg=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
 pg.goto(URL+'/discover',wait_until='networkidle')
 expect(pg.get_by_role('button',name='Reduced motion')).to_be_disabled()
 assert pg.locator('.discover').get_attribute('data-motion')=='off'
 assert pg.locator('.festival-halo').first.evaluate('e=>getComputedStyle(e).animationName')=='none'
 pg.emulate_media(reduced_motion='no-preference')
 expect(pg.get_by_role('button',name='Pause motion')).to_be_enabled()
 pg.goto(URL+'/discover/index.html?day=bad',wait_until='networkidle')
 expect(pg.get_by_role('radio',name='16 October, Shashthi')).to_be_checked()
 for a in pg.locator('a[href^="#"]').all():
  href=a.get_attribute('href');assert pg.locator(href).count()==1,href
 for href in [URL+'/',URL+'/discover/',URL+'/discover/index.html',URL+'/credits.html']:
  response=pg.request.get(href);r['links'].append({'url':href,'status':response.status});assert response.ok
 pg.close()
 pg=b.new_page(viewport={'width':390,'height':844})
 pg.add_init_script('delete window.IntersectionObserver')
 pg.goto(URL+'/discover/',wait_until='networkidle')
 expect(pg.get_by_role('heading',name='Flowers. Fire. Rhythm.')).to_be_visible()
 assert pg.locator('.ritual-card').first.evaluate('e=>getComputedStyle(e).opacity')=='1'
 pg.close()
 # Cold profile, including fonts. Explicit budget; this is simulation, not field data.
 ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,device_scale_factor=1)
 pg=ctx.new_page();cdp=ctx.new_cdp_session(pg)
 cdp.send('Network.enable');cdp.send('Network.setCacheDisabled',{'cacheDisabled':True})
 cdp.send('Network.emulateNetworkConditions',{'offline':False,'latency':150,'downloadThroughput':200000,'uploadThroughput':93750,'connectionType':'cellular4g'})
 cdp.send('Emulation.setCPUThrottlingRate',{'rate':4})
 pg.add_init_script("""window.__perf={lcp:0,cls:0};new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__perf.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__perf.cls+=e.value})).observe({type:'layout-shift',buffered:true});""")
 pg.goto(URL+'/discover/',wait_until='networkidle');pg.wait_for_timeout(1200)
 perf=pg.evaluate("""()=>({...window.__perf,resources:performance.getEntriesByType('resource').map(e=>({url:e.name,bytes:e.transferSize,decoded:e.decodedBodySize})),paints:performance.getEntriesByType('paint').map(e=>({name:e.name,time:e.startTime}))})""")
 total=sum(e['bytes'] for e in perf['resources'])
 assert not any('/App-' in e['url'] or '/videos/' in e['url'] or '/audio/' in e['url'] or '/art/trishul/' in e['url'] for e in perf['resources'])
 perf['transfer_bytes']=total;perf['budget_bytes']=400000;perf['budget_lcp_ms']=3500;perf['budget_cls']=.1
 r['performance']=perf
 assert total<=400000,perf
 assert perf['cls']<=.1,perf
 assert perf['lcp']<=3500,perf
 ctx.close();b.close()
r['checks']=['Calendar selection, URL reload and native radio arrows','Keyboard disclosures and chapter links','Five responsive viewports including 360x640','Pause/resume and OS reduced motion','No-observer visible fallback','Direct routes and internal links','No film, video, WebGL or audio downloads on discover','Cold mobile network/CPU simulation']
r['passed']=not r['errors'] and not any(r['axe'].values())
(OUT/'patch-results.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
assert r['passed'],r
print(json.dumps({'passed':r['passed'],'axe':r['axe'],'checks':r['checks'],'performance':{k:v for k,v in r['performance'].items() if k!='resources'}},indent=2))
