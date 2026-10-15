import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, mkdirSync, existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
// Only runtime assets enter the website. Original footage, references and evidence stay local.
const assets=['WAN2.2-NOTICE.txt','licenses/Wan2.2-Apache-2.0.txt','shakti-icon.svg','art/cosmic-background.png','art/trishul/trishul-hero.glb','art/trishul/keshav/trishul-flight.glb','art/trishul/keshav/license.txt','art/trishul/keshav/ATTRIBUTION.md','fonts/Cinzel-OFL.txt','fonts/NotoSerifBengali-OFL.txt','fonts/ATTRIBUTION.md','videos/playback/divine-catch.mp4','videos/playback/divine-finale.mp4','audio/shakti-original.m4a','posters/finale.jpg','social/shakti-social.jpg','credits.html','media/shakti-film.mp4']
export default defineConfig(({command})=>({plugins:[react(),{name:'runtime-assets-only',closeBundle(){
 for(const file of assets){const src=resolve('public',file);if(!existsSync(src))throw new Error(`Missing delivery asset: ${file}`);const dest=resolve('dist',file);mkdirSync(dirname(dest),{recursive:true});copyFileSync(src,dest)}
 copyFileSync('LICENSE','dist/LICENSE');copyFileSync('docs/DEPENDENCY-LICENSES.txt','dist/DEPENDENCY-LICENSES.txt')
 // Physical entry supports direct /discover/ loads on static hosts, including Pages.
 const html=readFileSync('dist/index.html','utf8')
  .replace('<title>SHAKTI · The Awakening</title>','<title>The Story of Shakti · SHAKTI</title>')
  .replace(/content="SHAKTI — The Awakening\. A 30-second Durga Puja cinematic by Rupjyoti Talukdar \(MadB0i\)\."/,'content="Explore Durga Puja: the 2026 Bengali calendar, mythology and the living traditions of Bengal and Assam."')
  .replace(/<meta property="og:title" content="[^"]*"\/>/,'<meta property="og:title" content="The Story of Shakti · SHAKTI"/>')
  .replace(/<meta property="og:url" content="[^"]*"\/>/,'<meta property="og:url" content="https://madb0i.github.io/SHAKTI/discover/"/>')
  .replace(/<meta property="og:description" content="[^"]*"\/>/,'<meta property="og:description" content="A cultural companion to SHAKTI: mythology, living heritage and Durga Puja 2026."/>')
 mkdirSync('dist/discover',{recursive:true});writeFileSync('dist/discover/index.html',html)
}}],publicDir:command==='serve'?'public':false,base:'/'}))
