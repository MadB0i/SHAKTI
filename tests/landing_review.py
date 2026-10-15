"""Rendered landing comparison and native ignition controls; production browser."""
from pathlib import Path
import json,os,sys,hashlib
from playwright.sync_api import sync_playwright,expect
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/landing';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4173');before='--before' in sys.argv
report={'checks':[],'errors':[],'frames':{}}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920),('mobile',390,844)]:
  pg=b.new_page(viewport={'width':w,'height':h},has_touch=name=='mobile');pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle')
  button=pg.get_by_role('button',name='IGNITE THE DIYA' if before else 'IGNITE',exact=True);expect(button).to_be_enabled(timeout=90000);pg.mouse.move(0,0);pg.wait_for_timeout(200);pg.locator('.stage').screenshot(path=str(OUT/f'{"before" if before else "after"}-{name}.png'))
  if before:pg.close();continue
  assert pg.evaluate('window.__SHAKTI__.snapshot().time')==-1
  assert pg.get_by_role('button').count()==1
  assert pg.locator('header,.caption,.final-label,.progress').count()==0
  box=button.bounding_box();assert box['height']>=48 and box['width']>=160
  assert button.evaluate('e=>getComputedStyle(e).cursor')=='pointer'
  assert abs(box['x']+box['width']/2-(pg.locator('.stage').bounding_box()['x']+pg.locator('.stage').bounding_box()['width']/2))<1
  assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth')
  report['frames'][name]={'button':box,'visible_buttons':pg.get_by_role('button').all_text_contents()}
  if name=='desktop':
   button.hover();pg.wait_for_timeout(300);pg.locator('.stage').screenshot(path=str(OUT/'desktop-hover.png'));pg.mouse.move(0,0);button.focus();assert button.evaluate('e=>getComputedStyle(e).outlineStyle')!='none';pg.locator('.stage').screenshot(path=str(OUT/'desktop-focus.png'));pg.keyboard.press('Enter')
  elif name=='portrait':button.focus();pg.keyboard.press('Space')
  else:button.tap()
  pg.wait_for_timeout(250);assert 0<pg.evaluate('window.__SHAKTI__.snapshot().time')<2
  expect(pg.get_by_role('button',name='Switch to widescreen' if name!='desktop' else 'Switch to portrait')).to_be_visible()
  expect(pg.get_by_role('button',name='Pause cinematic')).to_be_visible()
  pg.evaluate('async()=>await window.__SHAKTI__.seek(-1)');pg.get_by_role('button',name='IGNITE',exact=True).click();pg.wait_for_timeout(150);assert pg.evaluate('window.__SHAKTI__.snapshot().playing')
  # Dispatch two clicks before React removes the button; one ignition must survive.
  pg.evaluate('async()=>await window.__SHAKTI__.seek(-1)');button=pg.get_by_role('button',name='IGNITE',exact=True);button.evaluate('e=>{e.click();e.click()}');pg.wait_for_timeout(400);a=pg.evaluate('window.__SHAKTI__.snapshot().time');assert .2<a<2
  pg.evaluate('async()=>await window.__SHAKTI__.seek(-1)');pg.wait_for_timeout(100);canvas=pg.locator('canvas').first;rect=canvas.bounding_box();canvas.click(position={'x':rect['width']*.5,'y':rect['height']*.52});pg.wait_for_timeout(200);assert pg.evaluate('window.__SHAKTI__.snapshot().time')>=0
  pg.evaluate('async()=>await window.__SHAKTI__.seek(30)');pg.get_by_role('button',name='Replay cinematic').click();pg.wait_for_timeout(200);assert 0<=pg.evaluate('window.__SHAKTI__.snapshot().time')<2
  pg.get_by_role('button',name='Pause cinematic').click();a=pg.evaluate('window.__SHAKTI__.snapshot().time');pg.wait_for_timeout(150);assert pg.evaluate('window.__SHAKTI__.snapshot().time')==a
  pg.get_by_role('button',name='Resume cinematic').click();pg.wait_for_timeout(150);assert pg.evaluate('window.__SHAKTI__.snapshot().time')>a
  pg.get_by_role('button',name='Switch to widescreen' if name!='desktop' else 'Switch to portrait').click()
  if name=='desktop':
   pg.evaluate('window.__SHAKTI__.replay()');pg.wait_for_function('window.__SHAKTI__.snapshot().time>=30',timeout=45000)
   assert pg.evaluate('window.__SHAKTI__.snapshot().phase')=='complete';expect(pg.get_by_role('button',name='Replay cinematic')).to_be_visible();report['checks'].append('One actual complete 30-second replay reached the unchanged finale and greeting')
  report['checks'].append(name+': clean landing, native button, focus/keyboard or touch, single ignition, diya picking, replay, pause/resume and aspect control passed');pg.close()
 if not before:
  pg=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000);pg.get_by_role('button',name='IGNITE',exact=True).focus();pg.keyboard.press('Space');pg.wait_for_timeout(100);assert pg.evaluate('window.__SHAKTI__.snapshot().reduced');report['checks'].append('Reduced-motion preference and Space ignition passed');pg.close()
 b.close()
if not before:
 protected=json.loads((OUT/'protected-hashes-before.json').read_text());assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in protected.items());report['checks'].append(f'All {len(protected)} protected cinema source/assets/audio/video/font files unchanged by SHA-256')
 font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  tw=720 if name=='desktop' else 360;th=round(h*tw/w);sheet=Image.new('RGB',(tw*2,th+36),'#0b0b0b');d=ImageDraw.Draw(sheet)
  for i,kind in enumerate(['before','after']):sheet.paste(Image.open(OUT/f'{kind}-{name}.png').resize((tw,th)),(i*tw,36));d.text((i*tw+12,6),kind.upper(),font=font,fill='#e5c990')
  sheet.save(OUT/f'{name}-comparison.jpg')
 (OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not report['errors']
