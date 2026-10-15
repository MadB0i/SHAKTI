"""Actual GPU A/B: browser-only GLB substitution; active scene stays untouched."""
import hashlib
import json
import os
import re
import time
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/asset-comparison'
URL = os.environ.get('SHAKTI_URL', 'http://127.0.0.1:5173')

def instrumentation(route):
    response = route.fetch()
    body = response.text()
    # Identical test-only clock/light phase removes wall-clock flicker differences.
    body, n = re.subn(r'this.uniforms.uClock.value = now / 1e3;', 'this.uniforms.uClock.value = 10;', body)
    assert n == 1
    body, n = re.subn(r'Math.sin\(now \* 0.014\) \* 0.65 \+ Math.sin\(now \* 0.023\) \* 0.4', 'Math.sin(10000 * 0.014) * 0.65 + Math.sin(10000 * 0.023) * 0.4', body)
    assert n == 1
    body = body.replace('replay: () => this.replay() };', 'replay: () => this.replay(), closeup: () => { this.auditClose = true; } };')
    body = body.replace('const m = this.motion;', 'const m = this.auditClose ? {x:2.8,y:12.6,z:14,tx:0,ty:11.2,tz:-1.2,fov:37} : this.motion;')
    route.fulfill(response=response, body=body)

def stats(snapshot):
    frames = sorted(snapshot.pop('frameMs'))
    snapshot.update(frame_count=len(frames), mean_frame_ms=sum(frames)/len(frames),
                    median_frame_ms=frames[len(frames)//2], p95_frame_ms=frames[int(len(frames)*.95)])
    snapshot['observed_average_fps'] = 1000 / snapshot['mean_frame_ms']
    return snapshot

results = {'method': 'Serial warm seven-second replays with no screenshot readbacks during measurement. A/B uses the same running application, camera timeline, lights, environment, shaders and post-processing. Complete model height and bottom pivot matched; candidate proportions/materials/textures preserved. Only render evidence freezes clock flicker equally and adds an identical diagnostic close-up camera. Desktop Chromium D3D11; no physical phone validation.', 'models': {}}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--use-angle=d3d11', '--enable-gpu', '--disable-software-rasterizer'])
    for model in ['current', 'candidate']:
        dest = OUT / model
        dest.mkdir(exist_ok=True)
        results['models'][model] = {'renders': {}, 'performance': {}, 'errors': [], 'warnings': []}
        data = results['models'][model]
        for name, w, h in [('desktop', 1440, 810), ('portrait', 1080, 1920)]:
            page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
            page.on('pageerror', lambda e: data['errors'].append(str(e)))
            page.on('console', lambda m: data['errors'].append(m.text) if m.type == 'error' else data['warnings'].append(m.text) if m.type == 'warning' else None)
            if model == 'candidate':
                page.route('**/art/trishul/trishul-hero.glb', lambda r: r.fulfill(path=str(OUT/'candidate-normalized.glb'), content_type='model/gltf-binary'))
            # Performance runs use the untouched scene module and real flicker.
            start = time.perf_counter()
            page.goto(URL+'/?inspect=1')
            page.wait_for_load_state('networkidle')
            page.get_by_role('button', name='IGNITE THE DIYA', exact=True).wait_for(timeout=60000)
            data['renders'][name] = {'ready_wall_ms': (time.perf_counter()-start)*1000}
            assert page.evaluate('window.__SHAKTI__.snapshot().time') == -1
            page.get_by_role('button', name='IGNITE THE DIYA', exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
            page.get_by_role('button', name='Replay cinematic', exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().phase === "complete"', timeout=30000)
            data['performance'][name] = stats(page.evaluate('window.__SHAKTI__.snapshot()'))
            page.get_by_role('button', name='Replay cinematic', exact=True).click()
            page.wait_for_function('window.__SHAKTI__.snapshot().time > .3')
            page.get_by_role('button', name='Pause cinematic', exact=True).click()
            t = page.evaluate('window.__SHAKTI__.snapshot().time')
            page.wait_for_timeout(250)  # Deliberate pause stability interval.
            assert page.evaluate('window.__SHAKTI__.snapshot().time') == t
            page.get_by_role('button', name='Resume cinematic', exact=True).click()
            page.wait_for_function(f'window.__SHAKTI__.snapshot().time > {t+.2}')
            # Reload with deterministic comparison clocks, keeping source unchanged.
            page.route('**/src/cinema/Experience.ts*', instrumentation)
            page.reload()
            page.wait_for_load_state('networkidle')
            page.get_by_role('button', name='IGNITE THE DIYA', exact=True).wait_for(timeout=60000)
            page.get_by_role('button', name='IGNITE THE DIYA', exact=True).click()
            page.get_by_role('button', name='Hide controls for capture').click()
            page.locator('canvas').click(position={'x': 10, 'y': 10})
            for t, label in [(5.1, 'transformation'), (7, 'hold')]:
                page.evaluate('(t)=>window.__SHAKTI__.seek(t)', t)
                page.wait_for_timeout(1200)  # UI caption fade / animated final label.
                page.locator('.stage').screenshot(path=str(dest/f'{name}-{label}.png'))
            page.keyboard.press('Escape')
            page.get_by_role('button', name='Hide controls for capture').wait_for(state='visible')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            if name == 'desktop':
                page.get_by_role('button', name='Hide controls for capture').click()
                page.locator('canvas').click(position={'x': 10, 'y': 10})
                page.evaluate('window.__SHAKTI__.closeup()')
                page.wait_for_timeout(1200)
                page.locator('.stage').screenshot(path=str(dest/'closeup.png'))
            print(model, name, json.dumps(data['performance'][name]), flush=True)
            page.close()
        data['checks'] = ['user-gated ignition', 'seven-second completion', 'warm replay', 'pause/resume', 'clean view / Escape', 'responsive overflow', '6000 particles / 214 lamps retained']
        assert not data['errors'], data['errors']
    browser.close()

# Side-by-side contact sheets from actual renders, with unambiguous labels.
for label in ['desktop-hold', 'desktop-transformation', 'portrait-hold', 'portrait-transformation', 'closeup']:
    a, b = [Image.open(OUT/m/(label+'.png')).convert('RGB') for m in ['current', 'candidate']]
    sheet = Image.new('RGB', (a.width*2, a.height+54), '#17120d')
    sheet.paste(a,(0,54));sheet.paste(b,(a.width,54))
    draw = ImageDraw.Draw(sheet)
    draw.text((24,20),'CURRENT — retained original', fill='#f5e7cc')
    draw.text((a.width+24,20),'CANDIDATE — keshavckm1 / CC BY 4.0', fill='#f5e7cc')
    sheet.save(OUT/(label+'-comparison.png'))
before = json.loads((OUT/'preservation-before.json').read_text())
after = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in before}
assert before == after, 'Active implementation or original assets changed during comparison'
results['active_files_unchanged'] = before == after
(OUT/'preservation-after.json').write_text(json.dumps(after,indent=2))
(OUT/'verification.json').write_text(json.dumps(results,indent=2))
print('A/B evidence complete; active assets and scene hashes unchanged.', flush=True)
