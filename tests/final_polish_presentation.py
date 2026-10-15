from pathlib import Path
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'evidence/final-polish';r={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 for w in [1440,390]:
  pg=b.new_page(viewport={'width':w,'height':1000});pg.goto((out/'readme-preview.html').as_uri());pg.wait_for_load_state('networkidle');pg.screenshot(path=str(out/f'README-{w}.png'),full_page=True);assert pg.locator('img').evaluate('(e)=>e.complete&&e.naturalWidth===270');pg.close()
 pg=b.new_page(viewport={'width':390,'height':844});pg.goto('http://127.0.0.1:4181/?inspect=1');pg.wait_for_load_state('networkidle');pg.get_by_role('button',name='IGNITE',exact=True).click(timeout=90000);pg.evaluate('async()=>await window.__SHAKTI__.seek(29.5)')
 try:
  pg.add_script_tag(url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js')
  result=pg.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
  r['axe_violations']=[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in result['violations']]
 except Exception as e:r['axe_unavailable']=str(e)
 b.close()
(out/'presentation-checks.json').write_text(json.dumps(r,indent=2));print(r)
