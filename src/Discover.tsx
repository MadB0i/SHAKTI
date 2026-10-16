import { useEffect, useRef, useState } from 'react'
import { DeviArt, MotifArt, PowerArt, PandalArt, type Motif } from './DiscoverArt'
import './discover.css'

const PANCHANG='https://www.drikpanchang.com/navratri/durga-puja/durga-puja-calendar.html?year=2026&geoname-id=1275004'
const REGIONAL_VEHICLES='https://www.anandabazar.com/horoscope/know-maa-durgas-arrival-and-departure-vehicles-and-their-significance-dgtl/cid/1716549'
const REGIONAL_DATES='https://www.anandabazar.com/horoscope/time-and-fixture-of-durga-puja-2026-as-per-visuddha-siddhanta-and-guptapress-panjika-dgtl/cid/1714037'
const COMMUNITY_PANJIKA='https://banerul.com/panjika/'
const ASSAM_HORSE_REPORT='https://asomlive24.com/shardiya-navratri-2026/'
const ASSAM_BOAT_REPORT='https://dainikagradoot.in/blog/2026/09/29/দুই-লক্ষাধিক-ভক্তক-আদৰিব/'
const UNESCO='https://ich.unesco.org/en/RL/durga-puja-in-kolkata-00703'
const COMMUNITY_HISTORY='https://indianexpress.com/article/research/from-kings-and-landlords-to-communities-and-corporates-the-changing-face-of-durga-puja-10274328/'
const PRINCETON='https://artmuseum.princeton.edu/art/collections/objects/87648'
const ASSAM='https://assamtourism.gov.in/Kamakhya-Temple.php'
const RITUAL_BASE='https://www.drikpanchang.com/navratri/'
const days=[
 {date:16,weekday:'Friday',name:'Shashthi',bengali:'29 Ashwin · 1433',title:'An invitation to the Goddess',text:'Bilva Nimantran begins the invitation. The bel tree has a sacred place in this rite.'},
 {date:17,weekday:'Saturday',name:'Shashthi',bengali:'30 Ashwin · 1433',title:'The awakening · Bodhan',text:'Kalparambha, Akal Bodhan, Amantran and Adhivas mark the ritual beginning and welcome.'},
 {date:18,weekday:'Sunday',name:'Saptami',bengali:'1 Kartik · 1433',title:'Nature enters the celebration',text:'Saptami brings Navapatrika worship, also called Kolabou Puja in Bengal.'},
 {date:19,weekday:'Monday',name:'Ashtami',bengali:'2 Kartik · 1433',title:'At the sacred threshold',text:'Ashtami worship and Sandhi Puja lead into Navami rites; this calendar also lists Maha Navami on the 19th.'},
 {date:20,weekday:'Tuesday',name:'Navami',bengali:'3 Kartik · 1433',title:'Offerings and completion',text:'Navami Homa is listed here, alongside Vijayadashami and Durga Visarjan in the broader observance calendar.'},
 {date:21,weekday:'Wednesday',name:'Dashami',bengali:'4 Kartik · 1433',title:'A farewell, until next autumn',text:'Bengal Vijayadashami, immersion and Sindoor Utsav complete this Bengali festival sequence.'}
]
const rituals:{name:string;kind:Motif;intro:string;more:string;source:string}[]=[
 {name:'Navapatrika',kind:'leaf',intro:'Nine plants become a living offering: nature gathered into the worship of the Goddess.',more:'Often called Kolabou in Bengal, the bundle includes a banana plant. Its ritual bathing and worship belong to Saptami; meanings and practice vary by tradition.',source:RITUAL_BASE+'durga-puja/navpatrika-puja-date-time.html?year=2026&geoname-id=1275004'},
 {name:'Pushpanjali',kind:'lotus',intro:'Flowers held in joined palms. A quiet, collective gesture of devotion.',more:'Devotees offer flowers with prayers and mantras. Ashtami anjali is especially familiar in Bengali celebrations, while offerings also occur on other puja days.',source:RITUAL_BASE+'durga-puja/info/durga-puja-pushpanjali.html'},
 {name:'Sandhi Puja',kind:'lamp',intro:'An offering at the meeting of Ashtami and Navami, when one sacred moment becomes another.',more:'The traditional interval spans about 48 minutes around the tithi transition. In devotional belief it recalls Chamunda’s defeat of Chanda and Munda. It need not fall at night; consult the local panjika for timing.',source:RITUAL_BASE+'shardiya-navratri-sandhipuja.html?year=2026&geoname-id=1275004'},
 {name:'Dhunuchi naach',kind:'smoke',intro:'Incense rises from earthen vessels as dancers move before the Goddess.',more:'Dhunuchi dance is commonly accompanied by the dhaak. The vessel, fragrant smoke and rhythm turn an offering into a shared performance.',source:RITUAL_BASE+'durga-puja/info/durga-puja-dhunuchi-dance.html'},
 {name:'The sound of dhaak',kind:'drum',intro:'The great drum gives the festival its pulse: a call that carries across a neighbourhood.',more:'Dhaakis are the drummers whose performance accompanies worship and dance. Their work is part of the festival’s living network of skilled makers and performers.',source:UNESCO},
 {name:'Visarjan & Bijoya',kind:'lotus',intro:'The image returns to water. Farewell becomes an exchange of affection and good wishes.',more:'In Bengal, Bijoya greetings follow the farewell. Sindoor Khela, traditionally associated with married women, is one custom of Dashami; participation and practice differ between communities.',source:UNESCO}
]
function Source({href,children}:{href:string;children:React.ReactNode}){return <a className="source-link" href={href} target="_blank" rel="noreferrer">{children} <span aria-hidden="true">↗</span></a>}
function initialDay(){const n=Number(new URLSearchParams(location.search).get('day'));return days.some(d=>d.date===n)?n:16}

