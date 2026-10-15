from pathlib import Path
import subprocess,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/final-polish';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
def run(args):return subprocess.run(args,check=True,capture_output=True).stdout
def sound(path,start=0,duration=None):
 a=['ffmpeg','-v','error','-ss',str(start),'-i',str(path)]
 if duration:a+=['-t',str(duration)]
 return np.frombuffer(run(a+['-vn','-ac','1','-ar','6000','-f','f32le','-']),dtype=np.float32).astype(np.float64)
def correlate(rec,src,offset):
 a=rec[int((offset-.4)*6000):int((offset+len(src)/6000+.4)*6000)];n=1<<(len(a)+len(src)-1).bit_length();c=np.fft.irfft(np.fft.rfft(a,n)*np.conj(np.fft.rfft(src,n)),n);lag=int(np.argmax(c[:len(a)-len(src)+1]));part=a[lag:lag+len(src)];return {'delay_ms':round((lag/6000-.4)*1000,2),'correlation':float(np.dot(part,src)/(np.linalg.norm(part)*np.linalg.norm(src)))}
report={}
for name,title,w,h in [('desktop','Desktop',1440,810),('portrait','Reel',1080,1920)]:
 src=OUT/'after'/f'{name}-complete.webm';dest=OUT/f'SHAKTI-{title}-{w}x{h}.mp4'
 run(['ffmpeg','-v','error','-y','-i',str(src),'-t','30','-vf','fps=30','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-af','aresample=async=1:first_pts=0','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(dest)])
 probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dest)]));report[name]={'probe':probe}
 dw,dh=(320,180) if name=='desktop' else (180,320)
 for version,path in [('before',OUT/'before'/f'{name}-complete.webm'),('after',dest)]:
  raw=run(['ffmpeg','-v','error','-i',str(path),'-t','30','-vf',f'fps=30,scale={dw}:{dh}','-an','-pix_fmt','rgb24','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,dh,dw,3)
  # All frames are decoded; indexed contact sheets cover every second of the actual recording.
  sheet=Image.new('RGB',(dw*6,(dh+24)*5),'#080a12');d=ImageDraw.Draw(sheet)
  for second in range(30):
   x=second%6*dw;y=second//6*(dh+24);sheet.paste(Image.fromarray(frames[second*30]),(x,y+24));d.text((x+5,y+2),f'{second:02d}s',font=font,fill='#d9bc7e')
  sheet.save(OUT/version/f'{name}-recording-contact.jpg')
  for cut in [16,20]:
   indices=range(cut*30-2,cut*30+8);sheet=Image.new('RGB',(dw*5,(dh+24)*2),'#080a12');d=ImageDraw.Draw(sheet)
   for j,i in enumerate(indices):
    x=j%5*dw;y=j//5*(dh+24);sheet.paste(Image.fromarray(frames[i]),(x,y+24));d.text((x+5,y+2),f'{i/30:.3f}s',font=font,fill='#d9bc7e')
   sheet.save(OUT/version/f'{name}-cut-{cut}.jpg')
  if version=='after':
   assert len(frames)==900
   report[name]['decoded_frames']=len(frames);report[name]['cut_luminance']={str(cut):frames[cut*30-2:cut*30+8].mean((1,2,3)).tolist() for cut in [16,20]}
   report[name]['audio_sync']={label:correlate(sound(dest),sound(ROOT/'public/videos'/file,start,duration),offset) for label,file,start,duration,offset in [('catch','divine-catch.mp4',6.3,3.4,16.3),('finale','divine-finale.mp4',1,8,21)]}
   loud=subprocess.run(['ffmpeg','-hide_banner','-i',str(dest),'-af','ebur128=peak=true','-f','null','NUL'],capture_output=True,text=True,check=True);(OUT/f'{name}-loudness.txt').write_text(loud.stderr);report[name]['loudness_summary']=loud.stderr[loud.stderr.rfind('Summary:'):]
 print(name,report[name]['audio_sync'],flush=True)
(OUT/'export-verification.json').write_text(json.dumps(report,indent=2))
for name,w,h in [('desktop',1440,810),('portrait',1080,1920),('mobile',390,844)]:
 tw=640 if name=='desktop' else 300
 for time in ['16','24.5','with-controls']:
  pa=OUT/'before'/f'{name}-{time}.png';pb=OUT/'after'/f'{name}-{time}.png'
  if not pa.exists() or not pb.exists():continue
  a=Image.open(pa);b=Image.open(pb);th=round(tw*a.height/a.width);sheet=Image.new('RGB',(tw*2,th+28),'#080a12');d=ImageDraw.Draw(sheet)
  for j,im in enumerate([a,b]):sheet.paste(im.resize((tw,th)),(tw*j,28));d.text((tw*j+8,4),['BEFORE','AFTER'][j],font=font,fill='#d9bc7e')
  sheet.save(OUT/f'{name}-{time}-comparison.jpg')
