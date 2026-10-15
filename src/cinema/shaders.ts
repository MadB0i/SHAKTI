export const noise = `
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
float fbm(vec2 p){return .55*noise2(p)+.27*noise2(p*2.03)+.13*noise2(p*4.1)+.05*noise2(p*8.2);}
`
export const flameVertex = `
attribute float aDelay; attribute float aSeed; attribute float aSize;
uniform float uTime; uniform float uClock;
varying vec2 vUv; varying float vLit; varying float vSeed;
void main(){
 vUv=uv;vSeed=aSeed;
 vLit=smoothstep(aDelay,aDelay+.22,uTime);
 float flicker=1.+.12*sin(uClock*14.+aSeed*12.)+.06*sin(uClock*23.+aSeed*29.);
 vec3 p=position;
 p.x+=pow(uv.y,2.)*(sin(uClock*5.+aSeed*30.+uv.y*5.)*.08+sin(uClock*9.+aSeed)*.025);
 p.y=(p.y+.5)*flicker;
 vec4 center=modelViewMatrix*instanceMatrix*vec4(0.,0.,0.,1.);
 // Camera-facing quads retain an upright silhouette from every camera angle.
 center.xy+=p.xy*aSize*vec2(.55,1.)*vLit;
 gl_Position=projectionMatrix*center;
}
`
export const flameFragment = `
uniform float uClock; varying vec2 vUv; varying float vLit; varying float vSeed;
${noise}
void main(){
 float y=vUv.y; float sway=sin(y*9.-uClock*6.+vSeed*9.)*.035*y;
 float x=abs(vUv.x-.5-sway);
 float width=.27*pow(max(0.,sin(y*3.14159)),.75)*(1.-y*.65);
 float edge=1.-smoothstep(width*.55,width+ .025,x);
 float turbulence=.82+.18*noise2(vec2(y*9.-uClock*7.,vSeed*20.));
 float alpha=edge*smoothstep(0.,.06,y)*(1.-smoothstep(.78,1.,y))*vLit*turbulence;
 vec3 color=mix(vec3(2.,.25,.008),vec3(4.,1.8,.26),1.-smoothstep(.03,.17,x));
 color=mix(vec3(.25,.35,1.3),color,smoothstep(.01,.1,y));
 gl_FragColor=vec4(color,alpha);
}
`
export const floorVertex = `varying vec3 vWorld; void main(){vWorld=(modelMatrix*vec4(position,1.)).xyz;gl_Position=projectionMatrix*viewMatrix*vec4(vWorld,1.);}`
export const floorFragment = `
varying vec3 vWorld; uniform float uTime; uniform float uClock; uniform vec3 uEye;
${noise}
void main(){
 vec2 p=vWorld.xz; float grain=fbm(p*7.); float worn=fbm(p*.8);
 vec2 grid=p/2.4;grid.x+=mod(floor(grid.y+.5),2.)*.5;
 vec2 tile=abs(fract(grid+.5)-.5); float seam=smoothstep(.486,.5,max(tile.x,tile.y)+noise2(p*9.)*.005);
 float fine=pow(noise2(p*110.),8.);
 vec3 stone=mix(vec3(.024,.027,.029),vec3(.065,.062,.054),worn)*(.65+grain*.7);
 stone*=1.-seam*.55;stone+=fine*.009;
 vec3 toLamp=vec3(0.,.8,7.)-vWorld;
 float ignition=smoothstep(0.,.25,uTime);
 float warm=(.12+ignition*2.6)/(1.+dot(toLamp,toLamp)*1.8);
 float d=length(p-vec2(0,7)); float wave=max(0.,uTime-1.4)*9.;
 float ring=exp(-pow((d-wave)*3.,2.))*step(1.4,uTime)*(1.-smoothstep(3.4,4.,uTime));
 float field=smoothstep(1.5,3.5,uTime)*.035;
 vec3 light=vec3(.28,.32,.4)*.11+vec3(1.,.45,.13)*(warm+field+ring*2.);
 vec3 view=normalize(uEye-vWorld); vec3 halfv=normalize(normalize(toLamp)+view);
 float spec=pow(max(0.,halfv.y+ (grain-.5)*.14),70.)*ignition/(1.+d*d)*.3;
 vec3 color=stone*light*5.+vec3(.8,.32,.06)*spec;
 float fog=exp(-length(uEye-vWorld)*.055);
 gl_FragColor=vec4(color*fog,1.);
 #include <tonemapping_fragment>
 #include <colorspace_fragment>
}
`
export const poolVertex = `
attribute float aDelay;uniform float uTime;varying vec2 vUv;varying float vLit;
void main(){vUv=uv;vLit=smoothstep(aDelay,aDelay+.3,uTime);gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);}
`
export const poolFragment = `varying vec2 vUv;varying float vLit;void main(){float r=length(vUv-.5)*2.;float a=exp(-r*r*7.)*(1.-smoothstep(.7,1.,r))*vLit;gl_FragColor=vec4(1.,.31,.035,a*.23);}`
export const particleVertex = `
attribute vec3 aTarget;attribute float aSeed;attribute float aDelay;
uniform float uTime;uniform float uClock;uniform float uDpr;
varying float vAlpha;varying float vHeat;
void main(){
 float p=clamp((uTime-3.45-aDelay)/2.05,0.,1.);float e=p*p*(3.-2.*p);
 vec3 pos=mix(position,aTarget,e);
 float spiral=sin(p*3.14159);
 pos.x+=sin(p*12.+aSeed*30.)*spiral*(.5+aSeed);
 pos.z+=cos(p*12.+aSeed*30.)*spiral*(.5+aSeed);
 pos.y+=sin(p*3.14159)*1.8;
 pos+=vec3(sin(uClock*2.+aSeed*70.),cos(uClock+aSeed*30.),sin(aSeed*60.+uClock))*.025*e;
 vec4 mv=modelViewMatrix*vec4(pos,1.);
 gl_Position=projectionMatrix*mv;
 gl_PointSize=clamp((14.+aSeed*24.)*uDpr/-mv.z,1.,7.);
 vAlpha=smoothstep(0.,.15,p)*(1.-smoothstep(5.35,6.1,uTime)*.995);
 vHeat=aSeed;
}
`
export const particleFragment = `varying float vAlpha;varying float vHeat;void main(){float r=length(gl_PointCoord-.5)*2.;float a=exp(-r*r*5.)*(1.-smoothstep(.6,1.,r))*vAlpha;gl_FragColor=vec4(mix(vec3(2.,.35,.015),vec3(4.,2.,.4),vHeat),a);}`
export const smokeVertex = `
attribute float aSeed;uniform float uClock;uniform float uTime;varying vec2 vUv;varying float vAlpha;
void main(){vUv=uv;float life=fract(uClock*.12+aSeed);vec3 p=position;vec3 base=vec3(sin(aSeed*90.)*life*.9,.6+life*2.6,7.+cos(aSeed*80.)*life*.5);vec4 mv=modelViewMatrix*vec4(base,1.);mv.xy+=p.xy*(.3+life*1.3);gl_Position=projectionMatrix*mv;vAlpha=sin(life*3.14159)*smoothstep(0.,.6,uTime)*.07;}
`
export const smokeFragment = `${noise}
uniform float uClock;varying vec2 vUv;varying float vAlpha;
void main(){float r=length(vUv-.5)*2.;float n=fbm(vUv*5.+vec2(0.,-uClock*.15));float a=(1.-smoothstep(.1,1.,r))*n*vAlpha;gl_FragColor=vec4(.35,.27,.18,a);}
`
