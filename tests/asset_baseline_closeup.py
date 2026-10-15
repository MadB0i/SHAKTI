"""Capture a crop of the current real WebGL render; no replacement or image edits."""
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'evidence'/'asset-audit'/'baseline'
out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    page=browser.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1)
    page.goto('http://127.0.0.1:4173/?inspect=1');page.wait_for_load_state('networkidle')
    page.get_by_role('button',name='IGNITE THE DIYA',exact=True).click()
    page.evaluate('window.__SHAKTI__.seek(7)');page.wait_for_timeout(1200)
    page.get_by_role('button',name='Hide controls for capture').click()
    page.locator('canvas').click(position={'x':10,'y':10});page.wait_for_timeout(1200)
    page.screenshot(path=str(out/'current-geometry-closeup.png'),clip={'x':140,'y':170,'width':800,'height':720})
    browser.close()
