import { fetchInvestigation } from './client.mjs';

const $ = selector => document.querySelector(selector);
const form = $('#question-form');
const questionInput = $('#question');
const askButton = form.querySelector('button[type="submit"]');
const dialog = $('#evidence-dialog');
let currentRun = null;
let pendingParentRunId = null;
const evidenceButton = $('#evidence-button');

function setStatus(kind, label, message, id = 'NO RUN') {
  $('.status-strip').className = `status-strip ${kind}`;
  $('#status-label').textContent = label;
  $('#status-copy').textContent = message;
  $('#run-id').textContent = id;
}

function formatDate(value) {
  return new Date(`${value}T12:00:00Z`).toLocaleDateString('en-GB', { day:'numeric', month:'short', timeZone:'UTC' });
}

function renderTrace(steps) {
  const list = $('#trace-list'); list.replaceChildren();
  if (!steps.length) {
    const empty = document.createElement('li'); empty.className = 'trace-empty';
    empty.textContent = 'No tool call was confirmed.';
    list.append(empty); return;
  }
  for (const step of steps) {
    const li = document.createElement('li'); li.className = step.status.toLowerCase();
    const title = document.createElement('strong'); title.textContent = step.tool;
    const state = document.createElement('span'); state.className = 'trace-state';
    const phase = step.phase || 'TOOLS';
    state.textContent = step.status === 'ERROR' ? 'Failed' : step.status === 'BLOCKED' ? 'Blocked'
      : phase === 'PLAN' ? 'Planned' : phase === 'TOOLS' ? 'Executed'
      : phase === 'EVIDENCE' ? 'Recorded' : phase === 'VERIFY' ? 'Verified'
      : phase === 'RESPOND' ? 'Responded' : 'Finished';
    const detail = document.createElement('small'); detail.textContent = step.detail;
    li.append(title, state, detail); list.append(li);
  }
}

function chartSvg(series, comparison, width) {
  const data = series.points;
  const height = 240, left = 30, right = 8, top = 29, bottom = 30;
  const plotW = width - left - right, plotH = height - top - bottom;
  const x = i => left + i * plotW / Math.max(1, data.length - 1);
  const y = v => top + (10 - v) * plotH / 10;
  const groups = []; let group = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].value === null) { if (group.length) groups.push(group); group = []; }
    else group.push({ index:i, ...data[i] });
  }
  if (group.length) groups.push(group);
  const grid = [0,2,4,6,8,10].map(v => `<line class="chart-grid" x1="${left}" y1="${y(v)}" x2="${width-right}" y2="${y(v)}"/><text class="chart-axis" x="0" y="${y(v)+3}">${v}</text>`).join('');
  const gaps = data.map((p,i) => p.value === null ? `<rect class="chart-gap" x="${x(i)-3}" y="${top}" width="6" height="${plotH}" rx="2"/>` : '').join('');
  const boundaryIndex = comparison ? data.findIndex(p => p.local_date === comparison.comparison.start) : -1;
  const boundary = boundaryIndex > 0 ? `<line class="chart-boundary" x1="${x(boundaryIndex)-6}" y1="${top}" x2="${x(boundaryIndex)-6}" y2="${top+plotH}"/><text class="chart-period" x="${left}" y="13">EARLIER HISTORY</text><text class="chart-period" x="${x(boundaryIndex)+5}" y="13">RECENT PERIOD</text>` : '';
  const lines = groups.map(points => `<polyline class="chart-line" points="${points.map(p => `${x(p.index)},${y(p.value)}`).join(' ')}"/>`).join('');
  const points = groups.flat().map(p => `<circle class="chart-point" cx="${x(p.index)}" cy="${y(p.value)}" r="3" tabindex="0" role="button" aria-label="${p.local_date}: ${p.value} ${series.unit}, record ${p.source_record_id}. Open source" data-source-id="${p.source_record_id}" data-chart-label="${p.local_date} · ${p.value} ${series.unit} · ${p.source_record_id}"/>`).join('');
  const tickIndexes = [...new Set([0,Math.floor((data.length-1)/4),Math.floor((data.length-1)/2),Math.floor(3*(data.length-1)/4),data.length-1])];
  const ticks = tickIndexes.map(i => `<text class="chart-axis" x="${x(i)}" y="${height-6}" text-anchor="middle">${formatDate(data[i].local_date)}</text>`).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet" role="group" aria-labelledby="chart-svg-title chart-svg-description"><title id="chart-svg-title">Synthetic daily series for ${series.variable}</title><desc id="chart-svg-description">Missing days break the line. Each point opens its source record.</desc>${grid}${gaps}${boundary}${lines}${points}${ticks}</svg>`;
}

