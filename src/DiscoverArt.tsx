import { useId } from 'react'

/** Authored vector artwork, inspired by festive paper craft; not a ritual diagram. */
export function DeviArt(){
 const id=useId().replace(/:/g,'')
 return <figure className="devi-art">
  <svg viewBox="0 0 600 650" role="img" aria-labelledby={`${id}-title`}>
   <title id={`${id}-title`}>Maa Durga in vermilion and gold, surrounded by a floral halo, shiuli blossoms and autumn grasses. Original symbolic artwork.</title>
   <defs>
    <linearGradient id={`${id}-face`} x1="0" y1="0" x2="1" y2="1"><stop stopColor="#f4d39b"/><stop offset="1" stopColor="#dba55d"/></linearGradient>
    <linearGradient id={`${id}-red`} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#b43d2c"/><stop offset="1" stopColor="#70241f"/></linearGradient>
   </defs>
   <g className="festival-halo">
    <circle cx="300" cy="310" r="262" fill="#e9d9b8"/>
    <circle cx="300" cy="310" r="245" fill="none" stroke="#a42c24" strokeWidth="1"/>
    {Array.from({length:24},(_,i)=><g key={i} transform={`rotate(${i*15} 300 310)`}>
     <path d="M300 49Q271 79 300 111Q329 79 300 49Z" fill={i%2?'#f8f1e3':'#b44b35'} stroke="#9a5038" strokeWidth=".7"/>
     <path d="M300 61v38" stroke={i%2?'#aa392b':'#f8f1e3'} strokeWidth="1"/>
     <circle cx="300" cy="38" r="3" fill="#a42c24"/>
    </g>)}
    <circle cx="300" cy="310" r="204" fill={`url(#${id}-red)`}/>
    <circle cx="300" cy="310" r="194" fill="none" stroke="#e9c077" strokeDasharray="1 8" strokeWidth="3"/>
   </g>
   <g stroke="#763127" strokeLinejoin="round">
    <path d="M183 310Q130 412 185 519Q300 575 415 519Q470 412 417 310Z" fill="#412622"/>
    <path d="M207 265Q180 362 213 433Q244 490 300 510Q356 490 387 433Q420 362 393 265Z" fill={`url(#${id}-face)`} strokeWidth="2"/>
    <path d="M208 326Q173 304 168 343Q167 377 202 375M392 326Q427 304 432 343Q433 377 398 375" fill="#e8b779" strokeWidth="2"/>
    <path d="M186 279Q179 201 227 181Q227 128 265 139Q279 82 300 66Q321 82 335 139Q373 128 373 181Q421 201 414 279Z" fill="#ead5a6" strokeWidth="2"/>
    <path d="M201 259Q300 215 399 259L399 275Q300 235 201 275Z" fill="#b43d2c"/>
    <path d="M300 94Q256 147 300 204Q344 147 300 94Z" fill="#ab3629"/>
    <path d="M300 117Q275 150 300 183Q325 150 300 117Z" fill="#edc67b"/>
    <path d="M247 161Q214 190 245 218Q277 190 247 161ZM353 161Q386 190 355 218Q323 190 353 161Z" fill="#d7a24f"/>
    <path d="M241 179q-10 13 3 22m112-22q10 13-3 22" fill="none" stroke="#f8f1e3" strokeWidth="2"/>
    {Array.from({length:9},(_,i)=><g key={i} transform={`translate(${214+i*21.5} ${259-Math.sin(i/8*Math.PI)*20})`}><path d="M0-5l4 5-4 5-4-5Z" fill="#f4dfae" stroke="none"/></g>)}
    <path d="M218 317Q246 299 277 314M323 314Q354 299 382 317" fill="none" stroke="#412622" strokeWidth="5" strokeLinecap="round"/>
    <path d="M207 338Q244 322 278 344Q244 370 214 350L207 338ZM393 338Q356 322 322 344Q356 370 386 350L393 338Z" fill="#fff8e8" stroke="#412622" strokeWidth="2"/>
    <path d="M207 338l-13-12M393 338l13-12" fill="none" stroke="#412622" strokeWidth="3"/>
    <ellipse cx="247" cy="345" rx="8" ry="13" fill="#412622" stroke="none"/><ellipse cx="353" cy="345" rx="8" ry="13" fill="#412622" stroke="none"/>
    <circle cx="249" cy="341" r="2" fill="#fff8e8" stroke="none"/><circle cx="351" cy="341" r="2" fill="#fff8e8" stroke="none"/>
    <path d="M300 279Q281 301 300 319Q319 301 300 279Z" fill="#a42c24" stroke="none"/><path d="M300 287v23" stroke="#f8f1e3"/>
    <path d="M292 359Q282 399 303 402" fill="none" strokeWidth="1.2"/>
    <path d="M279 438Q300 427 321 438Q300 455 279 438Z" fill="#a42c24" strokeWidth="1"/>
    <path d="M283 438h34M283 470q17 7 34 0" stroke="#e5b172" strokeWidth="1"/>
    <circle cx="320" cy="406" r="23" fill="none" stroke="#fff0c4" strokeWidth="3"/><circle cx="338" cy="421" r="4" fill="#a42c24" stroke="#fff0c4" strokeWidth="2"/>
    <path d="M186 377q-38 38 0 61q38-23 0-61ZM414 377q-38 38 0 61q38-23 0-61Z" fill="#e8c777" strokeWidth="1.5"/>
    <circle cx="186" cy="410" r="8" fill="#a42c24"/><circle cx="414" cy="410" r="8" fill="#a42c24"/>
    <path d="M228 482Q300 560 372 482L384 513Q300 583 216 513Z" fill="#ead5a6"/>
    {Array.from({length:11},(_,i)=><circle key={i} cx={233+i*13.4} cy={520+Math.sin(i/10*Math.PI)*29} r="4" fill="#a42c24" stroke="none"/>)}
   </g>
   <g className="autumn-stems" fill="none" stroke="#947855" strokeWidth="1.2">
    <path d="M44 616Q108 483 83 371M68 624Q131 536 136 424M556 616Q492 483 517 371M532 624Q469 536 464 424"/>
    {Array.from({length:9},(_,i)=><g key={i} transform={`translate(${83+i*1.2} ${389+i*9}) rotate(${i*2})`}><path d="M0 0q-22-14-23-29M0 0q16-18 15-34M0 0q-12-14-12-32" stroke="#d5c29e" strokeWidth="3"/></g>)}
    {Array.from({length:9},(_,i)=><g key={i} transform={`translate(${517-i*1.2} ${389+i*9}) rotate(${-i*2})`}><path d="M0 0q22-14 23-29M0 0q-16-18-15-34M0 0q12-14 12-32" stroke="#d5c29e" strokeWidth="3"/></g>)}
   </g>
   {[['112','552','-15'],['488','552','15'],['150','583','20'],['450','583','-20']].map(([x,y,r],i)=><g key={i} transform={`translate(${x} ${y}) rotate(${r})`}>
    {Array.from({length:5},(_,j)=><ellipse key={j} cx="0" cy="-12" rx="7" ry="13" transform={`rotate(${j*72})`} fill="#fffaf1" stroke="#d6c6aa" strokeWidth=".8"/>)}<circle r="5" fill="#bd542b"/>
   </g>)}
   <path d="M216 597h168m-154 7h140" fill="none" stroke="#b38f58"/>
  </svg>
  <figcaption><span lang="bn">শক্তি</span> · A homecoming, drawn in the colours of autumn</figcaption>
 </figure>
}

