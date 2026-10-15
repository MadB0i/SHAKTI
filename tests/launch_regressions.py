from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,time,os
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/launch/after';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4186/SHAKTI')
OUT.mkdir(parents=True,exist_ok=True)
r={'checks':[],'errors':[],'console_errors':[]}
def seek(pg,t):pg.evaluate('async t=>await window.__SHAKTI__.seek(t)',t)
def snap(pg):return pg.evaluate('window.__SHAKTI__.snapshot()')
def openpage(b,**kw):
 pg=b.new_page(**kw);pg.on('pageerror',lambda e:r['errors'].append(str(e)));pg.on('console',lambda m:r['console_errors'].append(m.text) if m.type=='error' else None)
 pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');print('Loaded',kw,flush=True);expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000);return pg
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,900),('mobile',390,844)]:
  pg=openpage(b,viewport={'width':w,'height':h},has_touch=name=='mobile')
  assert pg.get_by_role('button').count()==1
  btn=pg.get_by_role('button',name='IGNITE',exact=True);btn.focus();assert btn.evaluate('e=>getComputedStyle(e).outlineStyle')!='none'
  if name=='mobile':btn.tap()
  else:pg.keyboard.press('Enter')
  pg.wait_for_function('window.__SHAKTI__.snapshot().time>.2')
  pg.mouse.move(0,0);pg.wait_for_timeout(2400)
  assert pg.locator('.stage').evaluate("e=>e.classList.contains('chrome-hidden')")
  pg.screenshot(path=str(OUT/f'{name}-unobstructed-playback.png'))
  pg.keyboard.press('Tab');assert pg.locator('.stage').evaluate("e=>!e.classList.contains('chrome-hidden')")
  pg.get_by_role('button',name='Pause cinematic').click();a=snap(pg)['time'];pg.wait_for_timeout(180);assert snap(pg)['time']==a
  pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_function('window.__SHAKTI__.snapshot().time>'+str(a+.1))
  for t in [15.9,16,16.1,17.57,17.6,17.7,27.59,27.6,28.8,29.5,3,17,7,26.7,30]:
   seek(pg,t);s=snap(pg);assert abs(s['time']-t)<.01 and not s['playing']
  pg.get_by_role('button',name='Replay cinematic').click();pg.wait_for_function('window.__SHAKTI__.snapshot().time>.1');assert snap(pg)['time']<2
  seek(pg,18);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(180)
  pg.get_by_role('button',name='Cinematic sound').click();pg.wait_for_timeout(180);s=snap(pg);assert s['media']['scoreGain']<.001
  pg.get_by_role('button',name='Cinematic sound').click();pg.wait_for_timeout(180);assert snap(pg)['media']['scoreGain']>.1
  pg.get_by_role('button',name='Pause cinematic').click();a=snap(pg)['time'];pg.wait_for_timeout(180);assert abs(snap(pg)['time']-a)<.001
  # Multiple synchronous seek requests must leave the final requested shot active.
  pg.evaluate('async()=>await Promise.all([window.__SHAKTI__.seek(17),window.__SHAKTI__.seek(5),window.__SHAKTI__.seek(29)])');assert snap(pg)['time']==29
  pg.get_by_role('slider',name='Film position in seconds').fill('20');pg.wait_for_function('window.__SHAKTI__.snapshot().time===20')
  pg.get_by_role('button',name='Resume cinematic').click();pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))");assert not snap(pg)['playing']
  pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false})")
  seek(pg,29.5);assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth')
  r[name+'-layout']=pg.locator('.controls button').evaluate_all('es=>es.map(e=>({text:e.textContent,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))')
  assert all(e['height']>=44 and e['width']>=44 for e in r[name+'-layout'])
  pg.get_by_role('button',name='Hide controls for capture').click();pg.keyboard.press('Escape');expect(pg.get_by_role('button',name='Hide controls for capture')).to_be_focused()
  seek(pg,28);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(250);assert snap(pg)['time']>28.1
  pg.get_by_role('button',name='Pause cinematic').click();frozen=snap(pg)['time'];pg.wait_for_timeout(150);assert snap(pg)['time']==frozen
  pg.get_by_role('button',name='Toggle fullscreen').click();pg.wait_for_function('!!document.fullscreenElement');pg.get_by_role('button',name='Toggle fullscreen').click();pg.wait_for_function('!document.fullscreenElement')
  seek(pg,30);pg.evaluate('''()=>{window.sharedUrl='';Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{window.sharedUrl=data.url}})}''');pg.get_by_role('button',name='Share SHAKTI').click();assert pg.evaluate('window.sharedUrl')==URL+'/'
  pg.evaluate('''()=>{Object.defineProperty(navigator,'share',{configurable:true,value:undefined});Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async()=>{throw new Error('denied')}}})}''');pg.get_by_role('button',name='Share SHAKTI').click();expect(pg.get_by_label('Copy the experience link')).to_have_value(URL+'/');pg.get_by_role('button',name='Close',exact=True).click()
  r['checks'].append(name+': hold pause/resume, fullscreen, native share payload and denied-clipboard copy fallback passed')
  seek(pg,-1);pg.get_by_role('button',name='IGNITE',exact=True).evaluate('e=>{e.click();e.click()}');pg.wait_for_timeout(200);assert 0<snap(pg)['time']<1
  seek(pg,-1);pg.wait_for_timeout(80);box=pg.locator('canvas').first.bounding_box();pg.locator('canvas').first.click(position={'x':box['width']*.5,'y':box['height']*.52});pg.wait_for_function('window.__SHAKTI__.snapshot().time>=0')
  r['checks'].append(name+': native IGNITE, keyboard/touch, double-click, diya picking, HUD focus restore, WebGL/video pause/resume, bidirectional/racing seeks, mute gain, hidden-tab pause, replay and framing passed')
  (OUT/'regressions.json').write_text(json.dumps(r,indent=2));pg.close()
 pg=openpage(b,viewport={'width':390,'height':844},reduced_motion='reduce');pg.get_by_role('button',name='IGNITE',exact=True).click();seek(pg,15.9);pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_function('window.__SHAKTI__.snapshot().time===16');assert not snap(pg)['playing'];pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_function('window.__SHAKTI__.snapshot().time>16.1');r['checks'].append('Reduced motion: static WebGL camera and explicit video consent at 16s');pg.close()
 for error,handler in [('HTTP 503',lambda route:route.fulfill(status=503,body='Unavailable')),('damaged video',lambda route:route.fulfill(status=200,content_type='video/mp4',body='invalid video'))]:
  pg=b.new_page();pg.route('**/videos/playback/divine-catch.mp4',handler);pg.goto(URL+'/');pg.get_by_role('alert').wait_for(timeout=30000);assert pg.get_by_role('button',name='IGNITE',exact=True).is_disabled();expect(pg.get_by_role('button',name='Reload scene')).to_be_visible();pg.screenshot(path=str(OUT/('error-'+error.replace(' ','-')+'.png')));r['checks'].append(error+': readable recovery and disabled ignition');pg.close()
 # Delayed delivery: it remains the single minimal landing action, safely disabled.
 pg=b.new_page();routes=[];pg.route('**/videos/playback/divine-catch.mp4',lambda route:routes.append(route));pg.goto(URL+'/',wait_until='domcontentloaded');pg.wait_for_function("document.querySelector('.ignite')!==null");expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_disabled();pg.wait_for_timeout(1500);assert not pg.get_by_role('alert').count();routes[0].continue_();expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=30000);r['checks'].append('Delayed video: stable minimal landing, disabled IGNITE, recovery when delivered');pg.close()
 b.close()
 edge=p.chromium.launch(channel='msedge',headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer']);pg=openpage(edge,viewport={'width':1440,'height':810});pg.get_by_role('button',name='IGNITE',exact=True).click();started=time.monotonic();pg.wait_for_function('window.__SHAKTI__.snapshot().time===30',timeout=45000);s=snap(pg);a=sorted(s['frameMs']);r['edge']={'version':edge.version,'wall_seconds':time.monotonic()-started,'fps':1000*len(a)/sum(a),'p95_ms':a[int(len(a)*.95)],'videoQuality':s['videoQuality'],'renderer':s['renderer']};r['checks'].append('Installed Edge: uninterrupted full 1x playback completed');pg.close();edge.close()
(OUT/'regressions.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert not r['errors'] and not r['console_errors']
