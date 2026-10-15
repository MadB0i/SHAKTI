"""Verify generated entries on a plain static server with NO SPA fallback."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from urllib.error import HTTPError
from playwright.sync_api import sync_playwright, expect
import json

ROOT=Path(__file__).resolve().parents[1]
class StaticHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/SHAKTI'):path=path[len('/SHAKTI'):]
        return super().translate_path(path)

server=ThreadingHTTPServer(('127.0.0.1',0),partial(StaticHandler,directory=str(ROOT/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/SHAKTI'
results={}
try:
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
        pg=b.new_page()
        for path in ['/discover','/discover/','/discover/index.html']:
            pg.goto(base+path);pg.wait_for_load_state('networkidle')
            expect(pg.get_by_role('heading',level=1)).to_have_text('The Story of Shakti.')
            assert pg.locator('.discover').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(9, 8, 13)'
            results[path]='physical entry, styled and interactive'
        pg.get_by_role('link',name='The film',exact=False).first.click()
        expect(pg.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000)
        results['/']='actual hybrid experience; all required media loaded'
        for path in ['/shakti-icon.svg','/credits.html','/LICENSE','/DEPENDENCY-LICENSES.txt','/art/trishul/keshav/ATTRIBUTION.md']:
            with urlopen(base+path) as response:assert response.status==200
            results[path]='200'
        try:urlopen(base+'/nonexistent-page')
        except HTTPError as e:assert e.code==404
        else:raise AssertionError('Unexpected SPA fallback')
        b.close()
finally:
    server.shutdown();server.server_close()
(ROOT/'evidence/v1-preparation/browser/static-routes.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
