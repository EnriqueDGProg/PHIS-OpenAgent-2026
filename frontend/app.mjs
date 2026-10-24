/**
 * PHIS Open Agent — Premium Investigation UI
 * Renders only data returned by the Python core. No scientific findings hardcoded.
 * Renders the 180-day v3 scientific result by default.
 */
import { fetchInvestigation } from './client.mjs';
import { windowDays, isOfflineScientificRun, sourceLabel, canContinueFrom,
  comparisonExplanation, findingExplanation, plainDate, TRACE_GROUPS } from './presentation.mjs';

// ─── DOM helpers ──────────────────────────────────────────────────────────────
const $ = sel => document.querySelector(sel);
const $$ = sel => [...document.querySelectorAll(sel)];

// ─── State ────────────────────────────────────────────────────────────────────
let currentRun = null;
let pendingParentRunId = null;
let runCount = 0;

// ─── Element refs ─────────────────────────────────────────────────────────────
const form          = $('#question-form');
const questionInput = $('#question');
const askButton     = $('#ask-button');
const evidenceBtn   = $('#evidence-button');
const dialog        = $('#evidence-dialog');
const traceList     = $('#trace-list');
const agentPhase    = $('#agent-phase');

// ─── Utilities ────────────────────────────────────────────────────────────────
function formatDate(iso) {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', timeZone: 'UTC',
  });
}

function setTitle(subject) {
  document.title = subject
    ? `PHIS — ${subject} investigation`
    : 'PHIS — Personal Health Intelligence System';
}

const isBenchmarkRun = isOfflineScientificRun;

// ─── Status strip ─────────────────────────────────────────────────────────────
function setStatus(kind, label, message, id = 'NO RUN') {
  const strip = $('.status-strip');
  strip.className = `status-strip ${kind}`;
  $('#status-label').textContent = label;
  $('#status-copy').textContent  = message;
  $('#run-id').textContent = id;
}

// ─── Run counter ──────────────────────────────────────────────────────────────
function incrementRunCounter() {
  runCount++;
  $('#rail-run-counter').textContent = `${String(runCount).padStart(2, '0')} / ${String(runCount).padStart(2, '0')}`;
}

// ─── Trajectory strip ─────────────────────────────────────────────────────────
function renderTrajectory(run) {
  const strip = $('#trajectory-strip');
  if (!run.comparison) { strip.hidden = true; return; }

  const { baseline, comparison, difference, unit } = run.comparison;
  const unitLabel = unit === 'hours' ? ' h' : '/10';
  const dirEl  = $('#trajectory-direction');
  const deltaEl = $('#trajectory-delta');
  const labelEl = $('#trajectory-label');
  const bValEl  = $('#trajectory-baseline-value');

  const diff = typeof difference === 'number' ? difference : (comparison.mean - baseline.mean);
  const absDiff = Math.abs(diff).toFixed(2);

  dirEl.textContent = diff < -0.05 ? '▼' : diff > 0.05 ? '▲' : '→';
  dirEl.className = 'trajectory-direction ' + (diff < -0.05 ? 'down' : diff > 0.05 ? 'up' : 'flat');
  deltaEl.textContent = `${diff < 0 ? '−' : diff > 0 ? '+' : ''}${absDiff}${unitLabel}`;
  labelEl.textContent = `${plainDate(comparison.start)}–${plainDate(comparison.end)} vs ${plainDate(baseline.start)}–${plainDate(baseline.end)}`;
  bValEl.textContent  = `${baseline.mean?.toFixed(2) ?? '—'}${unitLabel} (earlier 28-day mean)`;
  $('#trajectory-baseline-label').textContent = 'Earlier 28-day mean';

  strip.hidden = false;
}

// ─── Period card ──────────────────────────────────────────────────────────────
function renderPeriod(run) {
  const hasCmp = !!run.comparison;
  $('#period-title').textContent = hasCmp ? 'Two 28-day periods' : 'No period comparison';

  const earlierEl = $('#period-earlier');
  const recentEl  = $('#period-recent');
  const diffEl    = $('#period-diff');
  const diffVal   = $('#period-diff-value');
  const footnote  = $('#period-footnote');

  if (hasCmp) {
    const { baseline, comparison, difference, unit } = run.comparison;
    const unitLabel = unit === 'hours' ? ' h' : '/10';
    earlierEl.textContent = `${baseline.mean?.toFixed(2) ?? '—'}${unitLabel}`;
    recentEl.textContent  = `${comparison.mean?.toFixed(2) ?? '—'}${unitLabel}`;
    $('#period-earlier-dates').textContent = `${plainDate(baseline.start)}–${plainDate(baseline.end)}`;
    $('#period-recent-dates').textContent = `${plainDate(comparison.start)}–${plainDate(comparison.end)}`;

    const diff = typeof difference === 'number' ? difference : (comparison.mean - baseline.mean);
    diffVal.textContent = `${diff >= 0 ? '+' : ''}${diff.toFixed(2)}${unitLabel}`;
    diffVal.className   = 'diff-value ' + (diff < -0.05 ? 'negative' : diff > 0.05 ? 'positive' : 'neutral');
    diffEl.hidden = false;
    $('#period-description').textContent = comparisonExplanation(run)?.coverage ??
      'Only recorded measurements are compared. The difference does not establish a cause.';
    footnote.textContent = `Means rounded to 2 decimals; change uses unrounded means · source IDs in evidence`;
  } else {
    earlierEl.textContent = '—';
    recentEl.textContent  = '—';
    $('#period-earlier-dates').textContent = '—';
    $('#period-recent-dates').textContent = '—';
    diffEl.hidden = true;
    $('#period-description').textContent = run.status === 'PASS'
      ? 'The agent reviewed follow-up records without computing a period difference.'
      : `No valid comparison for this run. See the status and reason: ${run.reason_code || 'no comparable result'}.`;
    footnote.textContent = 'No figure to compare';
  }
}

