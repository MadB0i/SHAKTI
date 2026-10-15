"""Pinned axe-core audit of the local production candidate; no publication."""
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
import json, os

OUT=Path(__file__).resolve().parents[1]/'evidence/v1-preparation/browser'
OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4187/SHAKTI').rstrip('/')
AXE=OUT/'axe-core-4.10.3.min.js'
if not AXE.exists():
    with urlopen('https://cdn.jsdelivr.net/npm/axe-core@4.10.3/axe.min.js',timeout=30) as response:
        AXE.write_bytes(response.read())
results={}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    for name,w,h in [('desktop',1440,900),('mobile',390,844)]:
        page=browser.new_page(viewport={'width':w,'height':h})
        for route in ['discover/','?inspect=1']:
            page.goto(URL+'/'+route);page.wait_for_load_state('networkidle')
            if route.startswith('?'):
                expect(page.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000)
            page.add_script_tag(path=str(AXE))
            audit=page.evaluate('async()=>await axe.run(document)')
            key=f'{name}-{route}'
            results[key]={'violations':[{'id':v['id'],'impact':v['impact'],'description':v['description'],'nodes':[{'target':n['target'],'summary':n['failureSummary']} for n in v['nodes']]} for v in audit['violations']], 'passes':len(audit['passes']),'incomplete':[v['id'] for v in audit['incomplete']]}
            if route.startswith('discover'):
                page.locator('summary').first.click()
                audit=page.evaluate('async()=>await axe.run(document)')
                results[key+'-expanded']={'violations':[{'id':v['id'],'impact':v['impact'],'nodes':[n['target'] for n in v['nodes']]} for v in audit['violations']]}
            else:
                page.evaluate('async()=>await window.__SHAKTI__.seek(30)')
                audit=page.evaluate('async()=>await axe.run(document)')
                results[key+'-finale']={'violations':[{'id':v['id'],'impact':v['impact'],'nodes':[n['target'] for n in v['nodes']]} for v in audit['violations']]}
        page.close()
    browser.close()
(OUT/'accessibility.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
assert all(not r['violations'] for r in results.values()), 'See accessibility.json'
