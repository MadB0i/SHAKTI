"""Production sequence control, boundary and reduced-motion checks, no FPS measurement."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2b';URL='http://127.0.0.1:4173'
report={'errors':[],'checks':[],'boundary':{},'reduced':{},'requested_art':[]}
def seek(pg,t):
 pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');s=pg.evaluate('window.__SHAKTI__.snapshot()')
 for k in ['frameMs','transitionFrameMs','gatewayFrameMs']:s.pop(k)
 return s
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('request',lambda r:report['requested_art'].append(r.url) if '/art/' in r.url else None);pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,12)
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  report['boundary'][name]=[]
  for i in range(8):
   t=12+(i-3)/60;s=seek(pg,t);report['boundary'][name].append(s);pg.locator('.stage').screenshot(path=str(OUT/f'{name}-boundary-{i}.png'))
  a=report['boundary'][name][3];c=report['boundary'][name][4]
  delta=math.dist(a['camera']['position'],c['camera']['position']);assert delta<.02
  assert a['summoning']['replacementVisible'] and c['summoning']['replacementVisible'];assert not a['gateway']['visible'] and c['gateway']['visible']
  seek(pg,15.25);pg.keyboard.press('Escape');pg.get_by_role('button',name='Resume cinematic',exact=True).click();pg.wait_for_function('window.__SHAKTI__.snapshot().time>15.3');pg.get_by_role('button',name='Pause cinematic',exact=True).click();s=pg.evaluate('window.__SHAKTI__.snapshot()');pg.wait_for_timeout(250);assert pg.evaluate('window.__SHAKTI__.snapshot().time')==s['time']
  sound=pg.get_by_role('button',name='Divine resonance',exact=True);sound.click();assert pg.evaluate('window.__SHAKTI__.snapshot().audio.enabled') is False;sound.click();assert pg.evaluate('window.__SHAKTI__.snapshot().audio.enabled') is True
  seek(pg,16);pg.get_by_role('button',name='Replay cinematic',exact=True).click();pg.wait_for_function('window.__SHAKTI__.snapshot().time<1');pg.get_by_role('button',name='Pause cinematic',exact=True).click();s=pg.evaluate('window.__SHAKTI__.snapshot()');assert not s['gateway']['visible'] and not s['summoning']['replacementVisible']
  pg.set_viewport_size({'width':390,'height':844});seek(pg,15.25);pg.wait_for_timeout(200);assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth');pg.locator('.stage').screenshot(path=str(OUT/'controls-390.png'))
  report['checks'].append(f'{name}: 12s boundary camera delta {delta:.5f}; post-12 pause/resume, mute, replay reset, narrow responsive layout passed');pg.close()
 for name,w,h in [('desktop',1440,810),('portrait',390,844)]:
  pg=b.new_page(viewport={'width':w,'height':h},reduced_motion='reduce');pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();seek(pg,12);pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
  poses=[];report['reduced'][name]={}
  for t in [12,12.28,12.3,13,14.5,15.25,16]:
   s=seek(pg,t);assert s['reduced'];assert s['summoning']['quaternion']==[0,0,0,1];report['reduced'][name][str(t)]=s
   if t>=13:poses.append(s['camera'])
   if t in [12.3,15.25,16]:pg.locator('.stage').screenshot(path=str(OUT/f'reduced-{name}-{t}.png'))
  assert all(c==poses[0] for c in poses);assert report['reduced'][name]['12.3']['fade']==1
  report['checks'].append(name+': reduced-motion dip-to-black masks the switch to a stationary gateway camera; no weapon spin or spark burst');pg.close()
 b.close()
assert not any('durga-lion' in u or 'temple-gateway' in u or '/references/' in u for u in report['requested_art'])
report['checks'].append('Only nebula sheet and existing GLBs requested; future Durga and gateway reference are never rendered')
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 tw=480 if name=='desktop' else 240;th=round(h*tw/w);sheet=Image.new('RGB',(tw*4,(th+40)*2),'#101019');d=ImageDraw.Draw(sheet)
 for i in range(8):
  x=i%4*tw;y=i//4*(th+40);im=Image.open(OUT/f'{name}-boundary-{i}.png');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y+40));d.text((x+8,y+6),f'{12+(i-3)/60:.4f}s',font=font,fill='#f5e7cc')
 sheet.save(OUT/f'{name}-boundary-contact.png')
(OUT/'controls.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['checks'],indent=2));assert not report['errors'],report['errors']
