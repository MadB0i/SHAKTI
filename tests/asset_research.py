"""Read public listing metadata and inspect public previews. Never fetch protected models."""
import json, requests
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path(__file__).resolve().parents[1]/'evidence'/'asset-audit'
OUT.mkdir(parents=True,exist_ok=True)
ids=['7a5c476f6ca8427f840c5e47bd106525','f30d10582bfd4e78b2c5d216cd6eb9c4','94596f2f935d4973887a41f630541c18','33aa09d465214086bd889ee5d33b943a','dc80755afc164e44a62ce5c93ec2a59f']
models=[]
for uid in ids:
    r=requests.get(f'https://api.sketchfab.com/v3/models/{uid}',timeout=30)
    if r.ok:
        d=r.json();models.append(d)
        (OUT/f'{uid}-metadata.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
query=requests.get('https://api.sketchfab.com/v3/search',params={'type':'models','q':'trishul','downloadable':'true','count':24},timeout=30)
if query.ok:
    (OUT/'sketchfab-search.json').write_text(json.dumps(query.json(),indent=2),encoding='utf-8')
    for d in query.json().get('results',[]):
        print('SEARCH',json.dumps({k:d.get(k) for k in ['uid','name','viewerUrl','faceCount','license','isDownloadable']},ensure_ascii=False),flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    for d in models:
        uid=d['uid'];url=max(d['thumbnails']['images'],key=lambda x:x['width'])['url']
        response=page.goto(url,wait_until='load',timeout=45000)
        page.screenshot(path=str(OUT/f'{uid}-preview.png'),full_page=True)
        print('PREVIEW',uid,response.status if response else None,flush=True)
    for label,url in [
        ('sketchfab-first','https://sketchfab.com/3d-models/trishul-shivas-trident-7a5c476f6ca8427f840c5e47bd106525'),
        ('cgtrader-supplied','https://www.cgtrader.com/3d-models/various/various-models/trishul-of-lord-shiva'),
        ('cgtrader-painted','https://www.cgtrader.com/3d-models/various/various-models/trishul-8412e83e-6aa0-41d7-818b-7eca0fe6c397'),
        ('fab-mythic','https://www.fab.com/listings/91ff8ded-2496-4503-97c9-7eb7b85349a2'),
        ('fab-pashupatinath','https://www.fab.com/listings/55ae127c-4584-42ba-ad64-535c2dfa6dda')]:
        try:
            response=page.goto(url,wait_until='domcontentloaded',timeout=45000)
            page.wait_for_timeout(2500)
            body=page.locator('body').inner_text()
            (OUT/f'{label}-page.txt').write_text(body,encoding='utf-8')
            page.screenshot(path=str(OUT/f'{label}-page.png'))
            print('PAGE',label,response.status if response else None,body[:700].replace('\n',' | '),flush=True)
            images=page.locator('img').evaluate_all('(els)=>els.map(e=>({src:e.currentSrc||e.src,alt:e.alt})).filter(e=>e.src.includes("img-new.cgtrader.com/items/") || e.src.includes("media.sketchfab.com/models/"))')
            (OUT/f'{label}-images.json').write_text(json.dumps(images,indent=2),encoding='utf-8')
            if label=='sketchfab-first' and 'Download 3D Model' in body:
                buttons=page.get_by_text('Download 3D Model',exact=True)
                if buttons.count():
                    buttons.first.click();page.wait_for_timeout(1500)
                    print('DOWNLOAD_UI',page.locator('body').inner_text()[-4000:],flush=True)
                    page.screenshot(path=str(OUT/'sketchfab-download-access.png'))
                    (OUT/'sketchfab-download-access.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
        except Exception as e:
            print('PAGE_ERROR',label,str(e)[:300],flush=True)
    browser.close()
