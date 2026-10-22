import { fetchInvestigation } from './client.mjs';

const $ = selector => document.querySelector(selector);
const form = $('#question-form');
const questionInput = $('#question');
const askButton = form.querySelector('button[type="submit"]');
const dialog = $('#evidence-dialog');
let currentRun = null;
let pendingParentRunId = null;

function setStatus(kind, label, message, id = 'SIN EJECUCIÓN') {
  $('.status-strip').className = `status-strip ${kind}`;
  $('#status-label').textContent = label;
  $('#status-copy').textContent = message;
  $('#run-id').textContent = id;
}

function formatDate(value) {
  return new Date(`${value}T12:00:00Z`).toLocaleDateString('es-ES', { day:'numeric', month:'short', timeZone:'UTC' });
}

function renderTrace(steps) {
  const list = $('#trace-list'); list.replaceChildren();
  for (const step of steps) {
    const li = document.createElement('li'); li.className = step.status.toLowerCase();
    const title = document.createElement('strong'); title.textContent = step.tool;
    const detail = document.createElement('small'); detail.textContent = step.detail;
    li.append(title, detail); list.append(li);
  }
}

function chartSvg(series) {
  const data = series.points;
  const width = 680, height = 234, left = 30, right = 7, top = 9, bottom = 31;
  const plotW = width - left - right, plotH = height - top - bottom;
  const x = i => left + i * plotW / Math.max(1, data.length - 1);
  const y = v => top + (10 - v) * plotH / 9;
  const groups = []; let group = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].value === null) { if (group.length) groups.push(group); group = []; }
    else group.push({ index:i, ...data[i] });
  }
  if (group.length) groups.push(group);
  const grid = [2,4,6,8,10].map(v => `<line class="chart-grid" x1="${left}" y1="${y(v)}" x2="${width-right}" y2="${y(v)}"/><text class="chart-axis" x="0" y="${y(v)+3}">${v}</text>`).join('');
  const gaps = data.map((p,i) => p.value === null ? `<rect class="chart-gap" x="${x(i)-3}" y="${top}" width="6" height="${plotH}" rx="2"/>` : '').join('');
  const lines = groups.map(points => `<polyline class="chart-line" points="${points.map(p => `${x(p.index)},${y(p.value)}`).join(' ')}"/>`).join('');
  const points = groups.flat().map(p => `<circle class="chart-point" cx="${x(p.index)}" cy="${y(p.value)}" r="3" tabindex="0" role="img" aria-label="${p.local_date}: ${p.value} ${series.unit}, registro ${p.source_record_id}" data-chart-label="${p.local_date} · ${p.value} ${series.unit}"/>`).join('');
  const tickIndexes = [...new Set([0,Math.floor((data.length-1)/4),Math.floor((data.length-1)/2),Math.floor(3*(data.length-1)/4),data.length-1])];
  const ticks = tickIndexes.map(i => `<text class="chart-axis" x="${x(i)}" y="${height-6}" text-anchor="middle">${formatDate(data[i].local_date)}</text>`).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" role="img" aria-labelledby="chart-svg-title chart-svg-description"><title id="chart-svg-title">Serie diaria sintética de ${series.variable}</title><desc id="chart-svg-description">Los días sin registro se muestran como franjas y cortan la línea.</desc>${grid}${gaps}${lines}${points}${ticks}</svg>`;
}