function renderChart(run) {
  const container = $('#chart-container');
  const series = run.series[0];
  const variable = series?.variable || run.coverage[0]?.variable || 'energy';
  const label = variable === 'sleep_hours' ? 'Sleep' : 'Energy';
  $('.page-title').innerHTML = variable === 'energy' ? 'What changed in my <em>energy?</em>' : 'What changed in my <em>sleep?</em>';
  $('#breadcrumb-subject').textContent = label.toUpperCase();
  const coverage = run.coverage.find(item => item.variable === variable);
  $('#chart-title').textContent = variable === 'energy' ? 'Energy over time' : 'Sleep over time';
  $('#chart-unit').textContent = series?.unit === 'hours' ? 'HOURS' : 'SCALE 1–10';
  $('#legend-label').textContent = variable === 'energy' ? 'Recorded energy' : 'Recorded sleep';
  $('#coverage-label').textContent = coverage ? `${coverage.observed} / ${coverage.eligible} days` : 'NO COVERAGE';
  if (!series?.points.length) {
    $('.chart-footer').classList.add('no-series');
    $('.page-title').textContent = run.status === 'BLOCKED' ? 'Question outside scope' : 'Result unavailable';
    $('#breadcrumb-subject').textContent = run.status === 'BLOCKED' ? 'LIMIT' : 'NO RESULT';
    $('#chart-title').textContent = 'No series published';
    $('#chart-unit').textContent = '—';
    container.innerHTML = '<div class="chart-placeholder"><strong>No series available</strong><span>No line is shown without traceable records.</span></div>';
    $('#chart-help').textContent = 'No points to inspect in this run.';
    return;
  }
  $('.chart-footer').classList.remove('no-series');
  container.innerHTML = chartSvg(series, run.comparison, Math.max(300,container.clientWidth));
  $('#chart-help').textContent = 'Activate a point to see its date, value, and synthetic record ID.';
  const tooltip = document.createElement('div'); tooltip.className = 'chart-tooltip'; tooltip.hidden = true; container.append(tooltip);
  for (const point of container.querySelectorAll('.chart-point')) {
    const show = () => { tooltip.textContent = point.dataset.chartLabel; tooltip.hidden = false; const box = point.getBoundingClientRect(), parent = container.getBoundingClientRect(); tooltip.style.left = `${box.left-parent.left+box.width/2}px`; tooltip.style.top = `${box.top-parent.top-5}px`; };
    const hide = () => { tooltip.hidden = true; };
    point.addEventListener('mouseenter',show); point.addEventListener('focus',show);
    point.addEventListener('mouseleave',hide); point.addEventListener('blur',hide);
    point.addEventListener('click',() => openEvidence(null,point.dataset.sourceId));
    point.addEventListener('keydown',event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openEvidence(null,point.dataset.sourceId); } });
  }
}

function renderPeriod(run) {
  $('#period-title').textContent = run.comparison ? 'Two 28-day periods' : 'No period comparison';
  const values = $('#period-values').querySelectorAll('strong');
  values[0].textContent = run.comparison ? run.comparison.baseline.mean.toFixed(1) : '—';
  values[1].textContent = run.comparison ? run.comparison.comparison.mean.toFixed(1) : '—';
  $('#period-description').textContent = run.comparison
    ? `${run.comparison.baseline.observed} and ${run.comparison.comparison.observed} observed days. The comparison is descriptive and does not establish a cause.`
    : run.status === 'PASS' ? 'The agent reviewed follow-up records without calculating a period difference.'
      : 'No valid comparison for this run. See the status and reason.';
  $('#period-footnote').textContent = run.comparison
    ? `Mean of observed days · ${run.comparison.unit === 'hours' ? 'hours' : 'scale 1–10'} · source in evidence`
    : 'No figure to compare';
}

