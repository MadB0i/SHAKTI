import { useEffect, useState } from 'react'
import { DeviArt, MotifArt, type Motif } from './DiscoverArt'
import './discover.css'

const PANCHANG='https://www.drikpanchang.com/navratri/durga-puja/durga-puja-calendar.html?year=2026&geoname-id=1275004'
const UNESCO='https://ich.unesco.org/en/RL/durga-puja-in-kolkata-00703'
const HISTORY='https://www.utsav.gov.in/public/view-event/durga-puja-2'
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
 {name:'Visarjan & Bijoya',kind:'lotus',intro:'The image returns to water. Farewell becomes an exchange of affection and good wishes.',more:'In Bengal, Bijoya greetings follow the farewell. Sindoor Khela, traditionally associated with married women, is one custom of Dashami; participation and practice differ between communities.',source:HISTORY}
]
function Source({href,children}:{href:string;children:React.ReactNode}){return <a className="source-link" href={href} target="_blank" rel="noreferrer">{children} <span aria-hidden="true">↗</span></a>}
function initialDay(){const n=Number(new URLSearchParams(location.search).get('day'));return days.some(d=>d.date===n)?n:16}

export default function Discover(){
 const [selected,setSelected]=useState(initialDay)
 const day=days.find(d=>d.date===selected)!
 useEffect(()=>{document.title='The Story of Shakti · SHAKTI';document.querySelector('meta[name="description"]')?.setAttribute('content','Explore Durga Puja: the 2026 Bengali calendar, mythology, living traditions and the cultural histories of Bengal and Assam.');const sync=()=>setSelected(initialDay());window.addEventListener('popstate',sync);return()=>window.removeEventListener('popstate',sync)},[])
 const selectDay=(date:number)=>{setSelected(date);const url=new URL(location.href);url.searchParams.set('day',String(date));history.replaceState(null,'',url)}
 return <div className="discover">
  <a className="skip-link" href="#story">Skip to the story</a>
  <header className="museum-header">
   <a className="wordmark" href={import.meta.env.BASE_URL} aria-label="SHAKTI — return to the film">SHAKTI</a>
   <span className="museum-edition">A CELEBRATION OF THE DIVINE FEMININE</span>
   <nav aria-label="Primary"><a href={import.meta.env.BASE_URL}>The film <span aria-hidden="true">↗</span></a><a href={import.meta.env.BASE_URL+'discover/'} aria-current="page">The story</a></nav>
  </header>
  <main id="story">
   <section className="discover-hero" aria-labelledby="story-title">
    <div className="hero-copy"><p className="museum-kicker">Beyond the first flame</p><h1 id="story-title">The Story <em>of Shakti.</em></h1><p className="hero-deck">A goddess. A homecoming. A culture that creates itself anew, every autumn.</p><div className="hero-foot"><a className="museum-link" href="#calendar">Explore Durga Puja <span aria-hidden="true">↓</span></a><span>BENGAL & ASSAM · 2026</span></div></div>
    <DeviArt/>
   </section>
   <nav className="chapter-nav" aria-label="Story chapters"><span>IN THIS STORY</span>{[['01','The calendar','calendar'],['02','The mythology','mythology'],['03','A living heritage','heritage'],['04','The rituals','rituals']].map(([n,name,id])=><a key={id} href={'#'+id}><span>{n}</span>{name}</a>)}</nav>
   <section id="calendar" className="museum-section" aria-labelledby="calendar-title">
    <div className="section-intro"><div><p className="section-number">01 / The homecoming</p><h2 id="calendar-title">Six dates.<br/>An autumn of devotion.</h2></div><p>16–21 October 2026, following Drik Panchang’s Kolkata Bengali festival listing. Select a date to explore its observances.</p></div>
    <div className="calendar-heading"><p>OCTOBER 2026 / BENGALI YEAR 1433</p><Source href={PANCHANG}>Kolkata calendar · Drik Panchang</Source></div>
    <fieldset className="calendar-fieldset"><legend className="sr-only">Choose a festival date in October 2026</legend><div className="calendar-days">{days.map(d=><label className="day-choice" key={d.date}><input type="radio" name="festival-date" value={d.date} checked={d.date===selected} onChange={()=>selectDay(d.date)} aria-label={`${d.date} October, ${d.name}`} aria-controls="day-description"/><span className="day-face"><span className="weekday">{d.weekday}</span><strong>{d.date}</strong><span className="day-name">{d.name}</span><span className="bengali-date">{d.bengali}</span></span></label>)}</div></fieldset>
    <div id="day-description" className="day-description" aria-live="polite" aria-atomic="true"><div><p className="section-number">{day.date} October / {day.name}</p><h3>{day.title}</h3></div><p>{day.text}</p></div>
    <p className="calendar-note"><span>A note on calendars</span>Tithis cross civil dates. Shashthi appears twice here; many all-India calendars observe Vijayadashami on 20 October, while this listing places Bengal immersion on 21 October. Local panjikas and temple practice may differ. Confirm ritual timings locally.</p>
    <div className="belief-panel">
     <article className="vehicle"><MotifArt kind="elephant"/><div><span className="section-number">Traditional arrival / 2026</span><h3>Gaja · Elephant</h3><p>The elephant is associated in devotional tradition with abundance and rain.</p></div></article>
     <article className="vehicle"><MotifArt kind="rooster"/><div><span className="section-number">Traditional departure / 2026</span><h3>Charanayudha · Rooster</h3><p>A departure motif traditionally interpreted as an omen of unrest.</p></div></article>
    </div>
    <p className="belief-qualification">These are Drik Panchang’s 2026 vehicle labels, not a universal regional consensus. Its departure rule uses the Visarjan weekday and associates the rooster with Tuesday; Bengal’s Wednesday immersion listing should not be used to infer the same vehicle. These are religious beliefs, not scientific predictions.</p>
    <Source href={RITUAL_BASE+'durga-puja/omen/durga-arrival-on-elephant.html'}>Arrival tradition</Source>{' · '}<Source href={RITUAL_BASE+'durga-puja/omen/durga-departure-on-rooster.html'}>Departure tradition & weekday rule</Source>
   </section>
   <section id="mythology" className="museum-section myth-spread" aria-labelledby="myth-title">
    <div className="myth-emblem"><MotifArt kind="trident"/><span>SHAKTI / DIVINE POWER</span></div>
    <div className="myth-copy"><span className="section-number">02 / Sacred narrative</span><h2 id="myth-title">The power to<br/>restore balance.</h2><p className="myth-pull">In the Devi Mahatmya tradition, Maa Durga confronts and defeats Mahishasura, the buffalo demon.</p><p>For devotees, the story speaks of the Goddess’s protective power and the restoration of cosmic order. Her many arms and weapons give visible form to a power beyond ordinary human limits.</p><p>In Bengal’s homecoming imagination, the warrior is also a beloved daughter returning to her family. These are devotional narratives and interpretations, rather than documented historical events.</p><Source href={PRINCETON}>Devi Mahatmya · Princeton University Art Museum</Source>{' · '}<Source href="https://www.metmuseum.org/art/collection/search/38583">Durga’s imagery · The Met</Source></div>
   </section>
   <section id="heritage" className="museum-section" aria-labelledby="heritage-title">
    <div className="section-intro"><div><span className="section-number">03 / A living heritage</span><h2 id="heritage-title">From the courtyard<br/>to the whole city.</h2></div><p>Durga worship has a long history. The public festival we know today took shape through changing patronage, shared organisation and generations of artistic labour.</p></div>
    <ol className="history-list">
     <li><span className="era">12th century</span><h3>An older image</h3><p>A surviving Bengal-region sculpture of Durga slaying the buffalo demon is held by The Met. It documents an established iconography, not the start date of today’s festival.</p><Source href="https://www.metmuseum.org/art/collection/search/38583">The Met · object 1993.7</Source></li>
     <li><span className="era">Early modern Bengal</span><h3>The family courtyard</h3><p>Landholding and wealthy families became influential patrons of elaborate autumn pujas. Bonedi bari celebrations continue distinct household traditions; no single origin story accounts for every puja.</p><Source href={HISTORY}>Ministry of Tourism · history</Source></li>
     <li><span className="era">The public festival</span><h3>A shared celebration</h3><p>Barowari and later sarbojanin pujas widened collective organisation. Neighbourhood committees, craftspeople and visitors helped transform the celebration into a public cultural event.</p><Source href={COMMUNITY_HISTORY}>Historians’ interviews · Indian Express</Source></li>
     <li><span className="era">2021</span><h3>Living world heritage</h3><p>“Durga Puja in Kolkata” was inscribed on UNESCO’s Representative List of the Intangible Cultural Heritage of Humanity, recognising a living tradition of worship, creativity and collaboration.</p><Source href={UNESCO}>UNESCO · inscription</Source></li>
    </ol>
   </section>
   <section id="rituals" className="museum-section rituals" aria-labelledby="rituals-title">
    <div className="section-intro"><div><span className="section-number">04 / The gestures that endure</span><h2 id="rituals-title">Flowers. Fire. Rhythm.</h2></div><p>Small acts carry a vast inheritance. These are introductions to living practices, whose forms differ across families, temples and communities.</p></div>
    <div className="ritual-grid">{rituals.map(r=><article className="ritual-card" key={r.name}><div className="ritual-art"><MotifArt kind={r.kind}/></div><h3>{r.name}</h3><p>{r.intro}</p><details><summary>Inside the tradition</summary><p>{r.more}</p><Source href={r.source}>Ritual reference</Source></details></article>)}</div>
   </section>
   <section className="museum-section regional" aria-labelledby="region-title">
    <div><span className="section-number">Two regions / Many expressions</span><h2 id="region-title">A shared devotion.<br/>Distinct local worlds.</h2><h3>Bengal</h3><p>In Kolkata, temporary pandals become spaces for worship and ambitious public art. Clay image-making, design, performance and neighbourhood participation sustain the festival’s creative life.</p><Source href={UNESCO}>UNESCO · Durga Puja in Kolkata</Source></div>
    <div><h3>Assam</h3><p>Assam has its own traditions of Goddess worship alongside community Durga Pujas. At Guwahati’s Kamakhya temple, Assam Tourism describes a fifteen-day Pakhuva Puja, observed without an image of the deity.</p><p>That temple practice is distinct from the Bengali calendar shown above. One region’s observance should not stand in for every community’s.</p><Source href={ASSAM}>Assam Tourism · Kamakhya</Source></div>
   </section>
   <aside className="museum-section reading-room" aria-labelledby="sources-title">
    <div><h2 id="sources-title">The reading room</h2><p>Sources checked 15 October 2026.<br/>Original editorial text and symbolic vector art. Mythology, belief and documented history are identified in context.</p></div>
    <ul className="source-list"><li><a href={PANCHANG} target="_blank" rel="noreferrer">Drik Panchang ↗</a><span>Kolkata 2026 dates & vehicle labels</span></li><li><a href={UNESCO} target="_blank" rel="noreferrer">UNESCO ↗</a><span>Durga Puja in Kolkata · 2021 inscription</span></li><li><a href={PRINCETON} target="_blank" rel="noreferrer">Princeton University Art Museum ↗</a><span>Devi Mahatmya & cosmic balance</span></li><li><a href="https://www.metmuseum.org/art/collection/search/38583" target="_blank" rel="noreferrer">The Metropolitan Museum of Art ↗</a><span>Bengal-region Durga sculpture · 12th century</span></li><li><a href={HISTORY} target="_blank" rel="noreferrer">Ministry of Tourism ↗</a><span>Family patronage & public celebrations</span></li><li><a href={ASSAM} target="_blank" rel="noreferrer">Assam Tourism ↗</a><span>Kamakhya & local worship traditions</span></li></ul>
   </aside>
  </main>
  <footer className="museum-footer"><div><a className="wordmark" href={import.meta.env.BASE_URL}>SHAKTI</a><p>Created by Rupjyoti Talukdar · MadB0i</p></div><nav aria-label="Footer"><a href={import.meta.env.BASE_URL}>Return to the film ↗</a><a href={import.meta.env.BASE_URL+'credits.html'}>Credits</a></nav></footer>
 </div>
}
