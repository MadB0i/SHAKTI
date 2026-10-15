"""Decode the actual raw-art diagnostic recordings and capture their playback frames."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/divine-recall';report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h});pg.set_content(f'<html><body style="margin:0;background:#000"><video muted playsinline style="width:{w}px;height:{h}px" src="http://127.0.0.1:5173/evidence/divine-recall/{name}-divine-recall.webm"></video></body></html>');pg.wait_for_function('document.querySelector("video").readyState>=2');pg.evaluate('document.querySelector("video").play()')
  for i,t in enumerate([.3,.9,1.1,1.45,2.85]):
   pg.wait_for_function('(t)=>document.querySelector("video").currentTime>=t',arg=t);pg.locator('video').screenshot(path=str(OUT/f'{name}-decoded-{i}.png'))
  pg.wait_for_function('document.querySelector("video").ended',timeout=15000);report[name]=pg.evaluate('''()=>{const v=document.querySelector('video');return {width:v.videoWidth,height:v.videoHeight,duration:v.duration,ended:v.ended,error:v.error?.message??null}}''');assert report[name]['ended'] and report[name]['error'] is None;pg.close()
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 tw=480 if name=='desktop' else 260;th=round(h*tw/w);sheet=Image.new('RGB',(tw*5,th+45),'#11111a');d=ImageDraw.Draw(sheet)
 for i in range(5):
  im=Image.open(OUT/f'{name}-decoded-{i}.png');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(i*tw,45));d.text((i*tw+8,7),f'Decoded playback {i+1}',font=font,fill='#efdfbe')
 sheet.save(OUT/f'{name}-decoded-contact.png')
(OUT/'video-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

