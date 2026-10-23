import { fetchInvestigation } from './client.mjs';

const $ = selector => document.querySelector(selector);
const form = $('#question-form');
const questionInput = $('#question');
const askButton = form.querySelector('button[type="submit"]');
const dialog = $('#evidence-dialog');
let currentRun = null;
let pendingParentRunId = null;
const evidenceButton = $('#evidence-button');

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
  if (!steps.length) {
    const empty = document.createElement('li'); empty.className = 'trace-empty';
    empty.textContent = 'No se confirmó ninguna herramienta.';
    list.append(empty); return;
  }
  for (const step of steps) {
    const li = document.createElement('li'); li.className = step.status.toLowerCase();
    const title = document.createElement('strong'); title.textContent = step.tool;
    const state = document.createElement('span'); state.className = 'trace-state';
    const phase = step.phase || 'TOOLS';
    state.textContent = step.status === 'ERROR' ? 'Falló' : step.status === 'BLOCKED' ? 'Detenida'
      : phase === 'PLAN' ? 'Planificado' : phase === 'TOOLS' ? 'Ejecutada'
      : phase === 'EVIDENCE' ? 'Registrada' : phase === 'VERIFY' ? 'Verificada'
      : phase === 'RESPOND' ? 'Respondió' : 'Finalizada';
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
  const boundary = boundaryIndex > 0 ? `<line class="chart-boundary" x1="${x(boundaryIndex)-6}" y1="${top}" x2="${x(boundaryIndex)-6}" y2="${top+plotH}"/><text class="chart-period" x="${left}" y="13">HISTORIAL PREVIO</text><text class="chart-period" x="${x(boundaryIndex)+5}" y="13">PERIODO RECIENTE</text>` : '';
  const lines = groups.map(points => `<polyline class="chart-line" points="${points.map(p => `${x(p.index)},${y(p.value)}`).join(' ')}"/>`).join('');
  const points = groups.flat().map(p => `<circle class="chart-point" cx="${x(p.index)}" cy="${y(p.value)}" r="3" tabindex="0" role="button" aria-label="${p.local_date}: ${p.value} ${series.unit}, registro ${p.source_record_id}. Abrir origen" data-source-id="${p.source_record_id}" data-chart-label="${p.local_date} · ${p.value} ${series.unit} · ${p.source_record_id}"/>`).join('');
  const tickIndexes = [...new Set([0,Math.floor((data.length-1)/4),Math.floor((data.length-1)/2),Math.floor(3*(data.length-1)/4),data.length-1])];
  const ticks = tickIndexes.map(i => `<text class="chart-axis" x="${x(i)}" y="${height-6}" text-anchor="middle">${formatDate(data[i].local_date)}</text>`).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet" role="group" aria-labelledby="chart-svg-title chart-svg-description"><title id="chart-svg-title">Serie diaria sintética de ${series.variable}</title><desc id="chart-svg-description">Los días sin registro se muestran como franjas y cortan la línea. Cada punto abre su registro de origen.</desc>${grid}${gaps}${boundary}${lines}${points}${ticks}</svg>`;
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
  $('#coverage-label').textContent = coverage ? `${coverage.observed} / ${coverage.eligible} días` : 'SIN COBERTURA';
  if (!series?.points.length) {
    $('.chart-footer').classList.add('no-series');
    $('.page-title').textContent = run.status === 'BLOCKED' ? 'Solicitud fuera del alcance' : 'Resultado no disponible';
    $('#breadcrumb-subject').textContent = run.status === 'BLOCKED' ? 'LÍMITE' : 'SIN RESULTADO';
    $('#chart-title').textContent = 'Sin serie publicada';
    $('#chart-unit').textContent = '—';
    container.innerHTML = '<div class="chart-placeholder"><strong>Sin serie disponible</strong><span>No se presenta una línea sin registros trazables.</span></div>';
    $('#chart-help').textContent = 'No hay puntos que inspeccionar en esta ejecución.';
    return;
  }
  $('.chart-footer').classList.remove('no-series');
  container.innerHTML = chartSvg(series, run.comparison, Math.max(300,container.clientWidth));
  $('#chart-help').textContent = 'Activa un punto para ver su fecha, valor e ID de registro sintético.';
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
  $('#period-title').textContent = run.comparison ? 'Dos periodos de 28 días' : 'Sin comparación entre periodos';
  const values = $('#period-values').querySelectorAll('strong');
  values[0].textContent = run.comparison ? run.comparison.baseline.mean.toFixed(1) : '—';
  values[1].textContent = run.comparison ? run.comparison.comparison.mean.toFixed(1) : '—';
  $('#period-description').textContent = run.comparison
    ? `${run.comparison.baseline.observed} y ${run.comparison.comparison.observed} días observados. La comparación es descriptiva; no demuestra una causa.`
    : run.status === 'PASS' ? 'El agente consultó los registros de seguimiento sin calcular una diferencia entre periodos.'
      : 'No hay comparación válida para esta ejecución. Consulta el estado y su motivo.';
  $('#period-footnote').textContent = run.comparison
    ? `Media de días observados · ${run.comparison.unit === 'hours' ? 'horas' : 'escala 1–10'} · fuente en evidencias`
    : 'Sin cifra que comparar';
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
    const provenance = document.createElement('span'); provenance.className = 'finding-provenance';
    provenance.textContent = finding.source_record_ids.length
      ? `${finding.source_record_ids.length} IDs de origen sintéticos`
      : 'Sin registros: límite o abstención';
    const link = document.createElement('button'); link.type = 'button';
    link.textContent = finding.source_record_ids.length ? 'Inspeccionar registros ↗' : 'Examinar límite ↗';
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
  const lead = block(sourceId ? 'REGISTRO SELECCIONADO DEL GRÁFICO' : 'LECTURA SELECCIONADA');
  const heading = document.createElement('h4'); heading.textContent = point ? `${point.local_date} · ${point.value} ${point.unit}` : selected?.title || 'Sin lectura disponible';
  const summary = document.createElement('p'); summary.textContent = point
    ? 'Punto recibido en la serie del núcleo Python. El ID identifica un registro del fixture sintético.'
    : selected?.text || run.summary;
  lead.append(heading,summary);
  if (point) { const code=document.createElement('code'); code.className='selected-source'; code.textContent=point.source_record_id; lead.append(code); }
  else if (selected?.source_record_ids.length) {
    const records=disclosure(`Mostrar ${selected.source_record_ids.length} IDs de registros sintéticos`);
    const ids=document.createElement('div'); ids.className='source-list';
    for (const id of selected.source_record_ids) { const code=document.createElement('code'); code.textContent=id; ids.append(code); }
    records.append(ids); lead.append(records);
  } else { const note=document.createElement('p'); note.className='evidence-limit'; note.textContent='Esta declaración de límite no se atribuye a un registro medido.'; lead.append(note); }
  content.append(lead);
  const sponsor=block('SERVICIOS EXTERNOS');
  const sponsorText=document.createElement('p'); sponsorText.className='sponsor-warning';
  const activeEngine=run.sponsor_proofs.find(item => item.sponsor === 'meterless_engine' && item.status === 'VERIFIED');
  const disconnected=run.sponsor_proofs.filter(item => item.status !== 'VERIFIED').map(item => item.sponsor);
  sponsorText.textContent=`${activeEngine ? `Meterless World Model Engine local verificado: evento ${activeEngine.trace_id.slice(0,12)}. ` : ''}Desconectados: ${disconnected.join(', ')}. No se acredita inferencia externa.`;
  sponsor.append(sponsorText); content.append(sponsor);
  const origin=disclosure('Origen, ventana y cobertura');
  origin.append(description([['Dataset',run.dataset_id],['Modo',run.mode],['Escenario',run.scenario],['Ventana',`${run.window.start} a ${run.window.end}`],['Zona horaria',run.timezone],['Ejecución actual',run.run_id],['Ejecución previa',run.parent_run_id || 'Ninguna'],...run.coverage.map(c=>[`Cobertura ${c.variable}`,`${c.observed} de ${c.eligible} días`])])); content.append(origin);
  const method=disclosure('Método y límites');
  const methodText=document.createElement('p');
  methodText.textContent=run.comparison ? `${run.comparison.method}: ${run.comparison.baseline.start}–${run.comparison.baseline.end} (N=${run.comparison.baseline.observed}) frente a ${run.comparison.comparison.start}–${run.comparison.comparison.end} (N=${run.comparison.comparison.observed}). Los días ausentes siguen como null. Sin prueba de asociación ni inferencia causal.` : `No se ejecutó comparación. Motivo: ${run.reason_code || 'sin resultado comparable'}.`;
  method.append(methodText); content.append(method);
  const trace=disclosure('Plan y herramientas devueltos por Python');
  const list=document.createElement('ol'); list.className='trace-detail';
  for (const step of run.tool_trace) { const li=document.createElement('li'); const strong=document.createElement('strong'); strong.textContent=`${step.phase || 'TOOLS'} · ${step.tool} · ${step.status}`; const detail=document.createElement('span'); detail.textContent=step.detail; li.append(strong,detail); if(step.source_record_ids.length){const origin=document.createElement('small');origin.textContent=`${step.source_record_ids.length} registros sintéticos · evento ${step.trace_id.slice(0,12)}`;li.append(origin);} if(step.parent_event_id){const parent=document.createElement('small');parent.textContent=`Decisión basada en evento previo ${step.parent_event_id.slice(0,12)}`;li.append(parent);} list.append(li); }
  trace.append(list); content.append(trace);
}