export type Motif='elephant'|'horse'|'boat'|'lotus'|'leaf'|'lamp'|'smoke'|'drum'|'trident'
export function MotifArt({kind}:{kind:Motif}){
 const paths:Record<Motif,React.ReactNode>={
  elephant:<><path d="M22 84V53q0-22 26-22h41q19-15 34-1q12 12 6 29v23q0 22 16 17q12-6 2-20M28 68v31h15V77h38v22h15V62M102 44q-20-10-23 7q-3 18 13 19q15-2 10-26ZM22 44Q9 49 12 68"/><path d="M37 33v26h35V33M38 59l18 10 16-10M118 57l12 6"/><circle cx="117" cy="40" r="2" fill="currentColor"/></>,
  horse:<><path d="M28 65Q17 45 25 31M28 65l17-18h49l13-22 10-10 4 13 19 16-3 12-22-4-9 20-7 33h-9l1-32-35-1-12 33h-9l6-40ZM106 26q-24 8-23 24M116 18l-7-8-5 20M55 50v20h28V50"/><circle cx="124" cy="35" r="1.5" fill="currentColor"/><path d="M28 113h105"/></>,
  boat:<><path d="M12 79Q80 132 148 79Q88 95 12 79ZM30 81l16-18h70l13 20M80 62V14M84 17l43 41H84ZM74 21L40 57h34M11 113q12-7 24 0t24 0t24 0t24 0t24 0t24 0"/><path d="M35 75h82"/></>,
  lotus:<><path d="M80 92Q42 61 80 16Q118 61 80 92ZM80 92Q28 91 25 42Q73 49 80 92ZM80 92Q132 91 135 42Q87 49 80 92ZM80 92Q30 113 9 72Q47 65 80 92ZM80 92Q130 113 151 72Q113 65 80 92ZM80 92v22M45 115h70"/></>,
  leaf:<><path d="M82 111V25M82 64Q39 49 39 10Q84 19 82 64ZM82 82Q120 66 123 26Q82 35 82 82ZM82 100Q42 88 34 54Q76 58 82 100ZM82 107Q124 99 132 62Q89 67 82 107ZM66 112h32"/><path d="M48 23l28 31M115 40L88 72M46 65l30 25M120 76l-30 23" opacity=".5"/></>,
  lamp:<><path d="M24 77q56 53 112 0ZM80 75Q51 46 81 12Q109 44 80 75ZM50 99h60M61 102l-10 11h58l-10-11M38 70q42 16 84 0"/><path d="M80 64q-10-13 0-28q12 17 0 28Z" fill="currentColor" opacity=".2"/></>,
  smoke:<><path d="M37 79q43 46 86 0ZM73 99v12H56v7h48v-7H87V99M54 68q-21-17-3-29q17-13 0-27M79 67q21-16 1-31q-13-10 4-23M106 66q-16-13 0-25q20-15 3-29"/><path d="M44 76h72"/></>,
  drum:<><path d="M44 29Q80 15 116 29v65q-36 19-72 0ZM44 29q36 18 72 0M44 94q36-14 72 0M44 35l36 59 36-59M44 86l36-50 36 50M35 15L17 52m115-37 14 37"/><path d="M54 23l5-10m22 7V8m21 15 4-10"/></>,
  trident:<><path d="M80 112V13M79 16l-8 15m9-18 9 18M45 20v31q0 24 35 24q35 0 35-24V20M45 20l-9 15m9-15 9 15M115 20l-9 15m9-15 9 15M70 90h20M72 96h16"/><path d="M33 110q14-20 32-10m30 0q18-10 32 10"/></>
 }
 return <svg viewBox="0 0 160 130" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind]}</svg>
}

