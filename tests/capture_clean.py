"""Recapture only the clean final frames after the known UI fade."""
from pathlib import Path
from playwright.sync_api import sync_playwright
out = Path(__file__).resolve().parents[1] / 'evidence'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--use-angle=d3d11', '--enable-gpu', '--disable-software-rasterizer'])
    for name, w, h in [('portrait-clean.png', 390, 844), ('reel-1080-final.png', 1080, 1920)]:
        page = browser.new_page(viewport={'width': w, 'height': h})
        page.goto('http://127.0.0.1:4173/?inspect=1'); page.wait_for_load_state('networkidle')
        page.evaluate('window.__SHAKTI__.seek(7)'); page.wait_for_timeout(1200)
        page.get_by_role('button', name='Hide controls for capture').click()
        page.locator('canvas').click(position={'x': 15, 'y': 15})
        page.wait_for_timeout(1200)
        page.locator('.stage').screenshot(path=str(out / name))
        page.close()
    browser.close()
