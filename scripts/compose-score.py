"""Original synthesized score; no samples or generated music. Festival-inspired,
not authentic recorded dhaak/shankh. Copyright 2026 Rupjyoti Talukdar. MIT.
"""
from pathlib import Path
import numpy as np
import wave, subprocess
ROOT=Path(__file__).resolve().parents[1]; SR=48000
(ROOT/'evidence/launch').mkdir(parents=True,exist_ok=True);(ROOT/'public/audio').mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(20261015); mix=np.zeros((SR*30,2),np.float64)
def add(start,signal,gain=1,pan=0):
 i=round(start*SR); signal=signal[:len(mix)-i]*gain
 if len(signal)>0: mix[i:i+len(signal),0]+=signal*np.sqrt((1-pan)/2); mix[i:i+len(signal),1]+=signal*np.sqrt((1+pan)/2)
def tone(start,duration,freq,gain,pan=0):
 t=np.arange(round(duration*SR))/SR; env=(1-np.exp(-t/1.2))*np.minimum(1,(duration-t)/1.4)
 s=sum(np.sin(2*np.pi*freq*k*t+np.sin(t*.8)*.012)*a for k,a in [(1,1),(2,.22),(3,.08)])*env
 add(start,s,gain,pan)
def drum(start,low=True,gain=.24):
 t=np.arange(int(SR*.65))/SR; f=76 if low else 185
 phase=2*np.pi*(f*t+40*.035*(1-np.exp(-t/.035))); s=np.sin(phase)*np.exp(-t/(.19 if low else .09))
 noise=np.convolve(rng.normal(0,1,len(t)),[1,-.75],mode='same'); s+=noise*np.exp(-t/.014)*.15
 add(start,s*(1-np.exp(-t/.001)),gain,-.12 if low else .16)
def shimmer(start,duration,gain):
 t=np.arange(int(SR*duration))/SR; s=sum(np.sin(2*np.pi*f*t)*np.exp(-t/(duration*.35))/4 for f in [587.33,880,1174.66,1760])
 add(start,s*(1-np.exp(-t/.008)),gain,.25)
def air(start,duration,gain):
 t=np.arange(int(SR*duration))/SR; s=np.convolve(rng.normal(0,1,len(t)),np.ones(40)/40,mode='same')
 add(start,s*np.sin(np.pi*t/duration)**2,gain,-.15)
tone(0,16,73.416,.075,-.2); tone(2,14,110,.04,.2); shimmer(.12,2,.12); air(.02,.45,.35)
for start in [2.1,3.3,4.5,5.7]: shimmer(start,1.8,.05)
tone(6.8,5.3,146.832,.065); air(9,3,.38)
for beat in np.arange(7,27.5,.3125):
 pos=round((beat-7)/.3125)%6
 if pos in [0,2,3,5]: drum(beat,pos in [0,3],(.11 if beat<12 else .19)*(1 if pos in [0,3] else .58))
tone(12,6,146.832,.09,-.1); tone(12.2,5.5,220,.045,.1); air(14.4,1.8,.5); drum(16.05,True,.5); shimmer(16.06,3,.16)
tone(17.6,12.4,146.832,.10); tone(18,12,220,.05,.2); tone(19,11,293.665,.03,-.2)
for start in [12.6,19.2]:
 t=np.arange(int(3.2*SR))/SR; phase=2*np.pi*(293.665*t-8*.35*(1-np.exp(-t/.35)))
 s=sum(np.sin(k*phase)/k**1.6 for k in range(1,7))*np.sin(np.pi*t/3.2)**1.5; add(start,s,.10,-.05)
shimmer(24,4,.1); shimmer(27.6,2.4,.15); drum(27.6,True,.16)
dry=mix.copy()
for delay,gain in [(.113,.12),(.227,.07),(.389,.04)]:
 n=int(delay*SR);mix[n:]+=dry[:-n,::-1]*gain
fade=np.minimum(1,np.arange(len(mix))/(SR*.025))*np.minimum(1,(len(mix)-1-np.arange(len(mix)))/(SR*1.3))
mix*=fade[:,None]; mix*=.78/max(abs(mix).max(),1e-9)
out=ROOT/'evidence/launch/score-master.wav'
with wave.open(str(out),'wb') as f: f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-af','loudnorm=I=-18:TP=-1.5:LRA=9','-ar','48000','-c:a','aac','-b:a','192k','-movflags','+faststart',str(ROOT/'public/audio/shakti-original.m4a')],check=True)
print('Original 30-second score prepared.')