export function PowerArt(){return <svg viewBox="0 0 500 500" fill="none" stroke="currentColor" aria-hidden="true">
 <g className="festival-halo" style={{transformOrigin:'250px 250px'}}><circle cx="250" cy="250" r="221" opacity=".45"/><circle cx="250" cy="250" r="208" opacity=".45"/>{Array.from({length:16},(_,i)=><g key={i} transform={`rotate(${i*22.5} 250 250)`}><path d="M250 42Q220 75 250 106Q280 75 250 42Z"/><circle cx="250" cy="24" r="3" fill="currentColor"/></g>)}</g>
 <path d="M250 388V109m0 0-16 28m16-28 16 28M184 129v72q0 50 66 50t66-50v-72m-132 0-16 29m16-29 16 29m116-29-16 29m16-29 16 29M228 308h44m-40 15h36" strokeWidth="3" strokeLinecap="round"/>
 <path d="M176 367q74-34 148 0M194 387q56-25 112 0" strokeWidth="1.5"/>
</svg>}

export function PandalArt(){return <svg viewBox="0 0 430 420" fill="none" stroke="currentColor" strokeWidth="1.3" aria-hidden="true">
 <circle cx="215" cy="190" r="170" fill="#e9d9b8" stroke="none"/><path d="M32 370h366M55 357h320M74 344h282M90 332h250M91 171h248v161H91ZM77 171l138-114 138 114ZM96 157l119-85 119 85ZM109 182v137m212-137v137M130 182v137m170-137v137M153 332V219q62-87 124 0v113M166 332V224q49-67 98 0v108"/>
 <path d="M215 59V32m-7 10h14M114 171v-24m202 24v-24"/><circle cx="215" cy="130" r="17"/><path d="M208 128q7-9 14 0m-12 9h10"/>
 <path d="M195 320V261q20-38 40 0v59ZM188 286l-17-16m24 3-17-25m57 38 17-16m-17 3 17-25M204 260q11-13 22 0M202 275q5-5 9 0m7 0q5-5 9 0"/>
 <path d="M30 370V238m0 43q-27-29-17-48q26 7 17 48m0 29q31-23 27-42q-25 0-27 42M400 370V238m0 43q27-29 17-48q-26 7-17 48m0 29q-31-23-27-42q25 0 27 42"/>
 <path d="M46 382q35 13 70 0t70 0t70 0t70 0t70 0" strokeDasharray="1 5" strokeWidth="3"/>
</svg>}
