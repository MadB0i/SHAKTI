"""One bounded, actual-WebGL art-direction comparison. No active asset edits."""
import hashlib
import json
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'evidence/trishul-art-direction'
URL = os.environ.get('SHAKTI_URL','http://127.0.0.1:5173')
PROPOSALS = json.loads((OUT/'proposals.json').read_text())
MODELS = [('baseline','CURRENT / baseline')] + [(p['id'],p['name']) for p in PROPOSALS]

def instrument(route):
    response = route.fetch()
    body = response.text()
    body, n = re.subn(r'this.uniforms.uClock.value = now / 1e3;', 'this.uniforms.uClock.value = 10;', body)
    assert n == 1
    body,n = re.subn(r'Math.sin\(now \* 0.014\) \* 0.65 \+ Math.sin\(now \* 0.023\) \* 0.4', 'Math.sin(10000 * 0.014) * 0.65 + Math.sin(10000 * 0.023) * 0.4', body)
    assert n == 1
    body = body.replace('replay: () => this.replay() };', 'replay: () => this.replay(), closeup: () => { this.auditClose = true; } };')
    body = body.replace('const m = this.motion;', 'const m = this.auditClose ? {x:2.8,y:12.6,z:14,tx:0,ty:11.2,tz:-1.2,fov:37} : this.motion;')
    route.fulfill(response=response,body=body)

def stats(s):
    f=sorted(s.pop('frameMs'))
    s.update(frame_count=len(f),mean_frame_ms=sum(f)/len(f),p95_frame_ms=f[int(len(f)*.95)])
    s['observed_average_fps']=1000/s['mean_frame_ms']
    return s

report={'method':'Identical running SHAKTI application, hold at t=7 and formation at t=5.1; browser-only GLB interception. Original camera/lighting/environment/exposure/bloom unchanged. Equal wall-clock flicker phase for screenshots. Additional equal diagnostic close-up camera. Serial warm full seven-second replays use untouched runtime module and live flicker, with no screenshots during measurement. Desktop GPU, DPR 1, not physical phone tests.', 'models':{}}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    for model,label in MODELS:
        dest=OUT/model;dest.mkdir(exist_ok=True)
        data={'label':label,'performance':{},'errors':[],'warnings':[],'checks':[]}
        report['models'][model]=data
        for framing,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
            page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
            page.on('pageerror',lambda e:data['errors'].append(str(e)))
            page.on('console',lambda m:data['errors'].append(m.text) if m.type=='error' else data['warnings'].append(m.text) if m.type=='warning' else None)
            if model!='baseline':
                page.route('**/art/trishul/trishul-hero.glb',lambda r:r.fulfill(path=str(OUT/f'{model}.glb'),content_type='model/gltf-binary'))
            page.goto(URL+'/?inspect=1');page.wait_for_load_state('networkidle')
            page.get_by_role('button',name='IGNITE THE DIYA',exact=True).wait_for(timeout=60000)
            assert page.evaluate('window.__SHAKTI__.snapshot().time')==-1
            page.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"',timeout=30000)
            page.get_by_role('button',name='Replay cinematic',exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"',timeout=30000)
            data['performance'][framing]=stats(page.evaluate('window.__SHAKTI__.snapshot()'))
            page.get_by_role('button',name='Replay cinematic',exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().time > .2')
            page.get_by_role('button',name='Pause cinematic',exact=True).click()
            t=page.evaluate('window.__SHAKTI__.snapshot().time')
            page.wait_for_timeout(250)
            assert page.evaluate('window.__SHAKTI__.snapshot().time')==t
            page.get_by_role('button',name='Resume cinematic',exact=True).click()
            page.wait_for_function(f'window.__SHAKTI__.snapshot().time > {t+.2}')
            page.route('**/src/cinema/Experience.ts*',instrument)
            page.reload();page.wait_for_load_state('networkidle')
            page.get_by_role('button',name='IGNITE THE DIYA',exact=True).wait_for(timeout=60000)
            page.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
            page.get_by_role('button',name='Hide controls for capture').click()
            page.locator('canvas').click(position={'x':10,'y':10})
            for t,phase in [(5.1,'transformation'),(7,'hold')]:
                page.evaluate('(t)=>window.__SHAKTI__.seek(t)',t)
                page.wait_for_timeout(1200)
                page.locator('.stage').screenshot(path=str(dest/f'{framing}-{phase}.png'))
            if framing=='desktop':
                page.evaluate('window.__SHAKTI__.closeup()');page.wait_for_timeout(400)
                page.locator('.stage').screenshot(path=str(dest/'closeup.png'))
            page.keyboard.press('Escape')
            page.get_by_role('button',name='Hide controls for capture').wait_for(state='visible')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            data['checks'].append(framing+': user gate, replay, pause/resume, completion, clean/Escape, overflow')
            print(model,framing,json.dumps(data['performance'][framing]),flush=True)
            page.close()
        assert not data['errors'],data['errors']
    browser.close()

font_path=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(font_path),28) if font_path.exists() else ImageFont.load_default()
small=ImageFont.truetype(str(font_path),22) if font_path.exists() else ImageFont.load_default()
def labeled(model,frame):
    im=Image.open(OUT/model/f'{frame}.png').convert('RGB')
    tile=Image.new('RGB',(im.width,im.height+66),'#17120d');tile.paste(im,(0,66))
    label=dict(MODELS)[model];ImageDraw.Draw(tile).text((24,14),label,font=font,fill='#f5e7cc')
    return tile

# Each proposal paired directly with a new baseline render, all original scale.
for frame in ['desktop-hold','desktop-transformation','closeup']:
    baseline=labeled('baseline',frame)
    sheet=Image.new('RGB',(baseline.width*2,baseline.height*3),'#17120d')
    for row,(model,_) in enumerate(MODELS[1:]):
        sheet.paste(baseline,(0,row*baseline.height));sheet.paste(labeled(model,frame),(baseline.width,row*baseline.height))
    sheet.save(OUT/f'{frame}-contact.png')
    for model,_ in MODELS[1:]:
        pair=Image.new('RGB',(baseline.width*2,baseline.height),'#17120d');pair.paste(baseline,(0,0));pair.paste(labeled(model,frame),(baseline.width,0));pair.save(OUT/f'{model}-{frame}-pair.png')

portrait=Image.new('RGB',(1080*4,1986),'#17120d')
for i,(model,_) in enumerate(MODELS):portrait.paste(labeled(model,'portrait-hold'),(1080*i,0))
portrait.save(OUT/'portrait-contact.png')
desktop=Image.new('RGB',(2880,1752),'#17120d')
for i,(model,_) in enumerate(MODELS):desktop.paste(labeled(model,'desktop-hold'),(1440*(i%2),876*(i//2)))
desktop.save(OUT/'overview-contact.png')
before=json.loads((OUT/'preservation-before.json').read_text())
after={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in before}
assert before==after,'Active files changed'
(OUT/'preservation-after.json').write_text(json.dumps(after,indent=2))
report['active_files_unchanged']=True
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print('Contact sheets complete. Active GLB, rebuild source and runtime preserved.',flush=True)