function renderChart(run) {
  const container = $('#chart-container');
  const series = run.series[0];
  const variable = series?.variable || run.coverage[0]?.variable || 'energy';
  const label = variable === 'sleep_hours' ? 'Sueño' : 'Energía';
  $('.page-title').innerHTML = variable === 'energy' ? '¿Qué cambió en mi <em>energía?</em>' : '¿Qué cambió en mi <em>sueño?</em>';
  $('#breadcrumb-subject').textContent = label.toUpperCase();
  const coverage = run.coverage.find(item => item.variable === variable);
  $('#chart-title').textContent = variable === 'energy' ? 'Evolución de la energía' : 'Evolución del sueño';
  $('#chart-unit').textContent = series?.unit === 'hours' ? 'HORAS' : 'ESCALA 1–10';
  $('#legend-label').textContent = variable === 'energy' ? 'Energía registrada' : 'Sueño registrado';
  $('#coverage-label').textContent = coverage ? `${coverage.observed} / ${coverage.eligible} días registrados` : 'SIN COBERTURA';
  if (!series?.points.length) {
    container.innerHTML = '<div class="chart-placeholder"><span class="placeholder-symbol" aria-hidden="true">⌁</span><strong>Sin serie disponible</strong><span>No hay datos trazables para dibujar.</span></div>';
    return;
  }
  container.innerHTML = chartSvg(series);
  const tooltip = document.createElement('div'); tooltip.className = 'chart-tooltip'; tooltip.hidden = true; container.append(tooltip);
  for (const point of container.querySelectorAll('.chart-point')) {
    const show = () => { tooltip.textContent = point.dataset.chartLabel; tooltip.hidden = false; const box = point.getBoundingClientRect(), parent = container.getBoundingClientRect(); tooltip.style.left = `${box.left-parent.left+box.width/2}px`; tooltip.style.top = `${box.top-parent.top-5}px`; };
    const hide = () => { tooltip.hidden = true; };
    point.addEventListener('mouseenter',show); point.addEventListener('focus',show);
    point.addEventListener('mouseleave',hide); point.addEventListener('blur',hide);
  }
}

function renderPeriod(run) {
  const values = $('#period-values').querySelectorAll('strong');
  values[0].textContent = run.comparison ? run.comparison.baseline.mean.toFixed(1) : '—';
  values[1].textContent = run.comparison ? run.comparison.comparison.mean.toFixed(1) : '—';
  $('#period-description').textContent = run.comparison
    ? `Medias de ${run.comparison.baseline.observed} y ${run.comparison.comparison.observed} observaciones. Comparación descriptiva, sin prueba causal.`
    : 'No se calcula una comparación cuando faltan datos o la pregunta está fuera del alcance.';
}

function renderFindings(run) {
  const grid = $('#findings'); grid.replaceChildren();
  $('#finding-count').textContent = `${run.findings.length} ${run.findings.length === 1 ? 'LECTURA' : 'LECTURAS'}`;
  const kinds = {observation:'OBSERVACIÓN',association:'ASOCIACIÓN',hypothesis:'HIPÓTESIS',uncertainty:'INCERTIDUMBRE',abstention:'ABSTENCIÓN'};
  for (const [index,finding] of run.findings.entries()) {
    const card = document.createElement('article'); card.className = `finding-card ${finding.kind}`;
    const label = document.createElement('span'); label.className = 'finding-index'; label.textContent = `${String(index+1).padStart(2,'0')} / ${kinds[finding.kind]}`;
    const title = document.createElement('h4'); title.textContent = finding.title;
    const body = document.createElement('p'); body.textContent = finding.text;
    const link = document.createElement('button'); link.type = 'button'; link.textContent = 'Ver evidencia ↗'; link.addEventListener('click',openEvidence);
    card.append(label,title,body,link); grid.append(card);
  }
}

