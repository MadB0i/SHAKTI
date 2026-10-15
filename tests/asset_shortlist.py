"""Inspect additional public candidate previews without downloading model archives."""
import json,requests
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'evidence'/'asset-audit'
ids=['ef8230925b8a4a908862c6415bc8f726','7d154946cba44ac7ae858bc205727581','770c102a668041089d8a024a36ac2c11','03bf8ea458f74375895930f235b81ee7','208469700fc042e5bd977ea4684ff304','e5d2eb9517ba4ccead8b695014fb0f3f','e0498569303347098f997cfe4ba40b4f','4be12334d56f436588d778b61b97029f']
models=[]
for uid in ids:
    r=requests.get(f'https://api.sketchfab.com/v3/models/{uid}',timeout=30)
    if not r.ok: continue
    d=r.json();models.append(d)
    (out/f'{uid}-metadata.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    print(json.dumps({'uid':uid,'name':d['name'],'creator':d['user']['displayName'],'url':d['viewerUrl'],'triangles':d['faceCount'],'license':d.get('license'),'description':d.get('description'),'tags':[t['name'] for t in d.get('tags',[])]},ensure_ascii=False),flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    for d in models:
        url=max(d['thumbnails']['images'],key=lambda x:x['width'])['url']
        response=page.goto(url,wait_until='load',timeout=45000)
        page.screenshot(path=str(out/f'{d["uid"]}-preview.png'))
    for label in ['cgtrader-supplied','cgtrader-painted']:
        imgs=json.loads((out/f'{label}-images.json').read_text(encoding='utf-8'))
        imgs=[i for i in imgs if 'img-new.cgtrader.com/items/' in i['src'] and '/thumb/' not in i['src']]
        for i,img in enumerate(imgs[:3]):
            page.goto(img['src'],wait_until='load',timeout=45000)
            page.screenshot(path=str(out/f'{label}-preview-{i}.png'))
    browser.close()