// ─── Chart SVG ────────────────────────────────────────────────────────────────
function chartSvg(series, comparison, width) {
  const data   = series.points;
  const height = 248, left = 32, right = 10, top = 28, bottom = 32;
  const plotW  = width - left - right;
  const plotH  = height - top - bottom;

  // Scale to variable range — sleep: 0–12, energy: 0–10
  const isHours  = series.unit === 'hours';
  const maxVal   = isHours ? 12 : 10;
  const x = i => left + i * plotW / Math.max(1, data.length - 1);
  const y = v => top + (maxVal - v) * plotH / maxVal;

  // Split into contiguous groups (gaps = null values)
  const groups = []; let group = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].value === null) {
      if (group.length) { groups.push(group); group = []; }
    } else {
      group.push({ index: i, ...data[i] });
    }
  }
  if (group.length) groups.push(group);

  // The reference line is the Python core's earlier 28-day mean.
  const mean = Number.isFinite(comparison?.baseline?.mean) ? comparison.baseline.mean : null;

  // Grid lines
  const gridVals = isHours ? [0, 3, 6, 9, 12] : [0, 2, 4, 6, 8, 10];
  const grid = gridVals.map(v =>
    `<line class="chart-grid" x1="${left}" y1="${y(v)}" x2="${width - right}" y2="${y(v)}"/>` +
    `<text class="chart-axis" x="0" y="${y(v) + 3}">${v}</text>`
  ).join('');

  // Gap rectangles
  const gaps = data.map((p, i) =>
    p.value === null
      ? `<rect class="chart-gap" x="${x(i) - 3}" y="${top}" width="6" height="${plotH}" rx="2"/>`
      : ''
  ).join('');

  // Shade only the two returned 28-day windows, not the earlier 124 days.
  let boundary = '';
  if (comparison && data.length > 0) {
    const earlierIndex = data.findIndex(p => p.local_date === comparison.baseline.start);
    const recentIndex = data.findIndex(p => p.local_date === comparison.comparison.start);
    if (earlierIndex >= 0 && recentIndex > earlierIndex) {
      const earlierX = x(earlierIndex) - 3;
      const recentX = x(recentIndex) - 3;
      boundary =
        `<rect class="chart-shade-earlier" x="${earlierX}" y="${top}" width="${recentX - earlierX}" height="${plotH}"/>` +
        `<rect class="chart-shade" x="${recentX}" y="${top}" width="${width - right - recentX}" height="${plotH}"/>` +
        `<line class="chart-boundary" x1="${earlierX}" y1="${top}" x2="${earlierX}" y2="${top + plotH}"/>` +
        `<line class="chart-boundary" x1="${recentX}" y1="${top}" x2="${recentX}" y2="${top + plotH}"/>` +
        `<text class="chart-period-label" x="${earlierX + 3}" y="${top - 6}">EARLIER</text>` +
        `<text class="chart-period-label" x="${recentX + 3}" y="${top - 6}">RECENT</text>`;
    }
  }

  // Baseline mean line
  const baseline = mean !== null
    ? `<line class="chart-baseline" x1="${left}" y1="${y(mean)}" x2="${width - right}" y2="${y(mean)}"/>`
    : '';

  // Polylines and points
  const lines  = groups.map(pts =>
    `<polyline class="chart-line" points="${pts.map(p => `${x(p.index)},${y(p.value)}`).join(' ')}"/>`
  ).join('');

  const points = groups.flat().map(p =>
    `<circle class="chart-point" cx="${x(p.index)}" cy="${y(p.value)}" r="3.5"
      tabindex="0" role="button"
      aria-label="${p.local_date}: ${p.value} ${series.unit}, record ${p.source_record_id}. Activate to open source"
      data-source-id="${p.source_record_id}"
      data-chart-label="${p.local_date} · ${p.value} ${series.unit} · ${p.source_record_id}"/>`
  ).join('');

  // X-axis date ticks (5 spread evenly)
  const tickIdxs = [...new Set([
    0,
    Math.floor((data.length - 1) * 0.25),
    Math.floor((data.length - 1) * 0.5),
    Math.floor((data.length - 1) * 0.75),
    data.length - 1,
  ])];
  const ticks = tickIdxs.map(i =>
    `<text class="chart-axis" x="${x(i)}" y="${height - 6}" text-anchor="middle">${formatDate(data[i].local_date)}</text>`
  ).join('');

  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet"
    role="group" aria-labelledby="chart-svg-title chart-svg-desc">
    <title id="chart-svg-title">Synthetic daily series for ${series.variable}</title>
    <desc id="chart-svg-desc">Days without measurements break the line. Each point maps to a synthetic source record. The earlier 28-day mean is shown as a dashed line.</desc>
    ${grid}${gaps}${boundary}${baseline}${lines}${points}${ticks}
  </svg>`;
}

function renderChart(run) {
  const container = $('#chart-container');
  const series    = run.series[0];
  const variable  = series?.variable || run.coverage[0]?.variable || 'energy';
  const label     = variable === 'sleep_hours' ? 'Sleep' : 'Energy';
  const isEnergy  = variable !== 'sleep_hours';

  // Update page heading
  const pageTitle  = $('#page-title');
  pageTitle.innerHTML = isEnergy
    ? 'What changed in my <em>energy?</em>'
    : 'What changed in my <em>sleep?</em>';
  $('#breadcrumb-subject').textContent = label.toUpperCase();
  setTitle(`${label} investigation`);

  // Coverage
  const coverage = run.coverage.find(c => c.variable === variable);
  const days     = windowDays(run);
  $('#chart-title').textContent = isEnergy ? 'Energy over time' : 'Sleep over time';
  $('#chart-unit').textContent  = series?.unit === 'hours' ? 'HOURS' : 'SCALE 1–10';
  $('#legend-label').textContent = isEnergy ? 'Recorded energy' : 'Recorded sleep';
  $('#coverage-label').textContent = coverage
    ? `${coverage.observed} / ${days} days`
    : 'NO COVERAGE';
  $('#window-badge').textContent  = `${days} DAYS`;

  // No series case
  if (!series?.points.length) {
    $('.chart-footer').classList.add('no-series');
    pageTitle.textContent = run.status === 'BLOCKED' ? 'Question outside scope' : 'Result unavailable';
    $('#breadcrumb-subject').textContent = run.status === 'BLOCKED' ? 'LIMIT' : 'NO RESULT';
    $('#chart-title').textContent = 'No series published';
    $('#chart-unit').textContent  = '—';
    container.innerHTML = `<div class="chart-placeholder">
      <span class="placeholder-icon" aria-hidden="true">⬡</span>
      <strong>No series available</strong>
      <span>No line is drawn without traceable records.</span>
    </div>`;
    $('#chart-help').textContent = 'No data points to inspect in this run.';
    return;
  }

  $('.chart-footer').classList.remove('no-series');
  container.innerHTML = chartSvg(series, run.comparison, Math.max(280, container.clientWidth || 400));
  $('#chart-help').textContent = 'Activate a point to see its date, value, and synthetic record ID.';

  // Tooltip
  const tooltip = document.createElement('div');
  tooltip.className = 'chart-tooltip';
  tooltip.hidden = true;
  container.append(tooltip);

  for (const pt of container.querySelectorAll('.chart-point')) {
    const show = () => {
      tooltip.textContent = pt.dataset.chartLabel;
      tooltip.hidden = false;
      const box = pt.getBoundingClientRect(), parent = container.getBoundingClientRect();
      tooltip.style.left = `${box.left - parent.left + box.width / 2}px`;
      tooltip.style.top  = `${box.top - parent.top - 6}px`;
    };
    const hide = () => { tooltip.hidden = true; };
    pt.addEventListener('mouseenter', show);
    pt.addEventListener('focus', show);
    pt.addEventListener('mouseleave', hide);
    pt.addEventListener('blur', hide);
    pt.addEventListener('click', () => openEvidence(null, pt.dataset.sourceId));
    pt.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openEvidence(null, pt.dataset.sourceId); }
    });
  }
}

// ─── Agent trace ──────────────────────────────────────────────────────────────
function renderTrace(steps) {
  traceList.replaceChildren();
  if (!steps.length) {
    const li = document.createElement('li');
    li.className = 'trace-empty';
    li.textContent = 'No tool call was confirmed in this run.';
    traceList.append(li);
    return;
  }

  for (const group of TRACE_GROUPS) {
    const actual = steps.filter(step => group.phases.includes(step.phase));
    if (!actual.length) continue;
    const li = document.createElement('li');
    const stateValue = actual.some(step => step.status === 'ERROR') ? 'ERROR'
      : actual.some(step => step.status === 'BLOCKED') ? 'BLOCKED' : 'PASS';
    li.className = stateValue.toLowerCase();

    const header = document.createElement('div');
    header.className = 'trace-step-header';

    const name = document.createElement('strong');
    name.textContent = group.label;

    const state = document.createElement('span');
    state.className = 'trace-state';
    state.textContent = stateValue === 'ERROR' ? 'Failed'
      : stateValue === 'BLOCKED' ? 'Stopped' : 'Completed';
    header.append(name, state);

    const detail = document.createElement('small');
    const completedCopy = {
      'Plan investigation': 'Selected a bounded investigation from the question.',
      'Analyze scientific evidence': 'Ran the recorded scientific tool on fictional records.',
      'Save and check evidence': 'Saved or checked evidence in agent memory.',
      'Prepare explained result': 'Prepared the result from recorded evidence.',
    };
    detail.textContent = stateValue === 'PASS' ? completedCopy[group.label] :
      'This step did not complete; open the trace for the exact reason.';
    const technical = document.createElement('details');
    technical.className = 'trace-technical';
    const summary = document.createElement('summary');
    summary.textContent = 'Technical trace';
    technical.append(summary);
    for (const step of actual) {
      const line = document.createElement('small');
      line.textContent = [step.phase, step.tool, step.status, step.detail,
        step.trace_id && `event ${step.trace_id}`,
        step.engine_event_id && `Meterless event ${step.engine_event_id}`,
        step.parent_event_id && `prior event ${step.parent_event_id}`,
        step.query_id && `source query ${step.query_id}`,
        step.provider_request_id && `provider request ${step.provider_request_id}`,
        step.provider_response_id && `provider response ${step.provider_response_id}`,
        step.source_record_ids?.length && `${step.source_record_ids.length} source IDs`]
        .filter(Boolean).join(' · ');
      technical.append(line);
    }
    li.append(header, detail, technical);

    traceList.append(li);
  }
}

// ─── Finding cards ────────────────────────────────────────────────────────────
const KIND_LABELS = {
  observation:           'OBSERVATION',
  association:           'ASSOCIATION',
  hypothesis:            'HYPOTHESIS',
  candidate_contributor: 'QUALIFIED SIGNAL',
  unsupported_hypothesis:'NO EVIDENCE',
  uncertainty:           'CONFOUNDING LIMIT',
  abstention:            'ABSTAINED',
};

function renderFindings(run) {
  const grid = $('#findings');
  grid.replaceChildren();

  $('#finding-count').textContent = `${run.findings.length} ${run.findings.length === 1 ? 'FINDING' : 'FINDINGS'}`;
  const tierLegend = $('#evidence-tier-legend');
  tierLegend.hidden = run.findings.length === 0;

  if (!run.findings.length) {
    const empty = document.createElement('article');
    empty.className = 'finding-card empty-card';
    empty.setAttribute('role', 'listitem');
    empty.innerHTML = `<span class="finding-index">01 / OBSERVATION</span>
      <h4>No findings for this run.</h4>
      <p>The agent did not produce a promotable result. See the status and agent trace for the reason.</p>`;
    grid.append(empty);
    return;
  }

  for (const [idx, finding] of run.findings.entries()) {
    const card = document.createElement('article');
    card.className = `finding-card ${finding.kind}`;
    card.setAttribute('role', 'listitem');

    const idxEl = document.createElement('span');
    idxEl.className = 'finding-index';
    idxEl.textContent = `${String(idx + 1).padStart(2, '0')} / ${KIND_LABELS[finding.kind] ?? finding.kind.toUpperCase()}`;

    const title = document.createElement('h4');
    const explanation = findingExplanation(run, finding);
    title.textContent = explanation.title;

    const body = document.createElement('p');
    body.textContent = explanation.text;

    const prov = document.createElement('span');
    prov.className = 'finding-provenance';
    prov.textContent = finding.source_record_ids?.length
      ? 'Based on fictional records · inspect evidence'
      : 'Interpretive limit · inspect evidence';

    const actions = document.createElement('div');
    actions.className = 'finding-actions';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = finding.source_record_ids?.length ? 'Inspect records ↗' : 'Examine limit ↗';
    btn.setAttribute('aria-label', `${btn.textContent}: ${finding.title}`);
    btn.addEventListener('click', () => openEvidence(finding.finding_id));
    actions.append(btn);

    // Show signal detail link for scientific findings
    if (finding.evidence_signal_id && currentRun?.scientific_evidence?.signals) {
      const sigBtn = document.createElement('button');
      sigBtn.type = 'button';
      sigBtn.textContent = 'Signal detail ↗';
      sigBtn.setAttribute('aria-label', `Signal detail for ${finding.title}`);
      sigBtn.addEventListener('click', () => openEvidenceTab('tab-signals', finding.finding_id));
      actions.append(sigBtn);
    }

    card.append(idxEl, title, body, prov, actions);
    grid.append(card);
  }
}

// ─── Sponsor proof bar ────────────────────────────────────────────────────────
const SPONSOR_LABELS = {
  zetaris:           'Zetaris',
  meterless_engine:  'Meterless Engine',
  meterless_runtime: 'Meterless Runtime',
  nemotron:          'NVIDIA Nemotron',
};

function renderSponsorBar(run) {
  const bar = $('#sponsor-proof-bar');
  if (!run.sponsor_proofs?.length) { bar.hidden = true; return; }

  const container = $('#proof-badges');
  container.replaceChildren();

  for (const proof of run.sponsor_proofs) {
    const badge = document.createElement('div');
    const statusClass = proof.status === 'VERIFIED' ? 'verified'
      : proof.status === 'FAILED' ? 'failed' : 'not-connected';
    badge.className = `proof-badge ${statusClass}`;
    badge.title = proof.trace_id ? `Trace ID: ${proof.trace_id}` : 'No trace ID';

    const dot = document.createElement('span');
    dot.className = 'badge-dot';
    dot.setAttribute('aria-hidden', 'true');

    const label = document.createElement('span');
    label.textContent = `${SPONSOR_LABELS[proof.sponsor] ?? proof.sponsor}: ${proof.status.replace('_', ' ')}`;

    badge.append(dot, label);
    container.append(badge);
  }

  bar.hidden = false;
}

// ─── Clear presentation ───────────────────────────────────────────────────────
function clearPresentation(message) {
  currentRun = null;
  evidenceBtn.disabled = true;
  $('#page-title').innerHTML = 'Waiting for results…';
  $('#breadcrumb-subject').textContent = 'PENDING';
  $('#result-context').textContent = message;
  $('#chart-title').textContent = 'Daily series';
  $('#chart-unit').textContent = '—';
  $('#coverage-label').textContent = 'NO COVERAGE';
  $('#window-badge').textContent = '— DAYS';
  $('.chart-footer').classList.add('no-series');
  $('#chart-help').textContent = 'The series appears after a valid investigation result.';
  $('#chart-container').innerHTML = `<div class="chart-placeholder">
    <span class="placeholder-icon" aria-hidden="true">⬡</span>
    <strong>No current result</strong>
    <span>No figures from a prior run are retained.</span>
  </div>`;
  $('#trajectory-strip').hidden = true;
  $('#period-earlier').textContent = '—';
  $('#period-recent').textContent  = '—';
  $('#period-earlier-dates').textContent = '—';
  $('#period-recent-dates').textContent = '—';
  $('#period-diff').hidden = true;
  $('#period-description').textContent = 'Awaiting a valid comparison.';
  $('#period-footnote').textContent = 'No figure to compare';
  $('#findings').replaceChildren();
  $('#finding-count').textContent = 'NO CURRENT FINDINGS';
  $('#evidence-tier-legend').hidden = true;
  $('#sponsor-proof-bar').hidden = true;
  $('#followup-actions').hidden  = true;
  setTitle(null);
}

// ─── Follow-up context ────────────────────────────────────────────────────────
function updateFollowupBanner() {
  const banner = $('#followup-banner');
  const detail = $('#followup-detail');
  if (pendingParentRunId) {
    detail.textContent = `Continuing from run ${pendingParentRunId.slice(0, 20)} — reading prior World Model decision`;
    banner.hidden = false;
  } else {
    banner.hidden = true;
  }
}

// ─── Question suggestions ─────────────────────────────────────────────────────
for (const chip of $$('[data-fill]')) {
  chip.addEventListener('click', () => {
    questionInput.value = chip.dataset.fill;
    for (const option of $$('.entry-option')) {
      const active = option === chip;
      option.classList.toggle('active', active);
      option.setAttribute('aria-pressed', String(active));
    }
    pendingParentRunId = null;
    updateFollowupBanner();
    questionInput.focus();
  });
}

// ─── Follow-up action chips (post-result) ─────────────────────────────────────
function wireFollowupChips(run) {
  for (const chip of $$('#followup-actions [data-question]')) {
    chip.onclick = () => {
      const q = chip.dataset.question;
      questionInput.value = q;
      // Chips that continue the same investigation carry parent run ID
      if (chip.id === 'chip-next') {
        pendingParentRunId = run.run_id;
      } else {
        pendingParentRunId = null;
      }
      updateFollowupBanner();
      questionInput.focus();
    };
  }
}

// ─── Evidence dialog ──────────────────────────────────────────────────────────
function openEvidence(findingId = null, sourceId = null) {
  if (!currentRun) return;
  activateTab('tab-finding');
  renderEvidenceContent(currentRun, findingId, sourceId);
  $('#dialog-description').textContent = sourceId ? 'Selected fictional record and its source ID.'
    : findingId ? 'Selected finding and its original scientific support.' : 'Sources, scientific tests and run verification.';
  dialog.showModal();
}

function openEvidenceTab(tabId, findingId = null) {
  if (!currentRun) return;
  activateTab(tabId);
  renderEvidenceContent(currentRun, findingId, null);
  dialog.showModal();
}

evidenceBtn.addEventListener('click', () => openEvidence());
$('#dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
dialog.addEventListener('keydown', e => { if (e.key === 'Escape') dialog.close(); });

// ─── Tab switching ────────────────────────────────────────────────────────────
function activateTab(tabId) {
  $('#dialog-title').textContent = 'Evidence & verification';
  const subtitles = {
    'tab-finding': 'Finding and source records', 'tab-signals': 'All pre-planned scientific tests',
    'tab-trace': 'Tools and events actually recorded', 'tab-sponsors': 'Sponsor connection receipts',
    'tab-meta': 'Run metadata and fixed windows',
  };
  $('#dialog-description').textContent = subtitles[tabId] ?? 'Sources and scientific checks';
  for (const tab of $$('.dialog-tab')) {
    const active = tab.id === tabId;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  }
  $('#dialog-content').setAttribute('aria-labelledby', tabId);
  renderEvidenceContent(currentRun, null, null, tabId);
}

$('.dialog-tabs').addEventListener('keydown', event => {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  const tabs = $$('.dialog-tab');
  const current = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
  const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
    : (current + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
  event.preventDefault();
  activateTab(tabs[next].id);
  tabs[next].focus();
});

for (const tab of $$('.dialog-tab')) {
  tab.addEventListener('click', () => {
    activateTab(tab.id);
    renderEvidenceContent(currentRun, null, null, tab.id);
  });
}

// ─── Evidence drawer rendering ────────────────────────────────────────────────
function el(tag, attrs = {}, text = null) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'className') e.className = v;
    else e.setAttribute(k, v);
  }
  if (text !== null) e.textContent = text;
  return e;
}

function mkBlock(title) {
  const s = el('div', { className: 'evidence-block' });
  const h = el('h3', {}, title);
  s.append(h);
  return s;
}

function mkDisclosure(label, open = false) {
  const d = el('details', { className: 'evidence-disclosure' });
  if (open) d.open = true;
  const summary = el('summary', {}, label);
  d.append(summary);
  return d;
}

function mkDl(pairs) {
  const dl = el('dl', { className: 'evidence-dl' });
  for (const [key, val] of pairs) {
    dl.append(el('dt', {}, key), el('dd', {}, String(val ?? '—')));
  }
  return dl;
}

function renderEvidenceContent(run, findingId = null, sourceId = null, activeTab = 'tab-finding') {
  const content = $('#dialog-content');
  content.replaceChildren();

  if (!run) {
    content.append(el('p', {}, 'Start an investigation to inspect records and tool outputs.'));
    return;
  }

  const days = windowDays(run);

  switch (activeTab) {
    case 'tab-finding':  renderFindingTab(run, findingId, sourceId, days); break;
    case 'tab-signals':  renderSignalsTab(run, findingId); break;
    case 'tab-trace':    renderTraceTab(run); break;
    case 'tab-sponsors': renderSponsorsTab(run); break;
    case 'tab-meta':     renderMetaTab(run, days); break;
    default:             renderFindingTab(run, findingId, sourceId, days);
  }
}

// Tab: Finding / source record
function renderFindingTab(run, findingId, sourceId, days) {
  const content = $('#dialog-content');

  // Offline benchmark badge
  if (isBenchmarkRun(run)) {
    const badge = el('div', { className: 'benchmark-badge' });
    badge.innerHTML = `⚗ OFFLINE SCIENTIFIC EXHIBIT &nbsp;·&nbsp; ${days}-DAY SYNTHETIC BENCHMARK &nbsp;·&nbsp; NOT A LIVE RESULT`;
    content.append(badge);
  }

  const selected = run.findings.find(f => f.finding_id === findingId) || run.findings[0];
  const point    = sourceId
    ? run.series?.flatMap(s => s.points.map(p => ({ ...p, unit: s.unit }))).find(p => p.source_record_id === sourceId)
    : null;

  // Lead block
  const lead = mkBlock(sourceId ? 'SELECTED CHART RECORD' : 'SELECTED FINDING');
  const heading = el('h4', {}, point
    ? `${point.local_date} · ${point.value} ${point.unit}`
    : selected ? findingExplanation(run, selected).title : 'No finding available');
  const summary = el('p', {}, point
    ? 'This data point was returned by the Python core. The ID identifies a typed synthetic record.'
    : (selected ? findingExplanation(run, selected).text : run.summary));
  lead.append(heading, summary);
  if (selected) {
    const raw = mkDisclosure('Original scientific wording and source IDs');
    raw.append(el('p', {}, selected.text));
    lead.append(raw);
  }

  if (point) {
    lead.append(el('code', { className: 'selected-source' }, point.source_record_id));
  } else if (selected?.source_record_ids?.length) {
    const disc = mkDisclosure(`Show ${selected.source_record_ids.length} synthetic record IDs`);
    const ids = el('div', { className: 'source-list' });
    for (const id of selected.source_record_ids) ids.append(el('code', {}, id));
    disc.append(ids); lead.append(disc);
  } else {
    lead.append(el('p', { className: 'evidence-limit' },
      'This limit statement is not attributed to a measured record.'));
  }
  content.append(lead);

  // Evidence kind explanation
  if (selected?.kind) {
    const kindBlock = mkBlock('EVIDENCE TIER');
    const kindMap = {
      candidate_contributor: 'QUALIFIED SIGNAL — passed all predeclared temporal, block-bootstrap and multiple-testing gates.',
      association:           'UNQUALIFIED ASSOCIATION — raw correlation did not pass every gate. Do not interpret as a cause.',
      hypothesis:            'HYPOTHESIS — exploratory. Requires further investigation and preregistration.',
      unsupported_hypothesis:'NO EVIDENCE — no tested factor met the required gates for this outcome.',
      uncertainty:           'UNCERTAINTY — overlapping factors may change together. The analysis cannot isolate a cause.',
      abstention:            'RESPONSIBLE ABSTENTION — the question or evidence falls outside the verifiable scope.',
      observation:           'RECORDED CHANGE — what happened in the observed periods, not why.',
    };
    kindBlock.append(el('p', {}, kindMap[selected.kind] ?? selected.kind));
    content.append(kindBlock);
  }
}

// Tab: Scientific signals
function renderSignalsTab(run, findingId) {
  const content = $('#dialog-content');

  if (!run.scientific_evidence?.signals?.length) {
    // v1 route: no signal table
    const note = mkBlock('SCIENTIFIC SIGNALS');
    note.append(el('p', {}, 'No scientific signal table was published for this run. Inspect its plan, trace, and status for the reason.'));
    content.append(note);
    return;
  }

  const { signals, plan_sha256, record_digest_sha256, hypothesis_count, engine } = run.scientific_evidence;

  // Benchmark badge
  if (isBenchmarkRun(run)) {
    const badge = el('div', { className: 'benchmark-badge' });
    badge.innerHTML = `⚗ OFFLINE BENCHMARK SIGNALS &nbsp;·&nbsp; ${windowDays(run)}-DAY WINDOW &nbsp;·&nbsp; SEED NOT LIVE-CONNECTED`;
    content.append(badge);
  }

  const intro = mkBlock(`${hypothesis_count} PRE-PLANNED SCIENTIFIC TESTS · ALL RESULTS SHOWN`);
  intro.append(el('p', {},
    `PHIS planned these ${hypothesis_count} tests before looking at the results. ` +
    `Every result is shown, including tests that found no qualified signal. ` +
    `A test is a statistical check, not a participant or a diagnosis.`));
  const planDetails = mkDisclosure('Technical plan and source digests');
  planDetails.append(mkDl([
    ['Engine', engine ?? '—'],
    ['Plan SHA-256', (plan_sha256 ?? '—').slice(0, 24) + '…'],
    ['Record digest SHA-256', (record_digest_sha256 ?? '—').slice(0, 24) + '…'],
  ]));
  intro.append(planDetails);
  content.append(intro);

  // Signal table
  const tableBlock = mkBlock('ALL SCIENTIFIC TEST RESULTS');
  tableBlock.append(el('p', { className: 'evidence-limit' },
    'These are unadjusted pairwise observational associations in fictional synthetic data. Not causal or clinical claims.'));
  tableBlock.append(el('p', {}, 'Technical statistics below: r is correlation, N is the number of paired observations, CI is an uncertainty interval, and p and q are statistical checks.'));

  const table = el('table', { className: 'signal-table' });
  const thead = el('thead');
  thead.innerHTML = `<tr>
    <th>Exposure → Outcome</th>
    <th>Lag</th>
    <th>r</th>
    <th>N</th>
    <th>95% CI</th>
    <th>p</th>
    <th>q child (BY)</th>
    <th>Class</th>
    <th>Temporal</th>
  </tr>`;
  const tbody = el('tbody');

  const selected = findingId
    ? signals.find(s => s.signal_id === findingId)
    : null;

  for (const sig of signals) {
    const tr = el('tr');
    tr.className = sig.classification;
    if (sig.signal_id === (selected?.signal_id ?? signals[0]?.signal_id)) {
      tr.style.background = '#f0f8f0';
    }

    const pill = el('span', { className: `sig-class-pill ${sig.classification}` },
      sig.classification.replace('_', ' '));

    const ci = sig.ci95 ? `[${sig.ci95[0]?.toFixed(3)}, ${sig.ci95[1]?.toFixed(3)}]` : '—';
    const temporal = sig.temporal_state ?? (sig.temporal_reasons?.length ? sig.temporal_reasons.join(', ') : '—');

    tr.innerHTML = `
      <td>${(sig.exposure ?? '—').replace(/_/g, ' ')} → ${(sig.outcome ?? '—').replace(/_/g, ' ')}</td>
      <td>${sig.lag_days ?? '—'} d</td>
      <td>${typeof sig.effect === 'number' ? sig.effect.toFixed(3) : '—'}</td>
      <td>${sig.raw_n ?? '—'}</td>
      <td>${ci}</td>
      <td>${typeof sig.p_primary === 'number' ? sig.p_primary.toFixed(4) : '—'}</td>
      <td>${typeof sig.q_selection_child_by === 'number' ? sig.q_selection_child_by.toFixed(4) : '—'}</td>
      <td></td>
      <td>${temporal}</td>
    `;
    tr.cells[7].append(pill);
    tbody.append(tr);
  }
  table.append(thead, tbody);
  tableBlock.append(table);
  content.append(tableBlock);
}

// Tab: Tool trace
function renderTraceTab(run) {
  const content = $('#dialog-content');
  const block = mkBlock('TECHNICAL TRACE — EVERY RECORDED STEP');
  block.append(el('p', {},
    'Every tool call returned by the Python core. Blocked steps are explicitly recorded, never silently dropped.'));

  if (!run.tool_trace?.length) {
    block.append(el('p', {}, 'No tool trace for this run.'));
    content.append(block);
    return;
  }

  const list = el('ol', { className: 'trace-detail' });
  for (const step of run.tool_trace) {
    const li = el('li');
    const header = el('div', { className: 'td-header' });
    const name   = el('strong', {}, step.tool);
    const status = el('span', { className: `td-status ${step.status.toLowerCase()}` }, step.status);

    if (step.phase) {
      const pp = el('span', { className: `trace-phase-pill ${step.phase.toLowerCase()}` }, step.phase);
      header.append(name, status, pp);
    } else {
      header.append(name, status);
    }

    const detail = el('span', {}, step.detail || '');
    li.append(header, detail);

    if (step.source_record_ids?.length) {
      li.append(el('small', {}, `${step.source_record_ids.length} synthetic record IDs · event ${(step.trace_id || '').slice(0, 16)}`));
    }
    if (step.engine_event_id) {
      li.append(el('small', {}, `Meterless Engine event ID: ${step.engine_event_id}`));
    }
    if (step.query_id) {
      li.append(el('small', {}, `Zetaris query ID sent by PHIS: ${step.query_id} (not echoed by server)`));
    }
    if (step.parent_event_id) {
      li.append(el('small', {}, `Based on prior Engine event: ${step.parent_event_id}`));
    }
    list.append(li);
  }
  block.append(list);
  content.append(block);
}

// Tab: Sponsor proofs
function renderSponsorsTab(run) {
  const content = $('#dialog-content');

  const intro = mkBlock('TECHNICAL VERIFICATION — SPONSOR CONNECTIONS');
  intro.append(el('p', {},
    'Status is determined each run. A VERIFIED status means a real round-trip was traced. ' +
    'NOT_CONNECTED means the service is not wired in this run. ' +
    'No mock result is presented as a live sponsor connection.'));
  content.append(intro);

  for (const proof of (run.sponsor_proofs ?? [])) {
    const block = mkBlock(`${SPONSOR_LABELS[proof.sponsor] ?? proof.sponsor}`);
    const cls   = proof.status === 'VERIFIED' ? 'sponsor-proof-verified' : '';
    const sb    = el('div', { className: `sponsor-block ${cls}` });
    sb.append(el('p', {}, `Status: ${proof.status.replace('_', ' ')}`));

    if (proof.trace_id) {
      sb.append(el('p', {}, `Trace ID: ${proof.trace_id}`));
    }
    if (proof.status === 'NOT_CONNECTED') {
      sb.append(el('p', {}, 'This service was not contacted in this run. No call was made and no result was fabricated.'));
    }
    block.append(sb);
    content.append(block);
  }

  // Hardcoded absent sponsors for transparency
  const present = (run.sponsor_proofs ?? []).map(p => p.sponsor);
  for (const [key, label] of Object.entries(SPONSOR_LABELS)) {
    if (!present.includes(key)) {
      const block = mkBlock(label);
      const sb    = el('div', { className: 'sponsor-block' });
      sb.append(el('p', {}, 'Status: NOT_CONNECTED — not wired in this run.'));
      block.append(sb);
      content.append(block);
    }
  }
}

// Tab: Run metadata
function renderMetaTab(run, days) {
  const content = $('#dialog-content');
  const block = mkBlock('RUN METADATA');

  const isBenchmark = isBenchmarkRun(run);
  if (isBenchmark) {
    const badge = el('div', { className: 'benchmark-badge' });
    badge.innerHTML = `⚗ OFFLINE BENCHMARK &nbsp;·&nbsp; ${days}-DAY SYNTHETIC WINDOW &nbsp;·&nbsp; NOT CONNECTED TO LIVE ZETARIS`;
    block.append(badge);
  }

  block.append(mkDl([
    ['Dataset',           run.dataset_id ?? '—'],
    ['Contract version',  run.contract_version ?? '—'],
    ['Mode',              run.mode ?? '—'],
    ['Scenario',          run.scenario ?? '—'],
    ['Analysis window',   `${run.window?.start ?? '—'} to ${run.window?.end ?? '—'} (${days} days)`],
    ['Time zone',         run.timezone ?? '—'],
    ['Run ID',            run.run_id ?? '—'],
    ['Parent run ID',     run.parent_run_id ?? 'None'],
    ['Status',            run.status ?? '—'],
    ...(run.contract_version === 'investigation.v4' ? [['Planner mode', run.planner_mode ?? '—']] : []),
    ['Reason code',       run.reason_code ?? '—'],
    ...( run.coverage?.map(c => [`Coverage: ${c.variable}`, `${c.observed} of ${c.eligible} days (${(100 * c.observed / c.eligible).toFixed(0)}%)`]) ?? []),
  ]));

  if (run.comparison) {
    const { baseline, comparison, method } = run.comparison;
    const cmpBlock = mkBlock('PERIOD COMPARISON METHOD');
    cmpBlock.append(el('p', {},
      `${method}: ${baseline.start}–${baseline.end} (N=${baseline.observed}) ` +
      `versus ${comparison.start}–${comparison.end} (N=${comparison.observed}). ` +
      `Unrecorded measurements remain null. No proof of association or causality.`));
    content.append(cmpBlock);
  }

  content.append(block);
}

// ─── Window label ─────────────────────────────────────────────────────────────
function updateWindowLabel(run) {
  const wl = $('#window-label');
  if (run.window?.start && run.window?.end) {
    wl.textContent = `${formatDate(run.window.start).toUpperCase()} — ${formatDate(run.window.end).toUpperCase()} ${run.window.end.slice(0, 4)}`;
    wl.setAttribute('aria-label', `Analysis window: ${formatDate(run.window.start)} to ${formatDate(run.window.end)}`);
  }
}

// ─── Rail mode label ──────────────────────────────────────────────────────────
function updateModeUI(run) {
  const zetaris = run.sponsor_proofs?.find(p => p.sponsor === 'zetaris');
  const isLive  = run.mode === 'LIVE_SYNTHETIC_ZETARIS';
  const pill    = $('#mode-pill');
  const label   = $('#mode-label');

  pill.classList.toggle('live', isLive && zetaris?.status === 'VERIFIED');
  label.textContent = sourceLabel(run);

  const plannerNote = run.contract_version === 'investigation.v4'
    ? (run.planner_mode === 'NIGHTSHIFT_VERIFIED' ? 'Verified Nightshift planner.'
      : run.planner_mode === 'NVIDIA_VERIFIED' ? 'Verified NVIDIA Nemotron planner.'
      : `Planner: ${run.planner_mode?.toLowerCase() ?? 'unavailable'}; hosted inference not verified.`)
    : '';
  $('#demo-sponsor-status').textContent = isLive
    ? `Zetaris: ${zetaris?.status ?? 'NOT_CONNECTED'}. ${plannerNote} No medical advice.`
    : `Local synthetic mode. ${plannerNote} No medical advice.`;

  $('#rail-mode-label').textContent = isLive && zetaris?.status === 'VERIFIED' ? 'LIVE EVIDENCE' : 'EVIDENCE LAB';
}

// ─── Status messages ──────────────────────────────────────────────────────────
const STATUS_STATES = {
  PASS: {
    kind: '',
    label: 'RESULT READY',
    copy: (run) => run.scientific_evidence
      ? 'See the recorded change and the patterns that passed scientific checks below. None proves a cause.'
      : 'A recorded change is available below. Cause is not established.',
  },
  EXECUTED_PARTIAL: { kind: 'warning', label: 'PARTIAL RESULT',  copy: (run) => run.summary },
  INSUFFICIENT_DATA:{ kind: 'warning', label: 'INSUFFICIENT EVIDENCE', copy: (run) => run.summary },
  BLOCKED:          { kind: 'warning', label: 'RESPONSIBLE ABSTENTION', copy: (run) => run.summary },
  ERROR:            { kind: 'error',   label: 'TOOL UNAVAILABLE', copy: (run) => run.summary },
};

const PHASE_LABELS = {
  PASS: 'RESULT READY',
  EXECUTED_PARTIAL: 'PARTIAL RESULT',
  INSUFFICIENT_DATA: 'INSUFFICIENT COVERAGE',
  BLOCKED: 'ABSTENTION',
  ERROR: 'SOURCE OR TOOL UNAVAILABLE',
};

const PHASE_CLASSES = {
  PASS: 'phase-tag phase-pass',
  EXECUTED_PARTIAL: 'phase-tag phase-warn',
  INSUFFICIENT_DATA: 'phase-tag phase-warn',
  BLOCKED: 'phase-tag phase-warn',
  ERROR: 'phase-tag phase-error',
};

// ─── Main form submit ─────────────────────────────────────────────────────────
form.addEventListener('submit', async event => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) { questionInput.focus(); return; }

  const parentRunId = pendingParentRunId;

  clearPresentation('Analyzing the fictional records — please wait.');
  askButton.disabled = true;
  askButton.querySelector('.ask-label').textContent = 'Analyzing records…';
  for (const chip of $$('[data-question], .entry-option')) chip.disabled = true;
  $('#main').setAttribute('aria-busy', 'true');
  agentPhase.className = 'phase-tag phase-running';
  agentPhase.textContent = 'IN PROGRESS';
  traceList.innerHTML = '<li class="trace-empty">Working through the investigation. Completed steps will appear here.</li>';
  setStatus('busy', 'INVESTIGATION IN PROGRESS', 'Analyzing the fictional records. No findings are confirmed yet.', 'IN PROGRESS');

  try {
    const params = new URLSearchParams(location.search);
    const analysisVersion = ['v1','v2','v3','v4'].includes(params.get('analysis')) ? params.get('analysis') : 'v3';
    const scenario = params.get('scenario') || (analysisVersion === 'v1' || analysisVersion === 'v2' ? 'normal' : 'opportunity');

    currentRun = await fetchInvestigation(question, { scenario, parentRunId, analysisVersion });
    incrementRunCounter();

    updateModeUI(currentRun);
    updateWindowLabel(currentRun);

    pendingParentRunId = null;
    updateFollowupBanner();

    renderTrace(currentRun.tool_trace);
    renderChart(currentRun);
    renderTrajectory(currentRun);
    renderPeriod(currentRun);
    renderFindings(currentRun);
    renderSponsorBar(currentRun);

    // Status
    const state = STATUS_STATES[currentRun.status] || STATUS_STATES.ERROR;
    setStatus(state.kind, state.label, state.copy(currentRun), currentRun.run_id);
    agentPhase.className = PHASE_CLASSES[currentRun.status] ?? 'phase-tag phase-warn';
    agentPhase.textContent = PHASE_LABELS[currentRun.status] ?? 'UNKNOWN';

    // Result context line
    const ctxEl = $('#result-context');
    ctxEl.textContent = currentRun.parent_run_id
      ? `Follow-up based on the prior investigation saved in agent memory. Inspect the technical trace for the linked run.`
      : currentRun.status === 'PASS'
        ? `180 days of fictional records, ${plainDate(currentRun.window.start)}–${plainDate(currentRun.window.end)}. The comparison dates were fixed before this question.`
        : 'No scientific result was published for this run. The status and evidence panel explain why.';

    // Enable evidence drawer and follow-up chips
    evidenceBtn.disabled = false;
    if (canContinueFrom(currentRun)) {
      $('#followup-actions').hidden = false;
      wireFollowupChips(currentRun);
    }

    // Open signals tab by default if scientific_evidence present
    if (currentRun.scientific_evidence?.signals?.length) activateTab('tab-signals');

    $('#main').focus();
  } catch (error) {
    clearPresentation('The investigation did not return a valid result.');
    agentPhase.className = 'phase-tag phase-error';
    agentPhase.textContent = 'NO RESPONSE';
    renderTrace([]);
    setStatus('error', 'CONNECTION OR CONTRACT ERROR',
      'Could not get a valid result. The local service may be unavailable, or the result did not pass validation.');
    console.error('[PHIS] API response rejected:', error);
  } finally {
    askButton.disabled = false;
    askButton.querySelector('.ask-label').textContent = 'Investigate records';
    for (const chip of $$('[data-question], .entry-option')) chip.disabled = false;
    $('#main').removeAttribute('aria-busy');
  }
});

// Reset follow-up context when user manually edits the question
questionInput.addEventListener('input', () => {
  pendingParentRunId = null;
  updateFollowupBanner();
});

// Responsive chart redraw on resize
window.addEventListener('resize', () => {
  if (currentRun?.series?.[0]?.points.length) renderChart(currentRun);
});

// Keyboard: Escape closes dialog
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && dialog.open) dialog.close();
});
