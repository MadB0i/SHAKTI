"""Focused screenshots of the actual 3D hero at precise reveal times."""
import os, json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'evidence'/'hero-upgrade'
out.mkdir(exist_ok=True)
url=os.environ.get('SHAKTI_URL','http://127.0.0.1:5173')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    errors=[]
    for name,w,h in [('desktop',1440,900),('portrait',390,844),('reel',1080,1920)]:
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        page.goto(url+'/?inspect=1');page.wait_for_load_state('networkidle')
        page.get_by_role('button',name='IGNITE THE DIYA',exact=True).wait_for()
        page.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
        page.wait_for_function('window.__SHAKTI__.snapshot().time >= .2')
        for t,label in [(5.1,'transformation'),(5.6,'resolve'),(7,'hold')]:
            page.evaluate('(t)=>window.__SHAKTI__.seek(t)',t)
            page.wait_for_timeout(1200)
            page.locator('.stage').screenshot(path=str(out/f'{name}-{label}.png'))
        page.get_by_role('button',name='Hide controls for capture').click()
        page.locator('canvas').click(position={'x':10,'y':10})
        page.wait_for_timeout(1200)
        page.locator('.stage').screenshot(path=str(out/f'{name}-clean.png'))
        print(name,json.dumps(page.evaluate('window.__SHAKTI__.snapshot()'))[:500],flush=True)
        page.close()
    browser.close()
    assert not errors,errors
