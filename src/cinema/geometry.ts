import * as T from 'three'

/** Closed bowl profile includes the interior, rolled rim, and foot. */
export function diyaGeometry(segments=48) {
 const profile=[[0, .065],[.16,.065],[.21,.085],[.3,.16],[.39,.29],[.43,.34],[.435,.365],[.42,.385],[.4,.375],[.385,.34],[.34,.25],[.26,.17],[.14,.14],[0,.14]]
 const g=new T.LatheGeometry(profile.map(([x,y])=>new T.Vector2(x,y)),segments)
 const pos=g.attributes.position
 for(let i=0;i<pos.count;i++){
  const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i)
  const pinch=Math.pow(Math.max(0,z/.44),5)
  pos.setXYZ(i,x*(1.-pinch*.6),y+pinch*.015,z*(1.+pinch*.75))
 }
 g.computeVertexNormals();return g
}

export function floorPattern() {
 const paths=[
  new T.CatmullRomCurve3([new T.Vector3(0,0,0),new T.Vector3(0,4,0),new T.Vector3(0,8,0),new T.Vector3(0,12.2,0)]),
  ...[-1,1].map(s=>new T.CatmullRomCurve3([new T.Vector3(0,6.7,0),new T.Vector3(s*2.3,7.3,0),new T.Vector3(s*3.6,9,0),new T.Vector3(s*3.35,11.5,0)]))
 ]
 const lamps: {position:T.Vector3;delay:number;seed:number}[]=[]
 for(let k=0;k<paths.length;k++){
  const path=paths[k],n=Math.ceil(path.getLength()/.39)
  for(let j=0;j<=n;j++){
   const p=path.getPointAt(j/n),tan=path.getTangentAt(j/n)
   for(const row of [-1,0,1]){
    const x=(p.x+tan.y*row*.23)*1.15,z=7.-(p.y-tan.x*row*.23)*1.34
    if(Math.hypot(x,z-7)<.85)continue
    lamps.push({position:new T.Vector3(x,.02,z),delay:1.5+Math.hypot(x,z-7)/17.5*1.8,seed:lamps.length*.61803398875%1})
   }
  }
 }
 return lamps
}

/** Area-weighted triangle sampling, so the particles resolve into the actual solid. */
export function sampleSurface(geometry:T.BufferGeometry,count:number) {
 const p=geometry.attributes.position,areas:number[]=[];let sum=0
 const a=new T.Vector3(),b=new T.Vector3(),c=new T.Vector3(),ab=new T.Vector3(),ac=new T.Vector3()
 for(let i=0;i<p.count;i+=3){a.fromBufferAttribute(p,i);b.fromBufferAttribute(p,i+1);c.fromBufferAttribute(p,i+2);sum+=ab.subVectors(b,a).cross(ac.subVectors(c,a)).length()*.5;areas.push(sum)}
 let seed=783;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296}
 const values=new Float32Array(count*3)
 for(let i=0;i<count;i++){
  const pick=rand()*sum;let lo=0,hi=areas.length-1;while(lo<hi){const mid=(lo+hi)>>1;if(areas[mid]<pick)lo=mid+1;else hi=mid}
  a.fromBufferAttribute(p,lo*3);b.fromBufferAttribute(p,lo*3+1);c.fromBufferAttribute(p,lo*3+2)
  const r=Math.sqrt(rand()),s=rand();a.multiplyScalar(1-r).addScaledVector(b,r*(1-s)).addScaledVector(c,r*s);values.set([a.x,a.y+2.1,a.z-1.2],i*3)
 }
 return values
}
