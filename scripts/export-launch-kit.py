from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'evidence/launch'; OUT=ROOT/'launch-assets'
def run(args):return subprocess.run(['ffmpeg','-v','error','-y']+args,check=True,capture_output=True).stdout
report={};font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
for name,label,w,h in [('desktop','Desktop',1440,810),('portrait','Reel',1080,1920)]:
 dest=OUT/f'video/SHAKTI-{label}-{w}x{h}.mp4'
 run(['-i',str(E/f'after/{name}-complete.webm'),'-t','30','-vf','fps=30','-c:v','libx264','-crf','20','-preset','medium','-profile:v','high','-level:v','4.1','-maxrate','10M','-bufsize','20M','-pix_fmt','yuv420p','-af','aresample=async=1:first_pts=0','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(dest)])
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]));report[name]={'probe':probe}
 dw,dh=(320,180) if name=='desktop' else (180,320)
 raw=run(['-i',str(dest),'-vf',f'fps=30,scale={dw}:{dh}','-an','-pix_fmt','rgb24','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,dh,dw,3);assert len(frames)==900
 sheet=Image.new('RGB',(dw*6,(dh+24)*5),'#080a12');d=ImageDraw.Draw(sheet)
 for second in range(30):
  x=second%6*dw;y=second//6*(dh+24);sheet.paste(Image.fromarray(frames[second*30]),(x,y+24));d.text((x+5,y+2),f'{second:02d}s',font=font,fill='#d9bc7e')
 sheet.save(E/f'after/{name}-recording-contact.jpg')
 for cut in [16,17.6,27.6]:
  sheet=Image.new('RGB',(dw*5,(dh+24)*2),'#080a12');d=ImageDraw.Draw(sheet)
  for j,i in enumerate(range(round(cut*30)-3,round(cut*30)+7)):
   x=j%5*dw;y=j//5*(dh+24);sheet.paste(Image.fromarray(frames[i]),(x,y+24));d.text((x+5,y+2),f'{i/30:.3f}s',font=font,fill='#d9bc7e')
  sheet.save(E/f'after/{name}-transition-{cut}.jpg')
 audio=subprocess.run(['ffmpeg','-hide_banner','-i',str(dest),'-af','ebur128=peak=true','-f','null','NUL'],capture_output=True,text=True,check=True).stderr
 (E/f'{name}-loudness.txt').write_text(audio);report[name]['loudness_summary']=audio[audio.rfind('Summary:'):];report[name]['decoded_frames']=len(frames)
 print('Exported',dest.name,flush=True)
reel=OUT/'video/SHAKTI-Reel-1080x1920.mp4'
run(['-i',str(reel),'-vf','scale=540:960','-c:v','libx264','-crf','23','-preset','medium','-c:a','aac','-b:a','128k','-movflags','+faststart',str(ROOT/'docs/media/shakti-cinematic.mp4')])
(ROOT/'public/media').mkdir(exist_ok=True)
(ROOT/'public/media/shakti-film.mp4').write_bytes((ROOT/'docs/media/shakti-cinematic.mp4').read_bytes())
# 8.5 seconds, genuine excerpts from the finished film. Each audio edit is softly faded.
cuts=[(.7,2.2),(5.6,7.1),(14.5,16),(19.4,21.4),(28,30)]
filters=[];inputs=[]
for i,(a,b) in enumerate(cuts):
 filters += [f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]',f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st={b-a-.04}:d=0.04[a{i}]'];inputs += [f'[v{i}][a{i}]']
filters.append(''.join(inputs)+f'concat=n={len(cuts)}:v=1:a=1[v][a]')
teaser=OUT/'video/SHAKTI-Teaser-8.5s.mp4'
run(['-i',str(reel),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-crf','22','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(teaser)])
run(['-i',str(teaser),'-vf','scale=540:960','-c:v','libx264','-crf','23','-c:a','aac','-b:a','128k','-movflags','+faststart',str(OUT/'video/SHAKTI-X-Teaser.mp4')])
# First GIF frame starts with the already-lit flame. Small, silent and genuinely animated.
run(['-ss','0.7','-t','7','-i',str(reel),'-vf','fps=10,scale=270:480:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=3','-loop','0',str(ROOT/'docs/media/shakti-preview.gif')])
run(['-ss','29','-i',str(reel),'-frames:v','1',str(OUT/'covers/SHAKTI-Reel-Cover-1080x1920.jpg')])
im=Image.open(E/'after/desktop-29.5.png').convert('RGB').resize((1120,630),Image.Resampling.LANCZOS)
cover=Image.new('RGB',(1200,630),'#080a12');cover.paste(im,(40,0));d=ImageDraw.Draw(cover);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);d.text((65,600),'Created by Rupjyoti Talukdar (MadB0i)',font=small,fill='#c9b98f')
cover.save(OUT/'covers/SHAKTI-GitHub-LinkedIn-1200x630.jpg',quality=94);cover.save(ROOT/'public/social/shakti-social.jpg',quality=90)
(E/'export-verification.json').write_text(json.dumps(report,indent=2))
print('Launch kit exported.',flush=True)
