import { investigate } from './tools.mjs';
import { records } from './fixture.mjs';

const $ = selector => document.querySelector(selector);
const form = $('#question-form');
const questionInput = $('#question');
const askButton = form.querySelector('button[type="submit"]');
const dialog = $('#evidence-dialog');
let currentRun = null;

function setStatus(kind, label, message, id = 'SIN EJECUCIÓN') {
  const strip = $('.status-strip');
  strip.className = `status-strip ${kind}`;
  $('#status-label').textContent = label;
  $('#status-copy').textContent = message;
  $('#run-id').textContent = id;
}

function renderTrace(trace) {
  const list = $('#trace-list');
  list.replaceChildren();
  for (const step of trace) {
    const li = document.createElement('li');
    li.className = step.status;
    const name = document.createElement('strong'); name.textContent = step.label;
    const detail = document.createElement('small'); detail.textContent = step.detail;
    li.append(name, detail); list.append(li);
  }
}

function chartSvg(data) {
  const width = 680, height = 234, left = 30, right = 7, top = 9, bottom = 31;
  const plotW = width - left - right, plotH = height - top - bottom;
  const x = index => left + index * plotW / Math.max(1, data.length - 1);
  const y = value => top + (10 - value) * plotH / 9;
  const groups = []; let group = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].energy === null) { if (group.length) groups.push(group); group = []; }
    else group.push({ index: i, value: data[i].energy, record: data[i] });
  }
  if (group.length) groups.push(group);
  const grid = [2, 4, 6, 8, 10].map(value => `<line class="chart-grid" x1="${left}" y1="${y(value)}" x2="${width - right}" y2="${y(value)}"/><text class="chart-axis" x="0" y="${y(value) + 3}">${value}</text>`).join('');
  const gaps = data.map((record, i) => record.energy === null ? `<rect class="chart-gap" x="${x(i) - 4}" y="${top}" width="8" height="${plotH}" rx="2"/>` : '').join('');
  const lines = groups.map(points => `<polyline class="chart-line" points="${points.map(p => `${x(p.index)},${y(p.value)}`).join(' ')}"/>`).join('');
  const points = groups.flat().map(p => `<circle class="chart-point" cx="${x(p.index)}" cy="${y(p.value)}" r="3.3" tabindex="0" role="img" aria-label="${p.record.date}: energía ${p.value} de 10, registro ${p.record.id}" data-chart-label="${p.record.date} · ${p.value}/10"/>`).join('');
  const ticks = [0, 10, 20, 31, data.length - 1].map(index => `<text class="chart-axis" x="${x(index)}" y="${height - 6}" text-anchor="middle">${new Date(`${data[index].date}T12:00:00Z`).toLocaleDateString('es-ES', {day:'numeric',month:'short',timeZone:'UTC'})}</text>`).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" role="img" aria-labelledby="chart-svg-title chart-svg-description"><title id="chart-svg-title">Energía diaria sintética</title><desc id="chart-svg-description">Serie de energía en escala subjetiva de uno a diez. Los días sin registro se muestran como franjas y cortan la línea.</desc>${grid}${gaps}${lines}${points}${ticks}</svg>`;
}

function renderChart(run) {
  const container = $('#chart-container');
  if (!run.trend.length) {
    container.innerHTML = '<div class="chart-placeholder"><span class="placeholder-symbol" aria-hidden="true">⌁</span><strong>Sin serie disponible</strong><span>El resultado no incluye datos trazables para dibujar.</span></div>';
    $('#coverage-label').textContent = `${run.coverage.energy} / ${run.coverage.eligible} días registrados`;
    return;
  }
  container.innerHTML = chartSvg(run.trend);
  $('#coverage-label').textContent = `${run.coverage.energy} / ${run.coverage.eligible} días registrados`;
  const tooltip = document.createElement('div'); tooltip.className = 'chart-tooltip'; tooltip.hidden = true; container.append(tooltip);
  for (const point of container.querySelectorAll('.chart-point')) {
    const show = () => { tooltip.textContent = point.dataset.chartLabel; tooltip.hidden = false; const box = point.getBoundingClientRect(), parent = container.getBoundingClientRect(); tooltip.style.left = `${box.left - parent.left + box.width / 2}px`; tooltip.style.top = `${box.top - parent.top - 5}px`; };
    const hide = () => { tooltip.hidden = true; };
    point.addEventListener('mouseenter', show); point.addEventListener('focus', show); point.addEventListener('mouseleave', hide); point.addEventListener('blur', hide);
  }
}

function renderFindings(run) {
  const grid = $('#findings'); grid.replaceChildren();
  $('#finding-count').textContent = `${run.findings.length} ${run.findings.length === 1 ? 'LECTURA' : 'LECTURAS'}`;
  for (const [index, finding] of run.findings.entries()) {
    const card = document.createElement('article'); card.className = `finding-card ${finding.kind}`;
    const kind = {observation:'OBSERVACIÓN',hypothesis:'HIPÓTESIS',uncertainty:'INCERTIDUMBRE',abstention:'ABSTENCIÓN'}[finding.kind];
    const label = document.createElement('span'); label.className = 'finding-index'; label.textContent = `${String(index + 1).padStart(2,'0')} / ${kind}`;
    const title = document.createElement('h4'); title.textContent = finding.title;
    const body = document.createElement('p'); body.textContent = finding.body;
    const link = document.createElement('button'); link.type = 'button'; link.textContent = 'Ver evidencia ↗'; link.addEventListener('click', openEvidence);
    card.append(label,title,body,link); grid.append(card);
  }
}