function block(title) { const section=document.createElement('section'); section.className='evidence-block'; const h=document.createElement('h3'); h.textContent=title; section.append(h); return section; }
function description(items) { const dl=document.createElement('dl'); for (const [key,value] of items) { const dt=document.createElement('dt'); dt.textContent=key; const dd=document.createElement('dd'); dd.textContent=String(value); dl.append(dt,dd); } return dl; }
function renderEvidence(run) {
  const content = $('#dialog-content'); content.replaceChildren();
  const source = block('01 · Origen y alcance');
  const energy = run.coverage.find(item => item.variable === 'energy');
  source.append(description([['Dataset',run.dataset_id],['Modo',run.mode],['Escenario',run.scenario],['Ventana',`${run.window.start} a ${run.window.end}`],['Zona horaria',run.timezone],['Cobertura de energía',energy ? `${energy.observed} de ${energy.eligible} días` : 'No consultada'],['Ejecución previa',run.parent_run_id || 'Ninguna']])); content.append(source);
  const method = block('02 · Método y límites'); const text=document.createElement('p');
  text.textContent=run.comparison ? `${run.comparison.method}: ${run.comparison.baseline.start}–${run.comparison.baseline.end} (N=${run.comparison.baseline.observed}) frente a ${run.comparison.comparison.start}–${run.comparison.comparison.end} (N=${run.comparison.comparison.observed}). Los días ausentes siguen como null. Sin prueba de asociación ni inferencia causal.` : `No se ejecutó comparación. Motivo: ${run.reason_code || 'sin resultado comparable'}.`;
  method.append(text); content.append(method);
  for (const finding of run.findings) {
    const section=block(`03 · ${finding.finding_id} · ${finding.title}`); const p=document.createElement('p'); p.textContent=finding.text; section.append(p);
    const label=document.createElement('p'); label.textContent=finding.source_record_ids.length ? `${finding.source_record_ids.length} registros vinculados:` : 'Sin registros: declaración de alcance o límite.'; section.append(label);
    if (finding.source_record_ids.length) { const ids=document.createElement('div'); ids.className='source-list'; for (const id of finding.source_record_ids) { const code=document.createElement('code'); code.textContent=id; ids.append(code); } section.append(ids); }
    content.append(section);
  }
  const trace=block('04 · Herramientas ejecutadas'); const list=document.createElement('ol'); list.className='trace-detail';
  for (const step of run.tool_trace) { const li=document.createElement('li'); const strong=document.createElement('strong'); strong.textContent=`${step.tool} · ${step.status}`; const detail=document.createElement('span'); detail.textContent=step.detail; li.append(strong,detail); list.append(li); } trace.append(list); content.append(trace);
  const sponsor=block('05 · Patrocinadores'); const p=document.createElement('p'); p.textContent=run.sponsor_proofs.map(item=>`${item.sponsor}: ${item.status}`).join(' · '); sponsor.append(p); content.append(sponsor);
}

function openEvidence() { if (currentRun) renderEvidence(currentRun); dialog.showModal(); }
$('#evidence-button').addEventListener('click',openEvidence);
$('#dialog-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
questionInput.addEventListener('input',()=>{pendingParentRunId=null;});
for (const button of document.querySelectorAll('[data-question]')) button.addEventListener('click',()=>{questionInput.value=button.dataset.question; pendingParentRunId=button.dataset.question.includes('sueño') ? currentRun?.run_id || null : null; questionInput.focus();});

form.addEventListener('submit',async event=>{
  event.preventDefault(); const question=questionInput.value.trim(); if(!question){questionInput.focus();return;}
  askButton.disabled=true; setStatus('','CONSULTANDO NÚCLEO','Ejecutando herramientas Python sobre el fixture sintético…','EN CURSO');
  try {
    const scenario=new URLSearchParams(location.search).get('scenario') || 'normal';
    currentRun=await fetchInvestigation(question,{scenario,parentRunId:pendingParentRunId}); pendingParentRunId=null;
    $('#window-label').textContent=`${formatDate(currentRun.window.start).toUpperCase()} — ${formatDate(currentRun.window.end).toUpperCase()} ${currentRun.window.end.slice(0,4)}`;
    renderTrace(currentRun.tool_trace); renderChart(currentRun); renderPeriod(currentRun); renderFindings(currentRun);
    const states={PASS:['','OBSERVACIÓN DISPONIBLE'],EXECUTED_PARTIAL:['warning','RESULTADO PARCIAL'],INSUFFICIENT_DATA:['warning','EVIDENCIA INSUFICIENTE'],BLOCKED:['warning','ABSTENCIÓN RESPONSABLE'],ERROR:['error','HERRAMIENTA NO DISPONIBLE']};
    setStatus(states[currentRun.status][0],states[currentRun.status][1],currentRun.summary,currentRun.run_id);
  } catch(error) {
    currentRun=null; setStatus('error','ERROR DE CONEXIÓN O CONTRATO','No se pudo obtener una respuesta válida del núcleo Python. Inténtalo de nuevo.');
    console.error('Respuesta API rechazada',error);
  } finally {askButton.disabled=false;}
});