function renderFindings(run) {
  const grid = $('#findings'); grid.replaceChildren();
  $('#finding-count').textContent = `${run.findings.length} ${run.findings.length === 1 ? 'FINDING' : 'FINDINGS'}`;
  const kinds = {observation:'OBSERVATION',association:'ASSOCIATION',hypothesis:'HYPOTHESIS',uncertainty:'UNCERTAINTY',abstention:'ABSTENTION'};
  for (const [index,finding] of run.findings.entries()) {
    const card = document.createElement('article'); card.className = `finding-card ${finding.kind}`;
    const label = document.createElement('span'); label.className = 'finding-index'; label.textContent = `${String(index+1).padStart(2,'0')} / ${kinds[finding.kind]}`;
    const title = document.createElement('h4'); title.textContent = finding.title;
    const body = document.createElement('p'); body.textContent = finding.text;
    const provenance = document.createElement('span'); provenance.className = 'finding-provenance';
    provenance.textContent = finding.source_record_ids.length
      ? `${finding.source_record_ids.length} synthetic source IDs`
      : 'No records: limit or abstention';
    const link = document.createElement('button'); link.type = 'button';
    link.textContent = finding.source_record_ids.length ? 'Inspect records ↗' : 'Examine limit ↗';
    link.setAttribute('aria-label', `${link.textContent}: ${finding.title}`);
    link.addEventListener('click',() => openEvidence(finding.finding_id));
    card.append(label,title,body,provenance,link); grid.append(card);
  }
}

function block(title) { const section=document.createElement('section'); section.className='evidence-block'; const h=document.createElement('h3'); h.textContent=title; section.append(h); return section; }
function disclosure(title, open = false) { const details=document.createElement('details'); details.className='evidence-disclosure'; details.open=open; const summary=document.createElement('summary'); summary.textContent=title; details.append(summary); return details; }
function description(items) { const dl=document.createElement('dl'); for (const [key,value] of items) { const dt=document.createElement('dt'); dt.textContent=key; const dd=document.createElement('dd'); dd.textContent=String(value); dl.append(dt,dd); } return dl; }
function renderEvidence(run, findingId = null, sourceId = null) {
  const content = $('#dialog-content'); content.replaceChildren();
  const selected = run.findings.find(item => item.finding_id === findingId) || run.findings[0];
  const point = sourceId ? run.series.flatMap(item => item.points.map(p => ({...p,unit:item.unit}))).find(p => p.source_record_id === sourceId) : null;
  const lead = block(sourceId ? 'SELECTED CHART RECORD' : 'SELECTED FINDING');
  const heading = document.createElement('h4'); heading.textContent = point ? `${point.local_date} · ${point.value} ${point.unit}` : selected?.title || 'No finding available';
  const summary = document.createElement('p'); summary.textContent = point
    ? 'Point returned by the Python core. Its ID identifies a synthetic fixture record.'
    : selected?.text || run.summary;
  lead.append(heading,summary);
  if (point) { const code=document.createElement('code'); code.className='selected-source'; code.textContent=point.source_record_id; lead.append(code); }
  else if (selected?.source_record_ids.length) {
    const records=disclosure(`Show ${selected.source_record_ids.length} synthetic record IDs`);
    const ids=document.createElement('div'); ids.className='source-list';
    for (const id of selected.source_record_ids) { const code=document.createElement('code'); code.textContent=id; ids.append(code); }
    records.append(ids); lead.append(records);
  } else { const note=document.createElement('p'); note.className='evidence-limit'; note.textContent='This limit statement is not attributed to a measured record.'; lead.append(note); }
  content.append(lead);
  const sponsor=block('SPONSOR SERVICES');
  const sponsorText=document.createElement('p'); sponsorText.className='sponsor-warning';
  sponsorText.textContent=`Status in this run: ${run.sponsor_proofs.map(item => `${item.sponsor}: ${item.status}${item.trace_id ? ` · request ${item.trace_id}` : ''}`).join('; ')}.`;
  sponsor.append(sponsorText); content.append(sponsor);
  const origin=disclosure('Source, window, and coverage');
  origin.append(description([['Dataset',run.dataset_id],['Mode',run.mode],['Scenario',run.scenario],['Window',`${run.window.start} to ${run.window.end}`],['Time zone',run.timezone],['Current run',run.run_id],['Previous run',run.parent_run_id || 'None'],...run.coverage.map(c=>[`Coverage ${c.variable}`,`${c.observed} of ${c.eligible} days`])])); content.append(origin);
  const method=disclosure('Method and limits');
  const methodText=document.createElement('p');
  methodText.textContent=run.comparison ? `${run.comparison.method}: ${run.comparison.baseline.start}–${run.comparison.baseline.end} (N=${run.comparison.baseline.observed}) versus ${run.comparison.comparison.start}–${run.comparison.comparison.end} (N=${run.comparison.comparison.observed}). Missing days remain null. No proof of association or causality.` : `No comparison was run. Reason: ${run.reason_code || 'no comparable result'}.`;
  method.append(methodText); content.append(method);
  const trace=disclosure('Plan and tools returned by Python');
  const list=document.createElement('ol'); list.className='trace-detail';
  for (const step of run.tool_trace) { const li=document.createElement('li'); const strong=document.createElement('strong'); strong.textContent=`${step.phase || 'TOOLS'} · ${step.tool} · ${step.status}`; const detail=document.createElement('span'); detail.textContent=step.detail; li.append(strong,detail); if(step.source_record_ids.length){const origin=document.createElement('small');origin.textContent=`${step.source_record_ids.length} synthetic records · event ${step.trace_id.slice(0,12)}`;li.append(origin);} if(step.parent_event_id){const parent=document.createElement('small');parent.textContent=`Decision based on prior event ${step.parent_event_id.slice(0,12)}`;li.append(parent);} list.append(li); }
  trace.append(list); content.append(trace);
}