function openEvidence(findingId = null, sourceId = null) {
  if (!currentRun) return;
  renderEvidence(currentRun,findingId,sourceId);
  $('#dialog-title').textContent = sourceId ? 'Origen del punto.' : findingId ? 'Evidencia del hallazgo.' : 'Fuentes y límites.';
  dialog.showModal();
}
evidenceButton.addEventListener('click',() => openEvidence());
$('#dialog-close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
function updateFollowupContext() {
  const context=$('#followup-context');
  context.hidden=!pendingParentRunId;
  context.textContent=pendingParentRunId ? `Seguimiento de ${pendingParentRunId} · el agente recuperará la decisión persistida y elegirá nuevas herramientas.` : '';
}
function clearPresentation(message) {
  currentRun=null;
  evidenceButton.disabled=true;
  $('.page-title').textContent='Resultado pendiente';
  $('#breadcrumb-subject').textContent='PENDIENTE';
  $('#result-context').textContent=message;
  $('#chart-title').textContent='Serie diaria';
  $('#chart-unit').textContent='—';
  $('#coverage-label').textContent='SIN COBERTURA';
  $('.chart-footer').classList.add('no-series');
  $('#chart-help').textContent='La serie aparecerá tras una respuesta válida del núcleo Python.';
  $('#chart-container').innerHTML='<div class="chart-placeholder"><strong>Sin resultado vigente</strong><span>No se conservan cifras de una ejecución anterior.</span></div>';
  $('#period-values').querySelectorAll('strong').forEach(value=>{value.textContent='—';});
  $('#period-description').textContent='A la espera de una comparación válida.';
  $('#period-footnote').textContent='Sin cifra que comparar';
  $('#findings').replaceChildren();
  $('#finding-count').textContent='SIN LECTURAS VIGENTES';
}
questionInput.addEventListener('input',()=>{pendingParentRunId=null;updateFollowupContext();});
for (const button of document.querySelectorAll('[data-question]')) button.addEventListener('click',()=>{
  questionInput.value=button.dataset.question;
  pendingParentRunId=button.dataset.question.includes('sueño') ? currentRun?.run_id || localStorage.getItem('phis.synthetic.lastRunId') : null;
  updateFollowupContext();
  questionInput.focus();
});

form.addEventListener('submit',async event=>{
  event.preventDefault(); const question=questionInput.value.trim(); if(!question){questionInput.focus();return;}
  const parentRunId=pendingParentRunId;
  clearPresentation('Consulta en curso sobre datos sintéticos.');
  askButton.disabled=true; askButton.querySelector('span').textContent='Consultando Python';
  for (const button of document.querySelectorAll('[data-question]')) button.disabled=true;
  $('#main').setAttribute('aria-busy','true');
  $('#agent-phase').textContent='EN CURSO';
  $('#trace-list').innerHTML='<li class="trace-empty">Esperando respuesta del núcleo Python. Aún no hay herramientas confirmadas.</li>';
  setStatus('busy','CONSULTA EN CURSO','Esperando la ejecución local; todavía no hay resultados ni trazas confirmados.','EN CURSO');
  try {
    const scenario=new URLSearchParams(location.search).get('scenario') || 'normal';
    currentRun=await fetchInvestigation(question,{scenario,parentRunId});
    if(currentRun.status==='PASS' && currentRun.comparison) localStorage.setItem('phis.synthetic.lastRunId',currentRun.run_id);
    pendingParentRunId=null; updateFollowupContext();
    $('#window-label').textContent=`${formatDate(currentRun.window.start).toUpperCase()} — ${formatDate(currentRun.window.end).toUpperCase()} ${currentRun.window.end.slice(0,4)}`;
    renderTrace(currentRun.tool_trace); renderChart(currentRun); renderPeriod(currentRun); renderFindings(currentRun);
    const states={PASS:['','OBSERVACIÓN DISPONIBLE'],EXECUTED_PARTIAL:['warning','RESULTADO PARCIAL'],INSUFFICIENT_DATA:['warning','EVIDENCIA INSUFICIENTE'],BLOCKED:['warning','ABSTENCIÓN RESPONSABLE'],ERROR:['error','HERRAMIENTA NO DISPONIBLE']};
    setStatus(states[currentRun.status][0],states[currentRun.status][1],
      currentRun.status === 'PASS' ? 'Lectura descriptiva disponible abajo. La causa no está establecida.' : currentRun.summary,
      currentRun.run_id);
    $('#agent-phase').textContent={
      PASS:'RESPUESTA RECIBIDA',EXECUTED_PARTIAL:'RESULTADO PARCIAL',
      INSUFFICIENT_DATA:'COBERTURA INSUFICIENTE',BLOCKED:'ABSTENCIÓN',ERROR:'FALLO LOCAL'
    }[currentRun.status];
    $('#result-context').textContent=currentRun.parent_run_id
      ? `Seguimiento de ${currentRun.parent_run_id} · decisión recuperada del World Model · ejecución ${currentRun.run_id}`
      : `Ejecución ${currentRun.run_id} · datos sintéticos del núcleo Python`;
    evidenceButton.disabled=false;
    $('#main').focus();
  } catch(error) {
    clearPresentation('La consulta no devolvió un resultado válido.');
    $('#agent-phase').textContent='SIN RESPUESTA';
    renderTrace([]);
    setStatus('error','ERROR DE CONEXIÓN O CONTRATO','No se pudo obtener una respuesta válida del núcleo Python. Inténtalo de nuevo.');
    console.error('Respuesta API rechazada',error);
  } finally {
    askButton.disabled=false; askButton.querySelector('span').textContent='Investigar registros';
    for (const button of document.querySelectorAll('[data-question]')) button.disabled=false;
    $('#main').removeAttribute('aria-busy');
  }
});
window.addEventListener('resize',()=>{ if (currentRun?.series[0]?.points.length) renderChart(currentRun); });
