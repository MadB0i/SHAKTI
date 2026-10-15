import { useRef } from 'react'

/** Original, symbolic vector illustrations. These are not documentary artefacts. */
export function DeviArt(){
 const figure=useRef<HTMLElement>(null)
 return <figure className="devi-art" ref={figure} onPointerMove={e=>{
  if(e.pointerType!=='mouse'||matchMedia('(prefers-reduced-motion: reduce)').matches)return
  const r=e.currentTarget.getBoundingClientRect()
  figure.current?.style.setProperty('--tilt-x',`${((e.clientX-r.left)/r.width-.5)*5}deg`)
  figure.current?.style.setProperty('--tilt-y',`${((e.clientY-r.top)/r.height-.5)*-5}deg`)
 }} onPointerLeave={()=>{figure.current?.style.setProperty('--tilt-x','0deg');figure.current?.style.setProperty('--tilt-y','0deg')}}>
  <svg viewBox="0 0 600 590" role="img" aria-labelledby="devi-title">
   <title id="devi-title">Original symbolic illustration of Maa Durga: golden eyes, a crimson bindi and an ornate crown inside a celestial halo</title>
   <defs>
    <radialGradient id="devi-glow"><stop stopColor="#6e263d" stopOpacity=".45"/><stop offset="1" stopColor="#241933" stopOpacity="0"/></radialGradient>
    <linearGradient id="devi-gold" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#896336"/><stop offset=".45" stopColor="#f2d695"/><stop offset="1" stopColor="#af8042"/></linearGradient>
    <linearGradient id="devi-face" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#e5b86e" stopOpacity=".15"/><stop offset="1" stopColor="#b87649" stopOpacity=".02"/></linearGradient>
   </defs>
   <circle cx="300" cy="290" r="280" fill="url(#devi-glow)"/>
   <g fill="none" stroke="url(#devi-gold)">
    <circle cx="300" cy="290" r="252" opacity=".4"/><circle cx="300" cy="290" r="239" opacity=".25"/>
    {Array.from({length:40},(_,i)=><g key={i} transform={`rotate(${i*9} 300 290)`} opacity={i%5===0?.7:.3}><path d="M300 30v13"/><circle cx="300" cy="54" r="1.5" fill="#eab969"/></g>)}
    {Array.from({length:16},(_,i)=><path key={i} transform={`rotate(${i*22.5} 300 290)`} d="M300 78Q265 108 300 129Q335 108 300 78Z" opacity=".28"/>)}
    <path d="M300 10v20m-10-10h20M300 550v24m-12-12h24M20 290h24m-12-12v24m524-12h24m-12-12v24" opacity=".6"/>
   </g>
   <path d="M190 251Q174 405 242 465L300 498L358 465Q426 405 410 251Z" fill="url(#devi-face)" stroke="url(#devi-gold)" strokeWidth="1.3"/>
   <g fill="none" stroke="url(#devi-gold)" strokeWidth="1.3">
    <path d="M180 277Q123 266 129 330Q135 361 170 344M420 277Q477 266 471 330Q465 361 430 344"/>
    <path d="M172 348Q130 392 167 418Q202 392 172 348ZM428 348Q470 392 433 418Q398 392 428 348Z"/>
    <circle cx="167" cy="390" r="8"/><circle cx="433" cy="390" r="8"/>
    <path d="M183 260Q180 164 229 147Q238 90 273 106Q284 58 300 45Q316 58 327 106Q362 90 371 147Q420 164 417 260Z" fill="#141017"/>
    <path d="M193 239Q300 197 407 239M195 249Q300 207 405 249M201 218Q300 181 399 218"/>
    <path d="M300 73Q254 134 300 181Q346 134 300 73ZM300 103Q278 137 300 161Q322 137 300 103Z"/>
    <path d="M247 132Q214 166 248 195Q280 161 247 132ZM353 132Q386 166 352 195Q320 161 353 132Z"/>
    {Array.from({length:9},(_,i)=><g key={i} transform={`translate(${212+i*22} ${230-Math.sin(i/8*Math.PI)*19})`}><path d="M0-5l4 5-4 5-4-5Z" fill="#c39858"/></g>)}
    <path d="M219 175Q200 183 207 204M381 175Q400 183 393 204M286 195Q300 181 314 195"/>
   </g>
   <g fill="none" stroke="#e6bd77" strokeLinecap="round">
    <path d="M208 285Q242 266 274 285M326 285Q358 266 392 285" strokeWidth="3"/>
    <path d="M199 306Q239 289 276 312Q241 341 207 316L199 306ZM401 306Q361 289 324 312Q359 341 393 316L401 306Z" strokeWidth="2" fill="#c69b5520"/>
    <path d="M199 306L186 294M401 306l13-12" strokeWidth="2"/>
    <path d="M286 352Q281 389 299 391Q314 390 310 380" opacity=".8"/>
    <path d="M276 422Q300 410 324 422Q300 442 276 422Z" fill="#6b2636" stroke="#ba7c5b"/>
    <path d="M281 423h38M265 454Q300 473 335 454" opacity=".5"/>
    <circle cx="320" cy="391" r="21"/><circle cx="336" cy="405" r="3" fill="#e6bd77"/>
   </g>
   <g fill="#f0ce89"><ellipse cx="240" cy="313" rx="7" ry="12"/><ellipse cx="360" cy="313" rx="7" ry="12"/></g>
   <g fill="#09080d"><ellipse cx="241" cy="313" rx="3" ry="9"/><ellipse cx="359" cy="313" rx="3" ry="9"/></g>
   <path d="M300 246Q281 269 300 286Q319 269 300 246Z" fill="#a83743" stroke="#eab969"/>
   <path d="M300 253v24" stroke="#f0ce89"/>
   <g fill="none" stroke="url(#devi-gold)" opacity=".6"><path d="M229 475Q220 503 191 511M371 475Q380 503 409 511M250 485Q300 540 350 485M264 499Q300 528 336 499"/>
   <path d="M99 470q30-20 51 10q-30 20-51-10Zm402 0q-30-20-51 10q30 20 51-10Z"/>
   <path d="M89 457q22-1 31 15M511 457q-22-1-31 15"/></g>
  </svg>
  <figcaption>শক্তি · The many forms of strength</figcaption>
 </figure>
}

