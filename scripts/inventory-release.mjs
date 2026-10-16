// Local inventory only. This script cannot approve, push, tag or publish a release.
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { join, relative } from 'node:path'
import { createHash } from 'node:crypto'
const root='dist'
const version=JSON.parse(readFileSync('package.json','utf8')).version
function walk(dir){return readdirSync(dir).flatMap(name=>{const path=join(dir,name);return statSync(path).isDirectory()?walk(path):[path]})}
function origin(file){
 if(file==='media/shakti-film.mp4')return 'Owner-final film: documented Wan2.2 footage, separately credited Trishul/fonts and attribution-conditioned festival music; see CREDITS.md and AUDIO-PROVENANCE-v2.0.0.md'
 if(file.startsWith('audio/'))return 'Owner-final MP4 audio stream copy; Mrinal Sharma / No Copyright Indian Music; attribution-conditioned free-use statement and owner-reviewed scope basis, see AUDIO-PROVENANCE-v2.0.0.md'
 if(/fonts\/|\.ttf$/.test(file))return 'Cinzel / Noto Serif Bengali: SIL OFL 1.1; retained font notices'
 if(file.startsWith('art/trishul/keshav/'))return 'keshavckm1: CC BY 4.0; retained license, attribution and modifications'
 if(file==='art/cosmic-background.png')return 'Owner-confirmed OpenAI-assisted SHAKTI artwork; no exclusive copyright claim'
 if(/^(videos\/|media\/|posters\/|social\/)/.test(file))return 'Owner-confirmed local Wan2.2 via ComfyUI; Clipchamp edit/export; official Apache-2.0 model license and generated-output use statement reviewed'
 if(file.endsWith('.js'))return 'Original authored contributions plus bundled dependencies; see DEPENDENCY-LICENSES.txt (GSAP separate proprietary license)'
 return 'Original authored contributions / retained notices; MIT applies only to original contributions'
}
const files=walk(root).sort().map(path=>{const file=relative(root,path).replaceAll('\\','/'),bytes=readFileSync(path);return {file,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),origin_terms:origin(file)}})
writeFileSync('docs/asset-manifest.json',JSON.stringify({version,release:`v${version} — owner-authorized; music attribution and actual terms retained`,base:'/SHAKTI/',total_bytes:files.reduce((n,f)=>n+f.bytes,0),files},null,2)+'\n')
console.log(`Inventoried ${files.length} local delivery files; no approval or publication performed.`)
