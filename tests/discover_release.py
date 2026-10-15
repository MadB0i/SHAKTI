"""Production-browser checks. Never uploads media or publishes the site."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, os

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/v1-preparation/browser'
OUT.mkdir(parents=True,exist_ok=True)
URL=os.environ.get('SHAKTI_URL','http://127.0.0.1:4187/SHAKTI').rstrip('/')
report={'checks':[],'console_errors':[],'page_errors':[],'http_errors':[],'media':[]}

def observe(page):
    page.on('console',lambda m: report['console_errors'].append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e: report['page_errors'].append(str(e)))
    page.on('response',lambda r: report['http_errors'].append(f'{r.status} {r.url}') if r.status>=400 else None)

def overflow(page):
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), 'horizontal overflow'

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
    for name,w,h in [('desktop',1440,900),('mobile',390,844),('small-mobile',320,740),('tablet',768,1024)]:
        print('Checking discover:',name,flush=True)
        page=browser.new_page(viewport={'width':w,'height':h},has_touch=w<700)
        observe(page)
        requests=[]
        page.on('request',lambda r:requests.append(r.url))
        page.goto(URL+'/discover/')
        page.wait_for_load_state('networkidle')
        expect(page.get_by_role('heading',level=1)).to_have_text('The Story of Shakti.')
        assert page.locator('main').count()==1
        assert not any('/videos/' in r or '/art/trishul/' in r or '/App-' in r for r in requests), requests
        assert page.get_by_role('radio').count()==6
        page.screenshot(path=str(OUT/f'discover-{name}-hero.png'),animations='disabled')
        for day in [17,16,18,19,20,21]:
            radio=page.get_by_role('radio',name=f'{day} October,',exact=False)
            radio.check()
            expect(radio).to_be_checked()
            assert f'day={day}' in page.url
            expect(page.locator('#day-description')).to_contain_text(f'{day} October')
        page.reload();page.wait_for_load_state('networkidle')
        expect(page.get_by_role('radio',name='21 October, Dashami')).to_be_checked()
        radio=page.get_by_role('radio',name='21 October, Dashami')
        radio.focus();page.keyboard.press('ArrowLeft')
        expect(page.get_by_role('radio',name='20 October, Navami')).to_be_checked()
        page.get_by_role('radio',name='16 October, Shashthi').check()
        for summary in page.locator('summary').all():
            summary.focus();page.keyboard.press('Enter')
            assert summary.evaluate('e=>e.parentElement.open')
            page.keyboard.press('Enter')
            assert not summary.evaluate('e=>e.parentElement.open')
        # Deep anchor, browser Back and direct reload are native URL navigation.
        page.get_by_role('link',name='The rituals',exact=False).click()
        assert page.url.endswith('#rituals')
        page.go_back();page.wait_for_load_state('networkidle')
        overflow(page)
        page.evaluate('scrollTo(0,0)')
        page.screenshot(path=str(OUT/f'discover-{name}.png'),full_page=True,animations='disabled')
        page.screenshot(path=str(OUT/f'discover-{name}-hero.png'),animations='disabled')
        report[name+'-styles']=page.locator('.hero-deck').evaluate('e=>({font:getComputedStyle(e).fontFamily,size:getComputedStyle(e).fontSize,color:getComputedStyle(e).color,background:getComputedStyle(document.querySelector(".discover")).backgroundColor})')
        # Every visible focusable item keeps a focus indicator, including native disclosures.
        page.reload();page.wait_for_load_state('networkidle')
        for _ in range(55):
            page.keyboard.press('Tab')
            focused=page.evaluate('''() => {const e=document.activeElement;return !e||e===document.body?null:{name:e.getAttribute('aria-label')||e.textContent,outline:getComputedStyle(e).outlineStyle}}''')
            assert not focused or focused['outline']!='none', focused
        report['checks'].append(f'{name}: calendar selection/URL/reload/arrows, disclosures, native anchor/back, visible focus, no overflow; no film/WebGL downloads')
        page.close()

    # Exercise the real cinematic at both sizes, including both video decoders.
    for name,w,h in [('desktop',1440,900),('mobile',390,844)]:
        print('Checking cinematic:',name,flush=True)
        page=browser.new_page(viewport={'width':w,'height':h},has_touch=name=='mobile')
        observe(page)
        page.goto(URL+'/?inspect=1');page.wait_for_load_state('networkidle')
        ignite=page.get_by_role('button',name='IGNITE',exact=True)
        expect(ignite).to_be_enabled(timeout=90000)
        page.screenshot(path=str(OUT/f'film-{name}-landing.png'),animations='disabled')
        ignite.focus();page.keyboard.press('Enter')
        page.wait_for_function('window.__SHAKTI__.snapshot().time>.2')
        page.get_by_role('button',name='Pause cinematic').click()
        for t in [7,15.9,16.1,18,26.8,30]:
            page.evaluate('async t=>await window.__SHAKTI__.seek(t)',t)
            s=page.evaluate('window.__SHAKTI__.snapshot()')
            assert abs(s['time']-t)<.02
            if t>=16 and t<30:
                assert s['media']['readyState']>=2
                report['media'].append({'viewport':name,'time':t,'clip':s['media']['clip'],'readyState':s['media']['readyState']})
        page.screenshot(path=str(OUT/f'film-{name}-finale.png'),animations='disabled')
        overflow(page)
        expect(page.get_by_role('link',name='Explore Durga Puja')).to_be_visible()
        page.get_by_role('link',name='Explore Durga Puja').click()
        expect(page.get_by_role('heading',name='The Story of Shakti.')).to_be_visible()
        page.get_by_role('link',name='The film',exact=False).first.click()
        expect(page.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000)
        page.get_by_role('link',name='The Story of Shakti').click()
        expect(page.get_by_role('heading',level=1)).to_be_visible()
        report['checks'].append(f'{name}: IGNITE, WebGL seek, both clips decode, 30s finale, post-film Explore link, return to film, quiet story navigation')
        page.close()

    page=browser.new_page(viewport={'width':1440,'height':900})
    observe(page)
    page.goto(URL+'/?inspect=1');page.wait_for_load_state('networkidle')
    expect(page.get_by_role('button',name='IGNITE',exact=True)).to_be_enabled(timeout=90000)
    page.get_by_role('button',name='IGNITE',exact=True).click()
    page.wait_for_function('window.__SHAKTI__.snapshot().phase==="complete"',timeout=90000)
    report['full_playback']=page.evaluate('window.__SHAKTI__.snapshot()')
    assert report['full_playback']['time']==30
    assert all(q['totalVideoFrames']>0 and q['corruptedVideoFrames']==0 for q in report['full_playback']['videoQuality'])
    report['checks'].append('Uninterrupted real 30-second hybrid playback reaches completion; both videos decoded without corrupted frames')
    page.close()

    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    observe(page)
    page.goto(URL+'/discover');page.wait_for_load_state('networkidle')
    expect(page.get_by_role('heading',level=1)).to_be_visible()
    page.mouse.move(150,500)
    assert page.locator('.devi-art svg').evaluate('e=>getComputedStyle(e).transform')=='none'
    report['checks'].append('Direct /discover without trailing slash works; reduced motion disables illustration tilt')
    page.close()
    browser.close()

report['passed']=not(report['console_errors'] or report['page_errors'] or report['http_errors'])
(OUT/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert report['passed'], report
print(json.dumps({'passed':True,'checks':report['checks'],'media':report['media']},indent=2))