export default function Discover(){
 const root=useRef<HTMLDivElement>(null)
 const [selected,setSelected]=useState(initialDay)
 const [motion,setMotion]=useState(()=>!matchMedia('(prefers-reduced-motion: reduce)').matches)
 const [reduced,setReduced]=useState(()=>matchMedia('(prefers-reduced-motion: reduce)').matches)
 const [chapter,setChapter]=useState('calendar')
 const day=days.find(d=>d.date===selected)!
 useEffect(()=>{
  const query=matchMedia('(prefers-reduced-motion: reduce)')
  const sync=()=>{setReduced(query.matches);setMotion(!query.matches)}
  query.addEventListener('change',sync)
  return()=>query.removeEventListener('change',sync)
 },[])
 useEffect(()=>{
  if(!root.current||!('IntersectionObserver' in window))return
  const reveals=new IntersectionObserver(entries=>entries.forEach(entry=>{
   if(entry.isIntersecting){entry.target.classList.add('revealed');reveals.unobserve(entry.target)}
  }),{threshold:.12})
  root.current.querySelectorAll('.section-intro,.history-list li,.ritual-card,.vehicle,.myth-copy,.heritage-plate').forEach(el=>reveals.observe(el))
  const chapters=new IntersectionObserver(entries=>entries.forEach(entry=>{
   if(entry.isIntersecting)setChapter(entry.target.id)
  }),{rootMargin:'-15% 0px -55% 0px'})
  root.current.querySelectorAll('#calendar,#mythology,#heritage,#rituals').forEach(el=>chapters.observe(el))
  return()=>{reveals.disconnect();chapters.disconnect()}
 },[])
 useEffect(()=>{document.title='The Story of Shakti · SHAKTI';document.querySelector('meta[name="description"]')?.setAttribute('content','Explore Durga Puja: the 2026 Bengali calendar, mythology, living traditions and the cultural histories of Bengal and Assam.');const sync=()=>setSelected(initialDay());window.addEventListener('popstate',sync);return()=>window.removeEventListener('popstate',sync)},[])
 const selectDay=(date:number)=>{setSelected(date);const url=new URL(location.href);url.searchParams.set('day',String(date));history.replaceState(null,'',url)}
 return <div className="discover" ref={root} data-motion={motion?'on':'off'}>
  <a className="skip-link" href="#story">Skip to the story</a>
  <header className="museum-header">
   <a className="wordmark" href={import.meta.env.BASE_URL} aria-label="SHAKTI — return to the film">SHAKTI</a>
   <span className="museum-edition">The autumn annual · No. 01</span>
   <nav aria-label="Primary"><a href={import.meta.env.BASE_URL}>The film <span aria-hidden="true">↗</span></a><a href="#sources-title">Sources</a><button className="motion-toggle" disabled={reduced} title={reduced?'Your system prefers reduced motion':undefined} aria-label={reduced?'Reduced motion':motion?'Pause motion':'Resume motion'} onClick={()=>setMotion(v=>!v)}><span aria-hidden="true">{motion?'Ⅱ':'▷'}</span> <span className="motion-label">{reduced?'Reduced motion':motion?'Pause motion':'Resume motion'}</span></button></nav>
  </header>
  <main id="story" tabIndex={-1}>
   <section className="discover-hero" aria-labelledby="story-title">
    <div className="hero-copy"><p className="museum-kicker">When autumn feels like home</p><h1 id="story-title">The Story <em>of Shakti.</em></h1><p className="hero-deck">The first beat of the dhaak. Flowers in waiting hands. A goddess returning home.</p><div className="hero-foot"><a className="museum-link" href="#calendar">Explore Durga Puja <span aria-hidden="true">↓</span></a><span>Bengal & Assam · 2026</span></div></div>
    <DeviArt/>
    <p className="hero-season">Devotion · Art · Belonging</p>
   </section>
   <nav className="chapter-nav" aria-label="Story chapters"><span>Follow the story</span>{[['01','The calendar','calendar'],['02','The mythology','mythology'],['03','A living heritage','heritage'],['04','The rituals','rituals']].map(([n,name,id])=><a key={id} href={'#'+id} aria-current={chapter===id?'location':undefined}><span>{n}</span>{name}</a>)}</nav>
   <section id="calendar" className="museum-section" aria-labelledby="calendar-title">
    <div className="section-intro"><div><p className="section-number">01 / The homecoming</p><h2 id="calendar-title">Keep a little<br/>autumn in your heart.</h2></div><p>Six dates, many ways to celebrate. Explore 16–21 October 2026 through Drik Panchang’s Kolkata Bengali listing. The calendar tradition matters: other panjikas differ.</p></div>
    <div className="calendar-heading"><p>OCTOBER 2026 / BENGALI YEAR 1433</p><Source href={PANCHANG}>Kolkata calendar · Drik Panchang</Source></div>
    <fieldset className="calendar-fieldset"><legend className="sr-only">Choose a festival date in October 2026</legend><div className="calendar-days">{days.map(d=><label className="day-choice" key={d.date}><input type="radio" name="festival-date" value={d.date} checked={d.date===selected} onChange={()=>selectDay(d.date)} aria-label={`${d.date} October, ${d.name}`} aria-controls="day-description"/><span className="day-face"><span className="weekday">{d.weekday}</span><strong>{d.date}</strong><span className="day-name">{d.name}</span><span className="bengali-date">{d.bengali}</span></span></label>)}</div></fieldset>
    <div id="day-description" className="day-description" aria-live="polite" aria-atomic="true"><div key={day.date}><p className="section-number">{day.date} October / {day.name}</p><h3>{day.title}</h3></div><p>{day.text}</p></div>
    <p className="calendar-note"><strong>One calendar at a time.</strong> The dates above are a source-specific listing, not a universal timetable. Drik Panchang lists general Visarjan on Tuesday 20 October and Bengal Visarjan on Wednesday 21 October. Bengali panjikas also differ over Saptami. Confirm ritual times with your own temple or panjika.</p>
    <div className="correction-banner" id="calendar-correction"><span>2026 calendar correction</span><p><strong>Gaman: Nouka · Boat</strong> in the Bengali panjika comparison cited below. The earlier Rooster heading mixed calendar conventions. A Horse departure is not supported by this regional comparison.</p></div>
    <div className="belief-panel">
     <article className="vehicle"><div className="vehicle-pair"><MotifArt kind="elephant"/><MotifArt kind="horse"/></div><div><span className="section-number">Aagaman / Arrival · 2026</span><h3>Two panjikas.<br/>Two arrivals.</h3><p><strong>Gaja · Elephant</strong> in Bishuddha Siddhanta: Sunday Saptami, 18 October.<br/><strong>Ghotak · Horse</strong> in Gupta Press: Saturday Saptami, 17 October.</p></div></article>
     <article className="vehicle"><MotifArt kind="boat"/><div><span className="section-number">Gaman / Departure · 2026</span><h3>Nouka · Boat</h3><p>Anandabazar’s 2026 comparison reports Boat in both panjikas, using Wednesday Dashami, 21 October. This is a Bengali regional account, not an Assam-wide ruling.</p></div></article>
    </div>
    <p className="belief-qualification">Vehicle symbolism belongs to devotional tradition. These are reported regional interpretations, not scientific predictions. The calendar above retains Drik Panchang’s labels; the vehicle comparison is explicitly attributed to Bengali panjikas reported by Anandabazar on 1 October 2026.</p>
    <Source href={REGIONAL_VEHICLES}>Compare the two Bengali panjikas</Source>
    <details className="calendar-evidence"><summary>Why do the sources disagree?</summary><div className="evidence-body">
     <p><strong>The Bengali rule reported by Anandabazar uses Saptami for arrival and Dashami for departure.</strong> It applies the same weekday mapping to each:</p>
     <table className="rule-table"><caption>Bengali vehicle rule reported by Anandabazar</caption><thead><tr><th scope="col">Weekday</th><th scope="col">Traditional vehicle</th></tr></thead><tbody><tr><th scope="row">Sunday / Monday</th><td>Gaja · Elephant</td></tr><tr><th scope="row">Tuesday / Saturday</th><td>Ghotak · Horse</td></tr><tr><th scope="row">Wednesday</th><td>Nouka · Boat</td></tr><tr><th scope="row">Thursday / Friday</th><td>Dola · Palanquin</td></tr></tbody></table>
     <p><strong>Drik Panchang uses a different departure convention.</strong> Its omen page assigns Rooster to Tuesday or Saturday Visarjan. Its 2026 Kolkata page shows that label alongside Tuesday’s general Visarjan and Wednesday’s Bengal Visarjan. That combination cannot establish Rooster as the Bengali Wednesday departure. Nor does Tuesday’s tithi start establish Horse when the cited Bengali panjika selects Wednesday’s sunrise Dashami.</p>
     <p><strong>Assam’s reporting also conflicts.</strong> Asom Live 24 (22 September 2026) reports Horse departure in a Navratri account with Vijayadashami on Tuesday 20 October; it does not identify a panjika edition or publish the weekday mapping. Dainik Agradoot’s 29 September 2026 report on Bilweswar Devalaya says Horse arrival and Boat departure. Neither establishes one rule for all of Assam. Horse departure remains unverified for an Assam-wide label.</p>
     <Source href={ASSAM_HORSE_REPORT}>Asom Live 24 · Horse report</Source><br/><Source href={ASSAM_BOAT_REPORT}>Dainik Agradoot · Bilweswar report</Source>
     <p>Assam Tourism documents Kamakhya’s distinct fifteen-day Pakhuva Puja but gives no 2026 vehicle determination. Follow the panjika used by the local puja; the Kolkata sequence above is not a substitute.</p>
     <Source href={RITUAL_BASE+'durga-puja/omen/durga-departure-on-rooster.html'}>Drik Panchang’s departure convention</Source><br/><Source href={REGIONAL_DATES}>Bengali panjika date comparison</Source><br/><Source href={COMMUNITY_PANJIKA}>Community cross-check · Nerul Bengali panjika</Source>
    </div></details>
   </section>
   <section id="mythology" className="museum-section myth-spread" aria-labelledby="myth-title">
    <div className="myth-emblem"><PowerArt/><span>SHAKTI / DIVINE POWER</span></div>
    <div className="myth-copy"><span className="section-number">02 / Sacred narrative</span><h2 id="myth-title">The power to<br/>restore balance.</h2><p className="myth-pull">In the Devi Mahatmya tradition, Maa Durga confronts and defeats Mahishasura, the buffalo demon.</p><p>For devotees, the story speaks of the Goddess’s protective power and the restoration of cosmic order. Her many arms and weapons give visible form to a power beyond ordinary human limits.</p><p>In Bengal’s homecoming imagination, the warrior is also a beloved daughter returning to her family. These are devotional narratives and interpretations, rather than documented historical events.</p><Source href={PRINCETON}>Devi Mahatmya · Princeton University Art Museum</Source>{' · '}<Source href="https://www.metmuseum.org/art/collection/search/38583">Durga’s imagery · The Met</Source></div>
   </section>
   <section id="heritage" className="museum-section" aria-labelledby="heritage-title">
    <div className="section-intro"><div><span className="section-number">03 / A living heritage</span><h2 id="heritage-title">From the courtyard<br/>to the whole city.</h2></div><p>Durga worship has a long history. The public festival we know today took shape through changing patronage, shared organisation and generations of artistic labour.</p></div>
    <div className="heritage-layout"><figure className="heritage-plate"><PandalArt/><figcaption>A temporary home for an enduring tradition. Original symbolic pandal illustration.</figcaption></figure><ol className="history-list">
     <li><span className="era">12th century</span><h3>An older image</h3><p>A surviving Bengal-region sculpture of Durga slaying the buffalo demon is held by The Met. It documents an established iconography, not the start date of today’s festival.</p><Source href="https://www.metmuseum.org/art/collection/search/38583">The Met · object 1993.7</Source></li>
     <li><span className="era">Early modern Bengal</span><h3>The family courtyard</h3><p>Landholding and wealthy families became influential patrons of elaborate autumn pujas. Bonedi bari celebrations continue distinct household traditions; no single origin story accounts for every puja.</p><Source href={COMMUNITY_HISTORY}>Historical research · Indian Express</Source></li>
     <li><span className="era">The public festival</span><h3>A shared celebration</h3><p>Barowari and later sarbojanin pujas widened collective organisation. Neighbourhood committees, craftspeople and visitors helped transform the celebration into a public cultural event.</p><Source href={COMMUNITY_HISTORY}>Historians’ interviews · Indian Express</Source></li>
     <li><span className="era">2021</span><h3>Living world heritage</h3><p>“Durga Puja in Kolkata” was inscribed on UNESCO’s Representative List of the Intangible Cultural Heritage of Humanity, recognising a living tradition of worship, creativity and collaboration.</p><Source href={UNESCO}>UNESCO · inscription</Source></li>
    </ol></div>
   </section>
   <section id="rituals" className="museum-section rituals" aria-labelledby="rituals-title">
    <div className="section-intro"><div><span className="section-number">04 / The gestures that endure</span><h2 id="rituals-title">Flowers. Fire. Rhythm.</h2></div><p>Small acts carry a vast inheritance. These are introductions to living practices, whose forms differ across families, temples and communities.</p></div>
    <div className="ritual-grid">{rituals.map((r,i)=><article className="ritual-card" key={r.name}><span className="ritual-index" aria-hidden="true">0{i+1}</span><div className="ritual-art"><MotifArt kind={r.kind}/></div><h3>{r.name}</h3><p>{r.intro}</p><details><summary>Explore {r.name}</summary><p>{r.more}</p><Source href={r.source}>Source for {r.name}</Source></details></article>)}</div>
   </section>
   <section className="museum-section regional" aria-labelledby="region-title">
    <div><span className="section-number">Two regions / Many expressions</span><h2 id="region-title">A shared devotion.<br/>Distinct local worlds.</h2><h3>Bengal</h3><p>In Kolkata, temporary pandals become spaces for worship and ambitious public art. Clay image-making, design, performance and neighbourhood participation sustain the festival’s creative life.</p><Source href={UNESCO}>UNESCO · Durga Puja in Kolkata</Source></div>
    <div className="assam-column"><span className="region-marker">On the Nilachal hills</span><h3>Assam</h3><p>Assam has its own traditions of Goddess worship alongside community Durga Pujas. At Guwahati’s Kamakhya temple, Assam Tourism describes a fifteen-day Pakhuva Puja, observed without an image of the deity.</p><p>That temple practice is distinct from the Bengali calendar shown above. One region’s observance should not stand in for every community’s.</p><Source href={ASSAM}>Assam Tourism · Kamakhya</Source></div>
   </section>
   <aside className="museum-section reading-room" aria-labelledby="sources-title">
    <div><h2 id="sources-title">The reading room</h2><p>Calendar correction checked 16 October 2026.<br/>Original editorial text and symbolic vector art. Mythology, belief and documented history are identified in context. Panjika claims below are reported comparisons; publisher pages were not independently inspected.</p></div>
    <ul className="source-list"><li><a href={REGIONAL_VEHICLES} target="_blank" rel="noreferrer">Anandabazar ↗</a><span>2026 regional vehicle comparison</span></li><li><a href={PANCHANG} target="_blank" rel="noreferrer">Drik Panchang ↗</a><span>Kolkata 2026 · separate calendar convention</span></li><li><a href={UNESCO} target="_blank" rel="noreferrer">UNESCO ↗</a><span>Durga Puja in Kolkata · 2021 inscription</span></li><li><a href={PRINCETON} target="_blank" rel="noreferrer">Princeton University Art Museum ↗</a><span>Devi Mahatmya & cosmic balance</span></li><li><a href="https://www.metmuseum.org/art/collection/search/38583" target="_blank" rel="noreferrer">The Metropolitan Museum of Art ↗</a><span>Bengal-region Durga sculpture · 12th century</span></li><li><a href={COMMUNITY_HISTORY} target="_blank" rel="noreferrer">Indian Express ↗</a><span>Historians on family & public pujas</span></li><li><a href={ASSAM} target="_blank" rel="noreferrer">Assam Tourism ↗</a><span>Kamakhya & local worship traditions</span></li></ul>
   </aside>
  </main>
  <footer className="museum-footer"><div><a className="wordmark" href={import.meta.env.BASE_URL}>SHAKTI</a><p>Created by Rupjyoti Talukdar · MadB0i</p></div><nav aria-label="Footer"><a href={import.meta.env.BASE_URL}>Return to the film ↗</a><a href={import.meta.env.BASE_URL+'credits.html'}>Credits</a></nav></footer>
 </div>
}
