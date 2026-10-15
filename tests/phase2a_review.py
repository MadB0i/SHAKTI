"""Rendered Phase 2A evidence and Phase 1 image-preservation check."""
import json,os,re
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2a';URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:5173')
def freeze(route):
 response=route.fetch();s=response.text()
 s=s.replace('this.uniforms.uClock.value = clock / 1e3;','this.uniforms.uClock.value = this.elapsed <= 7 ? 10 : clock / 1e3;')
 s=s.replace('Math.sin(clock * 0.014)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.014)').replace('Math.sin(clock * 0.023)','Math.sin((this.elapsed <= 7 ? 10000 : clock) * 0.023)')
 route.fulfill(response=response,body=s)
report={'phase1_image_differences':{},'frames':{},'errors':[],'warnings':[]}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.on('pageerror',lambda e:report['errors'].append(str(e)));pg.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else report['warnings'].append(m.text) if m.type=='warning' else None)
  if ':5173' in URL:pg.route('**/src/cinema/Experience.ts*',freeze)
  pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
  pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10})
  for t,label in [(.8,'flame'),(3.25,'lamps'),(5.1,'formation'),(7,'hero')]:
   pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.wait_for_timeout(1200)
   path=OUT/f'after-{name}-{label}.png';pg.locator('canvas').screenshot(path=str(path))
   diff=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(OUT/f'before-{name}-{label}.png').convert('RGB'))
   report['phase1_image_differences'][f'{name}-{label}']={'different_bbox':diff.getbbox(),'max_channel_difference':max(v[1] for v in diff.getextrema())}
  report['frames'][name]={}
  for t,label in [(7,'hero'),(7.95,'calling'),(8.45,'pre-swap'),(8.505,'swap-before'),(8.52,'masked-swap'),(8.535,'swap-after'),(8.72,'release'),(9.65,'flight-midpoint'),(10.6,'flight-late'),(12,'final')]:
   pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.wait_for_timeout(400)
   pg.locator('.stage').screenshot(path=str(OUT/f'{name}-{label}.png'))
   snap=pg.evaluate('window.__SHAKTI__.snapshot()');snap.pop('frameMs');snap.pop('transitionFrameMs');report['frames'][name][label]=snap
  pg.close()
 pg=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');pg.on('pageerror',lambda e:report['errors'].append(str(e)))
 pg.goto(URL+'/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE THE DIYA',exact=True).click();pg.get_by_role('button',name='Hide controls for capture').click();pg.locator('canvas').click(position={'x':10,'y':10});pg.wait_for_timeout(1200)
 for t,label in [(7,'hero'),(8.52,'swap'),(12,'final')]:
  pg.evaluate('(t)=>window.__SHAKTI__.seek(t)',t);pg.wait_for_timeout(400)
  s=pg.evaluate('window.__SHAKTI__.snapshot()');assert s['reduced'] and s['summoning']['quaternion']==[0,0,0,1]
  pg.locator('.stage').screenshot(path=str(OUT/f'reduced-{label}.png'))
 pg.close()
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',26)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 labels=['hero','masked-swap','flight-midpoint','final'];sheet=Image.new('RGB',(w*2,(h+54)*2),'#17120d');draw=ImageDraw.Draw(sheet)
 for i,label in enumerate(labels):
  x=(i%2)*w;y=(i//2)*(h+54);sheet.paste(Image.open(OUT/f'{name}-{label}.png'),(x,y+54));draw.text((x+24,y+10),label.replace('-',' ').upper(),font=font,fill='#f5e7cc')
 sheet.save(OUT/f'{name}-contact.png')
 labels=['calling','pre-swap','swap-before','masked-swap','swap-after','release','flight-midpoint','final']
 tile_w=720 if name=='desktop' else 390
 tile_h=round(h*tile_w/w);film=Image.new('RGB',(tile_w*4,(tile_h+40)*2),'#17120d');draw=ImageDraw.Draw(film)
 for i,label in enumerate(labels):
  x=i%4*tile_w;y=i//4*(tile_h+40);im=Image.open(OUT/f'{name}-{label}.png');im=im.resize((tile_w,tile_h),Image.Resampling.LANCZOS);film.paste(im,(x,y+40));draw.text((x+12,y+6),label,font=font,fill='#f5e7cc')
 film.save(OUT/f'{name}-handoff-filmstrip.png')
(OUT/'render-review.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'errors':report['errors'],'warnings':report['warnings'],'phase1_differences':report['phase1_image_differences']},indent=2),flush=True)
assert not report['errors'],report['errors']