function renderPeriod(run) {
  const values = $('#period-values').querySelectorAll('strong');
  values[0].textContent = run.periods ? run.periods.earlier.mean.toFixed(1) : '—';
  values[1].textContent = run.periods ? run.periods.recent.mean.toFixed(1) : '—';
  $('#period-description').textContent = run.periods ? `Medias de ${run.periods.earlier.n} y ${run.periods.recent.n} observaciones. Comparación descriptiva, sin prueba causal.` : 'No se calcula una comparación cuando faltan datos o la pregunta está fuera del alcance.';
}

function detailBlock(title) { const block = document.createElement('section'); block.className = 'evidence-block'; const h = document.createElement('h3'); h.textContent = title; block.append(h); return block; }
function definitionList(items) { const dl = document.createElement('dl'); for (const [label,value] of items) { const dt = document.createElement('dt'); dt.textContent = label; const dd = document.createElement('dd'); dd.textContent = value; dl.append(dt,dd); } return dl; }
function renderEvidence(run) {
  const content = $('#dialog-content'); content.replaceChildren();
  const source = detailBlock('01 · Origen y alcance');
  source.append(definitionList([['Dataset',run.source.id],['Naturaleza',run.source.label],['Ventana',run.trend.length ? `${run.trend[0].date} a ${run.trend.at(-1).date}` : 'No consultada'],['Cobertura de energía',`${run.coverage.energy} de ${run.coverage.eligible} días`],['Unidad de energía',run.source.energyUnit],['Servicio',run.source.source]])); content.append(source);
  const method = detailBlock('02 · Método y límites'); const methodText = document.createElement('p'); methodText.textContent = run.periods ? `Dos mitades consecutivas de 21 días; medias aritméticas de los valores observados (N=${run.periods.earlier.n} y N=${run.periods.recent.n}). Los valores ausentes no se interpolan ni se tratan como cero. Sin prueba estadística, intervalo de confianza ni análisis causal.` : 'No se ejecutó comparación descriptiva ni análisis estadístico para esta ejecución.'; method.append(methodText); content.append(method);
  for (const finding of run.findings) { const block = detailBlock(`03 · ${finding.id} · ${finding.title}`); const p = document.createElement('p'); p.textContent = finding.body; block.append(p); const label = document.createElement('p'); label.textContent = finding.sourceIds.length ? `${finding.sourceIds.length} IDs de registro vinculados:` : 'Sin registros de origen: declaración de alcance o límite metodológico.'; block.append(label); if (finding.sourceIds.length) { const ids = document.createElement('div'); ids.className = 'source-list'; for (const id of finding.sourceIds) { const code = document.createElement('code'); code.textContent = id; ids.append(code); } block.append(ids); } content.append(block); }
  const trace = detailBlock('04 · Ejecución local'); const list = document.createElement('ol'); list.className = 'trace-detail'; for (const step of run.trace) { const li = document.createElement('li'); const strong = document.createElement('strong'); strong.textContent = `${step.label} · ${step.status}`; const text = document.createElement('span'); text.textContent = step.detail; li.append(strong,text); list.append(li); } trace.append(list); content.append(trace);
  const sponsor = detailBlock('05 · Integraciones'); const p = document.createElement('p'); p.textContent = 'Esta rama ejecuta únicamente herramientas locales del fixture. No hay trazas de Zetaris, Meterless, Nemotron ni del backend PHIS; su integración requiere respuestas reales y verificables.'; sponsor.append(p); content.append(sponsor);
}

function openEvidence() { if (currentRun) renderEvidence(currentRun); dialog.showModal(); }
$('#evidence-button').addEventListener('click', openEvidence);
$('#dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
for (const button of document.querySelectorAll('[data-question]')) button.addEventListener('click', () => { questionInput.value = button.dataset.question; questionInput.focus(); });

form.addEventListener('submit', async event => {
  event.preventDefault(); const question = questionInput.value.trim(); if (!question) { questionInput.focus(); return; }
  askButton.disabled = true; setStatus('', 'EXPLORANDO FIXTURE', 'Planificando y ejecutando herramientas locales…', 'EN CURSO');
  try {
    const scenario = new URLSearchParams(location.search).get('scenario');
    const options = scenario === 'error' ? {failTool:true} : scenario === 'insufficient' ? {data:records.map((r,i) => ({...r,energy:i < 8 ? r.energy : null}))} : {};
    currentRun = await investigate(question, options);
    renderTrace(currentRun.trace); renderChart(currentRun); renderPeriod(currentRun); renderFindings(currentRun);
    const states = {success:['','OBSERVACIÓN DISPONIBLE'],insufficient:['warning','EVIDENCIA INSUFICIENTE'],unsupported:['warning','ABSTENCIÓN RESPONSABLE'],error:['error','HERRAMIENTA NO DISPONIBLE']};
    setStatus(states[currentRun.status][0],states[currentRun.status][1],currentRun.summary,currentRun.id);
  } catch (error) {
    console.error('Error de interfaz local', error);
    setStatus('error','ERROR DE INTERFAZ','La exploración no pudo completarse. Inténtalo de nuevo.');
  } finally { askButton.disabled = false; }
});
