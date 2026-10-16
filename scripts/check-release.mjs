import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
const root = new URL('../', import.meta.url)
const status = JSON.parse(readFileSync(new URL('release-status.json', root), 'utf8'))
const pkg = JSON.parse(readFileSync(new URL('package.json', root), 'utf8'))
const pending = []
if (!status.publicReleaseApproved) pending.push('Owner publication approval is missing.')
if (!status.footageRightsConfirmed || !status.footageEvidence?.trim()) pending.push('Footage provenance/rights evidence is missing.')
if (status.version !== pkg.version) pending.push('Release status version does not match package.json.')
if (Number(pkg.version.split('.')[0]) >= 2) {
  if (!status.audioRightsConfirmed || !status.audioEvidence?.trim()) pending.push('Final embedded soundtrack redistribution permission remains unverified; see docs/AUDIO-PROVENANCE-v2.0.0.md.')
  const hash = path => createHash('sha256').update(readFileSync(new URL(path, root))).digest('hex')
  if (hash('docs/media/shakti-cinematic.mp4') !== status.approvedFilmSha256) pending.push('Owner-approved film changed after verification.')
  if (hash('public/audio/shakti-original.m4a') !== status.runtimeAudioSha256) pending.push('Runtime audio changed after verification.')
  if (!status.technicalValidationPassed) pending.push('Required v2 playback/build checks have not passed.')
}
if (pending.length) { console.error('PUBLIC RELEASE ON HOLD:\n' + pending.join('\n')); process.exit(1) }
console.log(`Recorded release gate satisfied for v${pkg.version}. Existing tags and releases must be preserved.`)
