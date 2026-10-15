"""The hero must load before ignition; a failed model must be visible to the user."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
url=os.environ.get('SHAKTI_URL','http://127.0.0.1:4173')
out=Path(__file__).resolve().parents[1]/'evidence'/'hero-upgrade'
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    page=browser.new_page(viewport={'width':390,'height':844})
    page.route('**/trishul-hero.glb',lambda route:route.abort())
    page.goto(url+'/?inspect=1');page.wait_for_load_state('networkidle')
    expect(page.get_by_role('alert')).to_contain_text('Trishul asset could not load')
    assert page.evaluate('window.__SHAKTI__.snapshot().time') == -1
    expect(page.get_by_role('button',name='PREPARING THE LIGHT')).to_be_disabled()
    expect(page.get_by_role('button',name='Reload scene')).to_be_visible()
    page.close()
    page=browser.new_page(viewport={'width':390,'height':844})
    page.goto(url+'/?inspect=1');page.wait_for_load_state('networkidle')
    expect(page.get_by_role('button',name='IGNITE THE DIYA',exact=True)).to_be_enabled()
    page.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"')
    page.keyboard.press('r')
    page.wait_for_function('window.__SHAKTI__.snapshot().time < 1')
    browser.close()
    report={'checks':['failed GLB shows a reload message','failed GLB cannot start an incomplete cinematic','successful preload enables ignition','complete sequence and keyboard replay'], 'result':'pass'}
    (out/'loading-checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
