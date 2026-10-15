"""Decode real exported frames and correlate captured audio against the supplied tracks."""
from pathlib import Path
import subprocess,json,numpy as np,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/hybrid'
def command(args):return subprocess.run(args,capture_output=True,check=True).stdout
def sound(path,start=0,duration=None):
 args=['ffmpeg','-v','error','-ss',str(start),'-i',str(path)]
 if duration:args+=['-t',str(duration)]
 return np.frombuffer(command(args+['-vn','-ac','1','-ar','6000','-f','f32le','-']),dtype=np.float32).astype(np.float64)
def correlate(recording,source,offset):
 # Inspect ±0.4s around the expected edit point. The native recording may include
 # small real-time media handoff/audio-device latency; no guessed synchronization.
 a=recording[max(0,int((offset-.4)*6000)):int((offset+len(source)/6000+.4)*6000)]
 n=1<<(len(a)+len(source)-1).bit_length();corr=np.fft.irfft(np.fft.rfft(a,n)*np.conj(np.fft.rfft(source,n)),n)
 limits=len(a)-len(source)+1;lag=int(np.argmax(corr[:limits]));part=a[lag:lag+len(source)];score=float(np.dot(part,source)/(np.linalg.norm(part)*np.linalg.norm(source)))
 return {'delay_ms':(lag/6000-.4)*1000,'correlation':score}
report={};font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
for name,w,h in [('Desktop',1440,810),('Reel',1080,1920)]:
 path=OUT/f'SHAKTI-{name}-{w}x{h}.mp4';probe=json.loads(command(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
 dw,dh=(320,180) if name=='Desktop' else (180,320)
 raw=command(['ffmpeg','-v','error','-i',str(path),'-vf',f'fps=30,scale={dw}:{dh}','-an','-pix_fmt','rgb24','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,dh,dw,3)
 report[name]={'duration':probe['format']['duration'],'frames':len(frames),'video':{k:probe['streams'][0].get(k) for k in ['codec_name','width','height','r_frame_rate','duration','nb_frames']},'audio':{k:probe['streams'][1].get(k) for k in ['codec_name','sample_rate','channels','duration']},'cuts':{}}
 for cut in [16,20]:
  indices=range(cut*30-3,cut*30+4);sheet=Image.new('RGB',(dw*7,dh+28),'#101019');draw=ImageDraw.Draw(sheet)
  for x,i in enumerate(indices):sheet.paste(Image.fromarray(frames[i]),(x*dw,28));draw.text((x*dw+7,4),f'{i/30:.3f}s',font=font,fill='#e8cc8f')
  sheet.save(OUT/f'{name.lower()}-cut-{cut}-consecutive.jpg');report[name]['cuts'][str(cut)]={'mean_luminance':frames[list(indices)].mean((1,2,3)).tolist(),'no_black_frames':bool(np.all(frames[list(indices)].mean((1,2,3))>2))}
 recording=sound(path)
 report[name]['audio_sync']={'catch':correlate(recording,sound(ROOT/'public/videos/divine-catch.mp4',6,4),16),'finale':correlate(recording,sound(ROOT/'public/videos/divine-finale.mp4',1,8),21)}
 result=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','ebur128=peak=true','-f','null','NUL'],capture_output=True,text=True,check=True);(OUT/f'{name.lower()}-loudness.txt').write_text(result.stderr)
report['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'public/videos').glob('*.mp4')}
(OUT/'export-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert all(report[k]['frames']==900 and all(v['no_black_frames'] for v in report[k]['cuts'].values()) for k in ['Desktop','Reel'])
