"""Real Chromium/WebGL verification. Run with the local Vite server running.
Requires Python Playwright and an installed Chromium browser.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

OUT = Path(os.environ.get('SHAKTI_EVIDENCE_DIR', str(Path(__file__).resolve().parents[1] / 'evidence')))
OUT.mkdir(exist_ok=True, parents=True)
URL = os.environ.get('SHAKTI_URL', 'http://127.0.0.1:5173')

with sync_playwright() as p:
    # Windows default headless ANGLE chose SwiftShader. Request the available
    # D3D11 adapter explicitly; the report records the actual selected renderer.
    browser = p.chromium.launch(headless=True, args=['--use-angle=d3d11', '--enable-gpu', '--disable-software-rasterizer'])
    page = browser.new_page(viewport={'width': 1440, 'height': 810}, device_scale_factor=1)
    errors, warnings = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else warnings.append(m.text) if m.type == 'warning' else None)
    page.goto(URL + '/?inspect=1')
    page.wait_for_load_state('networkidle')
    page.wait_for_function('window.__SHAKTI__ !== undefined')
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / 'desktop-initial.png'))
    print('BUTTONS', page.get_by_role('button').all_text_contents())
    assert page.evaluate('window.__SHAKTI__.snapshot().time') == -1, 'Must wait for user ignition'
    page.get_by_role('button', name='IGNITE THE DIYA', exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().time >= .8')
    page.screenshot(path=str(OUT / 'desktop-first-flame.png'))
    page.wait_for_function('window.__SHAKTI__.snapshot().time >= 3.15')
    page.screenshot(path=str(OUT / 'desktop-ignition.png'))
    page.wait_for_function('window.__SHAKTI__.snapshot().time >= 4.6')
    page.screenshot(path=str(OUT / 'desktop-assembly.png'))
    page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    page.wait_for_timeout(1100)
    page.screenshot(path=str(OUT / 'desktop-final.png'))
    # Warm sixteen-second replay without screenshot readbacks, measured separately from evidence.
    page.get_by_role('button', name='Replay cinematic', exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    desktop = page.evaluate('window.__SHAKTI__.snapshot()')
    page.get_by_role('button', name='Replay cinematic', exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().time > .3')
    page.get_by_role('button', name='Pause cinematic', exact=True).click()
    before = page.evaluate('window.__SHAKTI__.snapshot().time')
    page.wait_for_timeout(300)
    assert page.evaluate('window.__SHAKTI__.snapshot().time') == before
    page.get_by_role('button', name='Resume cinematic', exact=True).click()
    page.wait_for_function(f'window.__SHAKTI__.snapshot().time > {before + .2}')
    page.get_by_role('button', name='Switch to portrait').click()
    page.evaluate('window.__SHAKTI__.seek(16)')
    page.wait_for_timeout(1200)
    page.locator('.stage').screenshot(path=str(OUT / 'portrait-desktop.png'))
    page.set_viewport_size({'width': 390, 'height': 844})
    page.wait_for_timeout(400)
    page.evaluate('window.__SHAKTI__.seek(-1)')
    page.wait_for_timeout(1100)
    page.locator('.stage').screenshot(path=str(OUT / 'portrait-initial.png'))
    # Keyboard activation is an equivalent of direct canvas picking.
    page.get_by_role('button', name='IGNITE THE DIYA', exact=True).focus()
    page.keyboard.press('Enter')
    page.wait_for_function('window.__SHAKTI__.snapshot().time >= 3.15')
    page.locator('.stage').screenshot(path=str(OUT / 'portrait-ignition.png'))
    page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    page.wait_for_timeout(1100)
    page.locator('.stage').screenshot(path=str(OUT / 'portrait-final.png'))
    page.get_by_role('button', name='Replay cinematic', exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    portrait = page.evaluate('window.__SHAKTI__.snapshot()')
    page.get_by_role('button', name='Hide controls for capture').click()
    page.locator('canvas').click(position={'x': 15, 'y': 15})
    page.wait_for_timeout(1200)  # Includes the one-second final-label fade.
    page.locator('.stage').screenshot(path=str(OUT / 'portrait-clean.png'))
    page.keyboard.press('Escape')
    expect(page.get_by_role('button', name='Hide controls for capture')).to_be_visible()
    page.get_by_role('button', name='Replay cinematic').focus()
    assert page.get_by_role('button', name='Replay cinematic').evaluate('(e) => getComputedStyle(e).outlineStyle') != 'none'
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Horizontal overflow'
    # A narrow landscape viewport also retains usable controls.
    page.set_viewport_size({'width': 844, 'height': 390})
    page.get_by_role('button', name='Switch to widescreen').click()
    page.wait_for_timeout(300)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT / 'landscape-small.png'))
    # Picking the actual modeled diya starts the same timeline.
    page.set_viewport_size({'width': 1440, 'height': 810})
    page.evaluate('window.__SHAKTI__.seek(-1)')
    page.wait_for_timeout(300)
    page.locator('canvas').click(position={'x': 720, 'y': 400})
    page.wait_for_function('window.__SHAKTI__.snapshot().time >= 0', timeout=3000)
    touch = browser.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, device_scale_factor=2)
    touch.goto(URL + '/?inspect=1'); touch.wait_for_load_state('networkidle')
    rect = touch.locator('canvas').bounding_box()
    touch.touchscreen.tap(rect['x']+rect['width']*.5, rect['y']+rect['height']*.52)
    touch.wait_for_function('window.__SHAKTI__.snapshot().time >= 0', timeout=3000)
    touch.close()
    page.close()
    reduced = browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
    reduced.goto(URL + '/?inspect=1'); reduced.wait_for_load_state('networkidle')
    reduced.get_by_role('button', name='IGNITE THE DIYA', exact=True).click()
    reduced.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    reduced.screenshot(path=str(OUT / 'reduced-motion.png'))
    assert reduced.evaluate('window.__SHAKTI__.snapshot().reduced')
    reduced.close()
    reel = browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
    reel.goto(URL + '/?inspect=1'); reel.wait_for_load_state('networkidle')
    reel.locator('.stage').screenshot(path=str(OUT / 'reel-1080-initial.png'))
    reel.evaluate('window.__SHAKTI__.seek(3.25)'); reel.wait_for_timeout(400)
    reel.locator('.stage').screenshot(path=str(OUT / 'reel-1080-ignition.png'))
    reel.evaluate('window.__SHAKTI__.seek(16)'); reel.wait_for_timeout(1200)
    reel.get_by_role('button', name='Replay cinematic').click()
    reel.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
    full_reel = reel.evaluate('window.__SHAKTI__.snapshot()')
    reel.get_by_role('button', name='Hide controls for capture').click()
    reel.locator('canvas').click(position={'x': 15, 'y': 15})
    reel.wait_for_timeout(1200)
    reel.locator('.stage').screenshot(path=str(OUT / 'reel-1080-final.png'))
    def stats(s):
        for key in ['transitionFrameMs','gatewayFrameMs']:
            measured=sorted(s.pop(key))
            s[key.replace('FrameMs','_performance')]={'frame_count':len(measured),'mean_frame_ms':sum(measured)/len(measured) if measured else None,'p95_frame_ms':measured[min(len(measured)-1,int(len(measured)*.95))] if measured else None,'observed_average_fps':1000*len(measured)/sum(measured) if measured else None}
        frames = sorted(s.pop('frameMs'))
        s['frame_count'] = len(frames)
        if frames:
            s['median_frame_ms'] = frames[len(frames)//2]
            s['p95_frame_ms'] = frames[min(len(frames)-1, int(len(frames)*.95))]
            s['mean_frame_ms'] = sum(frames)/len(frames)
            s['observed_average_fps'] = 1000 / s['mean_frame_ms']
        return s
    report = {'url': URL, 'desktop': stats(desktop), 'portrait': stats(portrait), 'reel_1080': stats(full_reel), 'errors': errors, 'warnings': warnings, 'method': 'Warm sixteen-second replay, no screenshot readbacks or recording during measurement. Separate gateway statistics measure only 12–16 seconds. Headless Chromium on the recorded desktop adapter; portrait is a resized desktop browser, not a physical phone.', 'checks': ['user-gated start', 'sixteen-second completion', 'replay', 'pause/resume', 'keyboard ignition and focus ring', '3D diya picking', 'emulated touch ignition at DPR 2', 'aspect switch', 'clean view and Escape', 'responsive overflow', 'reduced motion', '1080x1920 rendering']}
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    browser.close()
    assert not errors, errors
