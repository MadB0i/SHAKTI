from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'evidence/final-polish';report={}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True)
 pg=b.new_page(viewport={'width':1440,'height':1000});pg.goto((out/'review.html').as_uri());pg.wait_for_load_state('networkidle')
 for name in ['portrait','desktop']:
  pg.get_by_role('button',name='Play final '+name).click();start=time.monotonic()
  # Normal 1x playback of the delivered MP4, independently of the app renderer.
  pg.wait_for_function('(id)=>document.getElementById(id).ended',arg=name,timeout=40000)
  report[name]=pg.locator('#'+name).evaluate('(v)=>({duration:v.duration,time:v.currentTime,width:v.videoWidth,height:v.videoHeight,rate:v.playbackRate,muted:v.muted,error:v.error,quality:{total:v.getVideoPlaybackQuality().totalVideoFrames,dropped:v.getVideoPlaybackQuality().droppedVideoFrames}})')
  report[name]['wall_seconds']=time.monotonic()-start
  assert report[name]['duration']==30 and report[name]['rate']==1 and not report[name]['error']
  pg.locator('#'+name).screenshot(path=str(out/f'{name}-export-playback-final.png'))
  print(name,report[name],flush=True)
 b.close()
(out/'export-browser-playback.json').write_text(json.dumps(report,indent=2))

