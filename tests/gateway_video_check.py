"""Decode and play the recorded full transition in Chromium; inspect actual video frames."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2b'
report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--use-angle=d3d11','--enable-gpu','--disable-software-rasterizer'])
 for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
  pg=b.new_page(viewport={'width':w,'height':h})
  pg.set_content(f'<html><body style="margin:0;background:#000"><video muted playsinline style="width:{w}px;height:{h}px" src="http://127.0.0.1:5173/evidence/phase2b/{name}-gateway.webm"></video></body></html>')
  pg.wait_for_function('document.querySelector("video").readyState >= 2')
  pg.evaluate('document.querySelector("video").play()')
  for i,t in enumerate([.25,1.2,2.4,3.2,4.0]):
   pg.wait_for_function('(t)=>document.querySelector("video").currentTime >= t',arg=t)
   pg.locator('video').screenshot(path=str(OUT/f'{name}-video-frame-{i}.png'))
  pg.wait_for_function('document.querySelector("video").ended',timeout=15000)
  report[name]=pg.evaluate('''()=>{const v=document.querySelector('video');return {decoded_width:v.videoWidth,decoded_height:v.videoHeight,duration:v.duration,current_time:v.currentTime,ended:v.ended,error:v.error?.message??null}}''')
  assert report[name]['ended'] and report[name]['error'] is None
  pg.close()
 b.close()
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
for name,w,h in [('desktop',1440,810),('portrait',1080,1920)]:
 tw=640 if name=='desktop' else 300;th=round(h*tw/w);sheet=Image.new('RGB',(tw*5,th+40),'#17120d');d=ImageDraw.Draw(sheet)
 for i in range(5):
  im=Image.open(OUT/f'{name}-video-frame-{i}.png');assert im.convert('RGB').getextrema()!=((0,0),(0,0),(0,0));sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(i*tw,40));d.text((i*tw+12,6),f'Decoded video / {i+1}',font=font,fill='#f5e7cc')
 sheet.save(OUT/f'{name}-video-contact.png')
(OUT/'video-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

