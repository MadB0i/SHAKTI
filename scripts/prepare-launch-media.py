"""Reproducible delivery edit. Sources untouched; no generative repair.
Requires FFmpeg, Python, Pillow and NumPy. Coordinates refer to the active crop.
"""
from pathlib import Path
import subprocess, json, hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/videos/playback'; OUT.mkdir(exist_ok=True)
EVIDENCE=ROOT/'evidence/launch'; EVIDENCE.mkdir(parents=True,exist_ok=True)
for folder in ['before','after']:(EVIDENCE/folder).mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-v','error','-y','-ss','8.4','-i',str(ROOT/'public/videos/divine-catch.mp4'),'-t','1.6','-vf','crop=706:1080:636:0','-an','-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'divine-catch.mp4')],check=True)
# Soft exposure mask tracks the face and favors its shadow cheek. No skin smoothing.
track=np.array([[0,690,160,155,205],[1,640,170,140,195],[2,450,300,100,145],[3,384,350,72,103],[4,358,380,52,78],[5,357,385,48,73],[6,344,395,44,67],[7,338,401,42,63],[8,337,405,41,62],[9,337,405,41,62],[10,337,405,41,62]])
w,h=726,1080
decoder=subprocess.Popen(['ffmpeg','-v','error','-i',str(ROOT/'public/videos/divine-finale.mp4'),'-vf','crop=726:1080:624:0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
encoder=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','30','-i','-','-an','-c:v','libx264','-preset','slow','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'divine-finale.mp4')],stdin=subprocess.PIPE)
yy,xx=np.mgrid[:h,:w].astype(np.float32); stats=[]
for n in range(300):
 raw=decoder.stdout.read(w*h*3)
 if len(raw)!=w*h*3: raise RuntimeError(f'Missing source frame {n}')
 rgb=np.frombuffer(raw,np.uint8).reshape(h,w,3).astype(np.float32)/255
 cx,cy,rx,ry=[np.interp(n/30,track[:,0],track[:,j]) for j in range(1,5)]
 mask=np.exp(-2*((xx-(cx-rx*.24))/rx)**2-2*((yy-cy)/ry)**2)
 luma=rgb@np.array([.2126,.7152,.0722],np.float32)
 shadows=np.clip((.78-luma)/.50,0,1)*np.clip(luma/.10,0,1)
 gain=1+.25*mask*shadows*np.clip((n/30-.5)/.8,0,1)
 graded=np.clip(rgb*gain[...,None],0,1)
 encoder.stdin.write((graded*255+.5).astype(np.uint8).tobytes())
 if n in [30,60,90,150,240]:
  Image.fromarray((rgb*255+.5).astype(np.uint8)).save(EVIDENCE/f'before/face-{n}.png')
  Image.fromarray((graded*255+.5).astype(np.uint8)).save(EVIDENCE/f'after/face-{n}.png')
  stats.append({'frame':n,'maximum_rgb_lift':float(((graded-rgb)*255).max())})
encoder.stdin.close(); assert encoder.wait()==0; assert decoder.wait()==0
report={'edit':'catch source 8.4–10 to film 16–17.6; finale 0–10 to 17.6–27.6; last frame held to 30','audio':'Embedded audio omitted from delivery files.','face_lift':stats,'assets':{}}
for name in ['divine-catch.mp4','divine-finale.mp4']:
 src=ROOT/'public/videos'/name; dest=OUT/name
 report['assets'][name]={'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'delivery_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
(EVIDENCE/'media-edit.json').write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