function openEvidence(findingId = null, sourceId = null) {
  if (!currentRun) return;
  renderEvidence(currentRun,findingId,sourceId);
  $('#dialog-title').textContent = sourceId ? 'Point source.' : findingId ? 'Finding evidence.' : 'Sources and limits.';
  dialog.showModal();
}
evidenceButton.addEventListener('click',() => openEvidence());
$('#dialog-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
function updateFollowupContext() {
  const context=$('#followup-context');
  context.hidden=!pendingParentRunId;
  context.textContent=pendingParentRunId ? `Follow-up to ${pendingParentRunId} · the agent will read the persisted decision and choose the next tools.` : '';
}
function clearPresentation(message) {
  currentRun=null;
  evidenceButton.disabled=true;
  $('.page-title').textContent='Result pending';
  $('#breadcrumb-subject').textContent='PENDING';
  $('#result-context').textContent=message;
  $('#chart-title').textContent='Daily series';
  $('#chart-unit').textContent='—';
  $('#coverage-label').textContent='NO COVERAGE';
  $('.chart-footer').classList.add('no-series');
  $('#chart-help').textContent='The series appears after a valid Python response.';
  $('#chart-container').innerHTML='<div class="chart-placeholder"><strong>No current result</strong><span>No figures from a prior run are retained.</span></div>';
  $('#period-values').querySelectorAll('strong').forEach(value=>{value.textContent='—';});
  $('#period-description').textContent='Awaiting a valid comparison.';
  $('#period-footnote').textContent='No figure to compare';
  $('#findings').replaceChildren();
  $('#finding-count').textContent='NO CURRENT FINDINGS';
}
questionInput.addEventListener('input',()=>{pendingParentRunId=null;updateFollowupContext();});
for (const button of document.querySelectorAll('[data-question]')) button.addEventListener('click',()=>{
  questionInput.value=button.dataset.question;
  pendingParentRunId=button.dataset.question.includes('sleep') ? currentRun?.run_id || localStorage.getItem('phis.synthetic.lastRunId') : null;
  updateFollowupContext();
  questionInput.focus();
});

form.addEventListener('submit',async event=>{
  event.preventDefault(); const question=questionInput.value.trim(); if(!question){questionInput.focus();return;}
  const parentRunId=pendingParentRunId;
  clearPresentation('Querying synthetic data.');
  askButton.disabled=true; askButton.querySelector('span').textContent='Querying Python';
  for (const button of document.querySelectorAll('[data-question]')) button.disabled=true;
  $('#main').setAttribute('aria-busy','true');
  $('#agent-phase').textContent='IN PROGRESS';
  $('#trace-list').innerHTML='<li class="trace-empty">Waiting for the Python core. No tools are confirmed yet.</li>';
  setStatus('busy','CONSULTA IN PROGRESS','Waiting for the local run; no results or traces are confirmed yet.','IN PROGRESS');
  try {
    const scenario=new URLSearchParams(location.search).get('scenario') || 'normal';
    currentRun=await fetchInvestigation(question,{scenario,parentRunId});
    const zetaris=currentRun.sponsor_proofs.find(proof=>proof.sponsor==='zetaris');
    $('#demo-sponsor-status').textContent=currentRun.mode==='LIVE_SYNTHETIC_ZETARIS'
      ? `Local Zetaris: ${zetaris?.status || 'NOT_CONNECTED'}. No medical advice.`
      : 'Local synthetic mode. See sponsor proofs for connection status. No medical advice.';
    $('.mode-pill').lastChild.textContent=currentRun.mode==='LIVE_SYNTHETIC_ZETARIS'
      ? ' SYNTHETIC · LOCAL ZETARIS' : ' SYNTHETIC · LOCAL';
    if(currentRun.status==='PASS' && currentRun.comparison) localStorage.setItem('phis.synthetic.lastRunId',currentRun.run_id);
    pendingParentRunId=null; updateFollowupContext();
    $('#window-label').textContent=`${formatDate(currentRun.window.start).toUpperCase()} — ${formatDate(currentRun.window.end).toUpperCase()} ${currentRun.window.end.slice(0,4)}`;
    renderTrace(currentRun.tool_trace); renderChart(currentRun); renderPeriod(currentRun); renderFindings(currentRun);
    const states={PASS:['','OBSERVATION AVAILABLE'],EXECUTED_PARTIAL:['warning','PARTIAL RESULT'],INSUFFICIENT_DATA:['warning','INSUFFICIENT EVIDENCE'],BLOCKED:['warning','RESPONSIBLE ABSTENTION'],ERROR:['error','TOOL UNAVAILABLE']};
    setStatus(states[currentRun.status][0],states[currentRun.status][1],
      currentRun.status === 'PASS' ? 'A descriptive finding is available below. Cause is not established.' : currentRun.summary,
      currentRun.run_id);
    $('#agent-phase').textContent={
      PASS:'RESPONSE RECEIVED',EXECUTED_PARTIAL:'PARTIAL RESULT',
      INSUFFICIENT_DATA:'INSUFFICIENT COVERAGE',BLOCKED:'ABSTENTION',ERROR:'SOURCE OR TOOL UNAVAILABLE'
    }[currentRun.status];
    $('#result-context').textContent=currentRun.parent_run_id
      ? `Follow-up to ${currentRun.parent_run_id} · decision recovered from World Model · run ${currentRun.run_id}`
      : `Run ${currentRun.run_id} · ${currentRun.mode==='LIVE_SYNTHETIC_ZETARIS' ? 'synthetic rows queried from local Zetaris' : 'synthetic data from the Python core'}`;
    evidenceButton.disabled=false;
    $('#main').focus();
  } catch(error) {
    clearPresentation('The query did not return a valid result.');
    $('#agent-phase').textContent='NO RESPONSE';
    renderTrace([]);
    setStatus('error','CONNECTION OR CONTRACT ERROR','Could not get a valid response from the Python core. Try again.');
    console.error('API response rejected',error);
  } finally {
    askButton.disabled=false; askButton.querySelector('span').textContent='Investigate records';
    for (const button of document.querySelectorAll('[data-question]')) button.disabled=false;
    $('#main').removeAttribute('aria-busy');
  }
});
window.addEventListener('resize',()=>{ if (currentRun?.series[0]?.points.length) renderChart(currentRun); });
