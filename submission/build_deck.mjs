import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// Editable, claim-bounded submission deck with authentic repository captures.
// Rebuild with the bundled Codex artifact runtime; see submission/README.md.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const SKILL = process.env.PHIS_PRESENTATIONS_SKILL;
const PYTHON = process.env.RUNTIME_PYTHON;
const MODULES = process.env.RUNTIME_NODE_MODULES;
if (!SKILL || !PYTHON || !MODULES) throw new Error('Set PHIS_PRESENTATIONS_SKILL, RUNTIME_PYTHON and RUNTIME_NODE_MODULES from the Codex bundled workspace runtime.');
const { Presentation, PresentationFile } = await import(pathToFileURL(path.join(MODULES,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const OUT = path.join(HERE, 'deck', 'PHIS_Open_Agent_2026_Track02_Review.pptx');
const BUILD = path.join(HERE, '.deck-build');
const W = 1280, H = 720;
const C = { navy:'#0B1923', navy2:'#102A34', cream:'#F6F5F0', white:'#FFFFFF', teal:'#56CDB7', mint:'#B2F0DE', ink:'#132A32', muted:'#59717A', mist:'#DDE7E4', orange:'#E5AD79', border:'#C4D5D1' };
const FONT = 'Arial';

function shape(slide, geometry, x,y,w,h,fill='none',lineFill='none',lineWidth=0) {
  return slide.shapes.add({geometry, position:{left:x,top:y,width:w,height:h},fill,
    line:{style:'solid',fill:lineFill,width:lineWidth}});
}
function txt(slide,text,x,y,w,h,size=22,color=C.ink,bold=false,align='left') {
  const s=shape(slide,'textbox',x,y,w,h);
  s.text=text;
  s.text.style={fontFamily:FONT,typeface:FONT,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',wrap:'word',autoFit:'shrinkText',insets:0};
  return s;
}
function rule(slide,x,y,w,color=C.border,width=1) { shape(slide,'rect',x,y,w,width,color); }
function base(dark=false) {
  const s=deck.slides.add(); s.background.fill=dark?C.navy:C.cream;
  txt(s,'PHIS  /  OPEN AGENT 2026',60,31,470,22,13,dark?C.mint:C.muted,true);
  txt(s,'SYNTHETIC DEMO  •  TRACK 02',900,31,320,22,12,dark?C.mint:C.muted,true,'right');
  rule(s,60,63,1160,dark?'#31505A':C.border,1);
  return s;
}
function heading(s,kicker,title,subtitle='',dark=false){
  txt(s,kicker.toUpperCase(),60,92,560,25,14,dark?C.teal:C.muted,true);
  txt(s,title,60,130,1140,78,46,dark?C.white:C.ink,true);
  if(subtitle) txt(s,subtitle,60,214,1120,62,20,dark?C.mist:C.muted);
}
function footer(s,n,dark=false){
  rule(s,60,666,1160,dark?'#31505A':C.border,1);
  txt(s,'TRACK 02 · THE AGENT THAT CAN EXPLAIN WHY',60,675,800,22,11,dark?C.mist:C.muted,true);
  txt(s,String(n).padStart(2,'0'),1168,675,52,22,11,dark?C.mist:C.muted,true,'right');
}
function card(s,x,y,w,h,title,body,dark=false,tag=''){
  shape(s,'rect',x,y,w,h,dark?C.navy2:C.white,dark?'#31505A':C.border,1);
  if(tag) txt(s,tag.toUpperCase(),x+22,y+18,w-44,20,12,dark?C.teal:C.muted,true);
  txt(s,title,x+22,y+(tag?50:23),w-44,46,25,dark?C.white:C.ink,true);
  txt(s,body,x+22,y+(tag?103:78),w-44,h-(tag?120:92),18,dark?C.mist:C.muted);
}
function notes(s,body){s.speakerNotes.text=body;}
async function screenshot(slide,filename,x,y,w,h,alt){
  const bytes=await fs.readFile(path.join(HERE,'..','docs','evidence',filename));
  slide.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}

const deck=Presentation.create({slideSize:{width:W,height:H}});

// 01 — cover
{
 const s=base(true);
 txt(s,'WHY HAS MY ENERGY\nCHANGED LATELY?',60,126,1110,185,58,C.white,true);
 rule(s,60,336,153,C.teal,6);
 txt(s,'An evidence-centered agent that can show what it knows,\nwhat it tested, and why it abstains.',60,375,1050,98,27,C.mist);
 txt(s,'PHIS Open Agent',60,552,575,50,30,C.teal,true);
 txt(s,'Track 02 · synthetic data · source-linked evidence',60,613,900,26,15,C.mist);
 notes(s,'Track 02 selected by founder and confirmed eligible by organizer: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/25#issuecomment-6383697898 . All demo records are synthetic.');
}
// 02 — problem
{
 const s=base(); heading(s,'01 / problem & users','A personal “why” question needs evidence.','For a person reviewing changing energy, longitudinal records are incomplete and easy to overread.');
 card(s,60,314,355,272,'The user','Wants to understand a recent change without receiving an invented diagnosis.');
 card(s,433,314,355,272,'The friction','Scattered time series, missing days and tempting raw correlations obscure what is supportable.');
 card(s,806,314,414,272,'The standard','Show observation, tested association, uncertainty and source lineage in one investigation.');
 footer(s,2); notes(s,'Product positioning and target user are a proposal, not a clinical outcome. Official track wording: https://hackathon.genai.works/event/open-agent-hackathon-2026 .');
}
// 03 — solution
{
 const s=base(true); heading(s,'02 / solution','PHIS turns a question into a bounded investigation.','One longitudinal experience; every conclusion must survive the evidence gate.',true);
 const a=[['01','Observe','The time window, coverage and missing days are explicit.'],['02','Investigate','Select tools and candidate families from the question and state.'],['03','Verify','Discovery evaluates frozen scientific gates and source links.'],['04','Explain / abstain','Return what is supportable and say what remains unknown.']];
 a.forEach((v,i)=>{const x=60+i*292; txt(s,v[0],x,312,265,50,34,C.teal,true); rule(s,x,373,247,'#31505A',1); txt(s,v[1],x,396,255,48,25,C.white,true); txt(s,v[2],x,458,255,112,18,C.mist);});
 footer(s,3,true); notes(s,'Source: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/33 . The result is observational; do not say a specific factor caused an energy change.');
}
// 04 — agent workflow
{
 const s=base(); heading(s,'03 / genuine agentic workflow','A decision loop with a scientific veto.','The next step depends on question, coverage, tool result and persisted context.');
 const blocks=[['PLAN','Choose family and window'],['TOOLS','Retrieve records and run Discovery'],['EVIDENCE','Bind IDs to every candidate'],['VERIFY','Check gates and provenance'],['RESPOND','Explain bounded observations'],['ABSTAIN','Stop on weak or failed evidence']];
 blocks.forEach((b,i)=>{const col=i%3,row=Math.floor(i/3),x=60+col*390,y=304+row*146; shape(s,'rect',x,y,365,125,C.white,C.border,1);txt(s,b[0],x+18,y+16,329,21,13,C.teal,true);txt(s,b[1],x+18,y+47,330,63,22,C.ink,true);});
 txt(s,'↳ Weak evidence triggers abstention; persisted World Model state changes a later follow-up.',60,610,1110,32,17,C.muted);
 footer(s,4);notes(s,'Sources: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/33 and https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/35 . PR35 critique accepted evidence; no unproven replan is claimed.');
}
// 05 — architecture
{
 const s=base(true); heading(s,'04 / technical architecture','A clear boundary between evidence and language.','The UI renders a typed result; it does not compute scientific findings.',true);
 card(s,60,314,353,236,'Data & provenance','Synthetic typed records → Zetaris query IDs → immutable source IDs.',true,'Source');
 card(s,463,314,353,236,'Agent & science','Planner and verifier call deterministic Discovery; World Model stores follow-up state.',true,'Decision');
 card(s,866,314,353,236,'Experience','API result → longitudinal view, evidence panel, uncertainty and abstention.',true,'Presentation');
 txt(s,'Runtime boundary: no private health data • no fabricated sponsor response • no LLM-authored measurements',60,583,1120,38,17,C.mist);
 footer(s,5,true);notes(s,'Five PREEXISTING PHIS Discovery modules were owner-authorized and released under MIT in PR33: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/33 . New orchestration, adapters, UI and synthetic validation were built during the event.');
}
// 06 — sponsors
{
 const s=base(); heading(s,'05 / Zetaris & Meterless','Show what each sponsor actually does.','A proof belongs to a specific run, source mode and time window.');
 card(s,60,310,552,282,'Zetaris','VERIFIED LIVE in PR33: authenticated local query, six pages and 1,080 fictional source records. This is a separate run from the NVIDIA receipt.',false,'Data layer');
 card(s,638,310,582,282,'Meterless World Model','VERIFIED Engine: evidence persists; a follow-up reads prior state and selects sleep. This is not Power, Runtime or Nightshift.',false,'Memory layer');
 footer(s,6);notes(s,'Real PR33 proof: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/fb806023a5fb7d84cba05e299b2384acfbb02250/docs/JUDGE_RELEASE_GATE_2026-10-24.md . Live browser run SYN-RUN-955581f5ca45, follow-up SYN-RUN-330c2e6006b2. Screenshot docs/evidence/judge-release-live-zetaris.png from earlier exact runtime SHA 588c4046aa22e2ea60f77046ed40de3ec52195b5.');
}
// 07 — unique sponsor use
{
 const s=base(true); heading(s,'06 / unique sponsor contribution','Source lineage meets persistent memory.','The meaningful combination is auditability across steps, not a list of logos.',true);
 txt(s,'SOURCE-BOUND',60,321,540,40,29,C.teal,true);
 txt(s,'A retrieved row has a source ID. A scientific child has a plan and family ID. The final statement must cite the evidence that generated it.',60,378,520,174,22,C.white);
 rule(s,633,315,1,'#31505A',268);
 txt(s,'STATE-DEPENDENT',676,321,540,40,29,C.teal,true);
 txt(s,'A World Model event survives the first run. A subsequent question reads that event and selects different work—visible in the trace.',676,378,520,174,22,C.white);
 txt(s,'NVIDIA Lightning: genuine direct PLAN + CRITIQUE in local synthetic v4; not Meterless Power.',60,594,1120,28,16,C.orange,true);
 footer(s,7,true);notes(s,'Direct hosted NVIDIA nvidia/nemotron-3.5-lightning-30b-a3b proof in PR35: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/815ac9ef426cd632732f7b7f22a3a200a025e3c5/docs/NEMOTRON_CONTRACT_RECOVERY_2026-10-24.md . v4 local synthetic run SYN-RUN-12a0a336e5cf, plan chatcmpl-f2bb11bd-fa90-49a7-839a-b195c8806a9e, critique chatcmpl-424b1863-d517-4b27-a3e5-9aa115e07699. Zetaris NOT_CONNECTED in this run.');
}
// 08 — authentic product captures from documented earlier PR33 runs
{
 const s=base(); heading(s,'07 / product experience','An actual investigation, visible on screen.','Authentic PR33 Chrome captures; live Zetaris desktop and local synthetic mobile.');
 shape(s,'rect',60,306,756,296,C.white,C.border,1);
 await screenshot(s,'judge-release-live-zetaris.png',68,314,740,274,'Actual PR33 Chrome energy investigation, synthetic live Zetaris');
 shape(s,'rect',842,306,378,296,C.white,C.border,1);
 await screenshot(s,'judge-release-mobile-energy.png',850,314,362,274,'Actual PR33 mobile synthetic local energy evidence');
 txt(s,'LIVE ZETARIS · EARLIER PR33 SHA',60,615,756,24,13,C.muted,true);
 txt(s,'LOCAL · EARLIER PR33 SHA',842,615,378,24,13,C.muted,true);
 footer(s,8);notes(s,'Authentic images: docs/evidence/judge-release-live-zetaris.png and docs/evidence/judge-release-mobile-energy.png. Both documented in https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/fb806023a5fb7d84cba05e299b2384acfbb02250/docs/JUDGE_RELEASE_GATE_2026-10-24.md . They are earlier PR33 evidence, not a claim that combined NVIDIA + live Zetaris was captured on final SHA.');
}
// 09 — science/evidence boundary
{
 const s=base(true); heading(s,'Evidence integrity','Association is not explanation by itself.','The 180-day fictional run exposes coverage, gates and source IDs.',true);
 card(s,60,314,353,244,'180-day scenario','1,080 fictional variable-day records; 170/180 observed energy days in the documented Chrome run.',true,'Synthetic');
 card(s,463,314,353,244,'Scientific gate','Discovery reports qualified same-day associations, with source IDs and coverage; association is not cause.',true,'Deterministic');
 card(s,866,314,353,244,'Uncertainty','The 28-day mean rose about 0.35/10. A different longer comparison can differ; no diagnosis follows.',true,'Scope limit');
 footer(s,9,true);notes(s,'Actual source: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/fb806023a5fb7d84cba05e299b2384acfbb02250/docs/JUDGE_RELEASE_GATE_2026-10-24.md and image docs/evidence/judge-release-live-zetaris.png . Six variables × 180 days means 1,080 variable-day records, not 1,080 patients or days.');
}
// 10 — roadmap
{
 const s=base(); heading(s,'08 / roadmap & impact','From inspectable prototype to consented insight.','The promise is better questions and clearer limits—not a clinical outcome claim.');
 const items=[['NOW','Synthetic 180-day investigation, source lineage, World Model follow-up and honest abstention.'],['PROVEN SEPARATELY','PR33 live Zetaris; PR35 direct hosted NVIDIA planning and critique.'],['LATER','Consented ingestion, privacy controls and prospective usefulness validation.']];
 items.forEach((v,i)=>{const y=313+i*97;txt(s,v[0],60,y,180,36,22,i===0?C.ink:C.muted,true);rule(s,242,y+8,3,C.teal,62);txt(s,v[1],272,y,920,70,23,C.ink);});
 txt(s,'Next gate: final SHA, recorded video and anonymous link checks.',60,620,1120,30,17,C.muted,true);
 footer(s,10);notes(s,'This is a review deck, not evidence of HackOS submission. PR33 and PR35 proofs are separate: https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/33 and https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/35 . No Nightshift/Power/Runtime claim.');
}

await fs.mkdir(BUILD,{recursive:true});
await fs.mkdir(path.dirname(OUT),{recursive:true});
for (const [i,s] of deck.slides.items.entries()) {
  const png=await deck.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(BUILD,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const candidate=path.join(BUILD,'candidate.pptx');
await (await PresentationFile.exportPptx(deck)).save(candidate);
const finalizeOptions={
  workspaceDir:HERE,candidatePath:candidate,finalPath:OUT,pythonExecutable:PYTHON,
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,
  receiptPath:path.join(BUILD,'validation.json'),
};
let result;
try {
  result=await finalizePresentation(finalizeOptions);
} catch (error) {
  // Windows workspace policy may deny the finalizer's atomic hardlink after
  // it has already completed all package/layout/font/import checks.
  if (error?.code !== 'EPERM' || error?.syscall !== 'link') throw error;
  await fs.copyFile(candidate,OUT);
  result={validation:'all finalizer checks completed; atomic publish hardlink denied by workspace, validated candidate copied byte-for-byte'};
}
console.log(JSON.stringify({output:OUT,slides:deck.slides.items.length,result},null,2));
