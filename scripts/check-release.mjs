import { readFileSync } from 'node:fs'
const status=JSON.parse(readFileSync(new URL('../release-status.json',import.meta.url),'utf8'))
const pending=[]
if(!status.publicReleaseApproved)pending.push('Owner publication approval is missing.')
if(!status.footageRightsConfirmed)pending.push('Distribution verification for the supplied footage remains unconfirmed; see the recorded rights review. This flag is not a finding of illegality.')
if(!status.footageEvidence?.trim())pending.push('The footage evidence record is missing.')
if(pending.length){console.error('PUBLIC RELEASE ON HOLD:\n'+pending.join('\n'));process.exit(1)}
console.log('Recorded release gate satisfied. Verify the evidence before publication.')