export type Motif='elephant'|'rooster'|'lotus'|'leaf'|'lamp'|'smoke'|'drum'|'trident'
export function MotifArt({kind}:{kind:Motif}){
 const paths:Record<Motif,React.ReactNode>={
  elephant:<><path d="M22 84V53q0-22 26-22h41q19-15 34-1q12 12 6 29v23q0 22 16 17q12-6 2-20M28 68v31h15V77h38v22h15V62M102 44q-20-10-23 7q-3 18 13 19q15-2 10-26ZM22 44Q9 49 12 68"/><path d="M37 33v26h35V33M38 59l18 10 16-10M118 57l12 6"/><circle cx="117" cy="40" r="2" fill="currentColor"/></>,
  rooster:<><path d="M84 47q-5-16 9-21q-5-17 5-17q8 0 9 14q13-4 15 5q0 7-12 11l15 9-18 6q0 26-16 40q-20 13-40-6q-18-12-8-38q-20-24-31-3q3-31 25-21q-13-25-27-13q27-24 42 9q-2-22-17-25q30-5 35 33q15 16 14 27M67 101v14m18-18v18m-27 0h18m1 0h18"/><circle cx="99" cy="42" r="2" fill="currentColor"/><path d="M107 55q18 17 3 19M55 64q25-5 22 22"/></>,
  lotus:<><path d="M80 92Q42 61 80 16Q118 61 80 92ZM80 92Q28 91 25 42Q73 49 80 92ZM80 92Q132 91 135 42Q87 49 80 92ZM80 92Q30 113 9 72Q47 65 80 92ZM80 92Q130 113 151 72Q113 65 80 92ZM80 92v22M45 115h70"/></>,
  leaf:<><path d="M82 111V25M82 64Q39 49 39 10Q84 19 82 64ZM82 82Q120 66 123 26Q82 35 82 82ZM82 100Q42 88 34 54Q76 58 82 100ZM82 107Q124 99 132 62Q89 67 82 107ZM66 112h32"/><path d="M48 23l28 31M115 40L88 72M46 65l30 25M120 76l-30 23" opacity=".5"/></>,
  lamp:<><path d="M24 77q56 53 112 0ZM80 75Q51 46 81 12Q109 44 80 75ZM50 99h60M61 102l-10 11h58l-10-11M38 70q42 16 84 0"/><path d="M80 64q-10-13 0-28q12 17 0 28Z" fill="currentColor" opacity=".25"/></>,
  smoke:<><path d="M37 79q43 46 86 0ZM73 99v12H56v7h48v-7H87V99M54 68q-21-17-3-29q17-13 0-27M79 67q21-16 1-31q-13-10 4-23M106 66q-16-13 0-25q20-15 3-29"/><path d="M44 76h72"/></>,
  drum:<><path d="M44 29Q80 15 116 29v65q-36 19-72 0ZM44 29q36 18 72 0M44 94q36-14 72 0M44 35l36 59 36-59M44 86l36-50 36 50M35 15L17 52m115-37 14 37"/><path d="M54 23l5-10m22 7V8m21 15 4-10"/></>,
  trident:<><path d="M80 112V13M79 16l-8 15m9-18 9 18M45 20v31q0 24 35 24q35 0 35-24V20M45 20l-9 15m9-15 9 15M115 20l-9 15m9-15 9 15M70 90h20M72 96h16"/><path d="M33 110q14-20 32-10m30 0q18-10 32 10"/></>
 }
 return <svg viewBox="0 0 160 130" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind]}</svg>
}
