/** @typedef {import('../contracts/investigation.v1.d.ts').InvestigationV1} InvestigationV1 */

/**
 * Validates an investigation.v2 (scientific) response.
 * The 16-child predeclared family, sponsor proofs, and Engine trace
 * must all be present and cross-referenced.
 */
export function validateScientificInvestigation(value) {
  if (!value || value.contract_version !== 'investigation.v2' || value.synthetic !== true ||
      !['SYNTHETIC_LOCAL_ONLY','LIVE_SYNTHETIC_ZETARIS'].includes(value.mode) ||
      !['PASS','BLOCKED','ERROR','INSUFFICIENT_DATA'].includes(value.status))
    throw new Error('Invalid scientific contract');

  if (!value.window?.start || !value.window?.end || !Array.isArray(value.findings) ||
      !Array.isArray(value.tool_trace) || !Array.isArray(value.sponsor_proofs) ||
      !Array.isArray(value.series) || !Array.isArray(value.coverage))
    throw new Error('Incomplete scientific response');

  const zetaris = value.sponsor_proofs.find(item => item.sponsor === 'zetaris');
  const engine  = value.sponsor_proofs.find(item => item.sponsor === 'meterless_engine');

  if (!zetaris || !engine ||
      !['VERIFIED','NOT_CONNECTED','FAILED'].includes(zetaris.status) ||
      !['VERIFIED','NOT_CONNECTED'].includes(engine.status))
    throw new Error('Invalid sponsor proof');

  if (engine.status === 'VERIFIED' &&
      !value.tool_trace.some(item => item.trace_id === engine.trace_id && item.engine_event_id))
    throw new Error('Untraced Engine proof');

  if (value.mode === 'SYNTHETIC_LOCAL_ONLY' && zetaris.status !== 'NOT_CONNECTED')
    throw new Error('False Zetaris proof in local mode');

  if (value.status === 'PASS') {
    const evidence = value.scientific_evidence;
    if (!evidence || evidence.hypothesis_count !== 16 || evidence.signals?.length !== 16 ||
        !/^[a-f0-9]{64}$/.test(evidence.plan_sha256) ||
        !/^[a-f0-9]{64}$/.test(evidence.record_digest_sha256))
      throw new Error('Missing Discovery family');

    if (evidence.signals.some(signal =>
        signal.exposure === 'unrelated_count' && signal.classification === 'candidate_signal'))
      throw new Error('Promoted negative control');

    if (value.mode === 'LIVE_SYNTHETIC_ZETARIS') {
      const ids = evidence.source_query?.request_ids;
      if (zetaris.status !== 'VERIFIED' || !Array.isArray(ids) || ids.length !== 3 ||
          new Set(ids).size !== 3 || zetaris.trace_id !== ids[0] ||
          ids.some(id => !value.tool_trace.some(step =>
            step.tool === 'zetaris.query_v2' && step.trace_id === id && step.query_id)))
        throw new Error('Untraced Zetaris pagination');
    }
  } else if (value.scientific_evidence !== null || value.comparison !== null || value.series.length) {
    throw new Error('Stale scientific evidence after failure');
  }

  if (value.findings.some(item =>
      !['observation','association','candidate_contributor','unsupported_hypothesis','uncertainty','abstention']
        .includes(item.kind) ||
      !Array.isArray(item.source_record_ids)))
    throw new Error('Invalid scientific finding');

  return value;
}

/**
 * Validates any investigation response (v1 or v2).
 * Dispatches to validateScientificInvestigation for v2.
 * All field checks are English.
 */
export function validateInvestigation(value) {
  if (value?.contract_version === 'investigation.v2') return validateScientificInvestigation(value);
  if (['investigation.v3', 'investigation.v4'].includes(value?.contract_version))
    return validateLongitudinalInvestigation(value);

  if (!value || value.contract_version !== 'investigation.v1' ||
      !['SYNTHETIC_LOCAL_ONLY','LIVE_SYNTHETIC_ZETARIS'].includes(value.mode))
    throw new Error('Unsupported contract version or mode');

  if (!['PASS','EXECUTED_PARTIAL','INSUFFICIENT_DATA','BLOCKED','ERROR'].includes(value.status))
    throw new Error('Unknown status value');

  if (typeof value.run_id !== 'string' || typeof value.summary !== 'string' ||
      !value.window?.start || !value.window?.end)
    throw new Error('Incomplete run fields');

  if (!Array.isArray(value.coverage) || !Array.isArray(value.series) ||
      !Array.isArray(value.findings) || !Array.isArray(value.tool_trace) ||
      !Array.isArray(value.sponsor_proofs))
    throw new Error('Missing required collections');

  const zetaris = value.sponsor_proofs.find(proof => proof.sponsor === 'zetaris');
  const engine  = value.sponsor_proofs.find(proof => proof.sponsor === 'meterless_engine');

  if (value.sponsor_proofs.some(proof =>
      !['NOT_CONNECTED','VERIFIED','FAILED'].includes(proof.status) ||
      (proof.status !== 'VERIFIED' && proof.trace_id !== null) ||
      (proof.status === 'VERIFIED' && proof.sponsor !== 'zetaris' &&
        !value.tool_trace.some(step => step.trace_id === proof.trace_id)) ||
      (proof.sponsor !== 'zetaris' && proof.sponsor !== 'meterless_engine' &&
        proof.status !== 'NOT_CONNECTED') ||
      (proof.sponsor === 'meterless_engine' && proof.status === 'FAILED')))
    throw new Error('Unexpected sponsor proof status or trace');

  if (value.mode === 'SYNTHETIC_LOCAL_ONLY' && zetaris?.status !== 'NOT_CONNECTED')
    throw new Error('Unexpected Zetaris proof in local mode');

  if (engine?.status === 'VERIFIED' && (
      !/^[0-9a-f]{64}$/.test(engine.trace_id) ||
      engine.trace_id === zetaris?.trace_id ||
      !value.tool_trace.some(step =>
        step.trace_id === engine.trace_id &&
        step.tool !== 'zetaris.synthetic_query' &&
        step.phase)))
    throw new Error('Unexpected Engine proof trace');

  if (value.mode === 'LIVE_SYNTHETIC_ZETARIS') {
    if (!zetaris) throw new Error('Missing Zetaris proof');
    const query = value.tool_trace.find(step =>
      step.tool === 'zetaris.synthetic_query' && step.trace_id === zetaris.trace_id);
    if (zetaris.status === 'VERIFIED' && (
        !zetaris.trace_id || !query || query.status !== 'PASS' ||
        query.source_record_ids.length !== 156 ||
        !query.query_id || !/^[0-9a-f]{64}$/.test(query.sql_sha256)))
      throw new Error('Zetaris proof not traceable');
    if (value.status === 'PASS' && zetaris.status !== 'VERIFIED')
      throw new Error('Zetaris proof not traceable on PASS');
    if (value.reason_code === 'source_error' && (
        value.status !== 'ERROR' || value.coverage.length || value.series.length ||
        value.comparison !== null || zetaris.status === 'VERIFIED'))
      throw new Error('Source error state with unexpected data');
  }

  for (const series of value.series) {
    if (!['energy','sleep_hours'].includes(series.variable) ||
        !['score/10','hours'].includes(series.unit))
      throw new Error('Invalid variable or unit');
    if (!Array.isArray(series.points)) throw new Error('Invalid series points');
    for (const point of series.points) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(point.local_date)) throw new Error('Invalid date');
      if (point.value === null && point.source_record_id !== null) throw new Error('Gap with source ID');
      if (point.value !== null && (
          !Number.isFinite(point.value) || !/^SYN-[A-Z0-9_-]+$/.test(point.source_record_id)))
        throw new Error('Value without valid source ID');
    }
  }

  if (value.findings.some(finding =>
      !['observation','association','hypothesis','uncertainty','abstention'].includes(finding.kind)))
    throw new Error('Unknown finding kind');

  if (value.tool_trace.some(step =>
      !['PASS','BLOCKED','ERROR'].includes(step.status) ||
      (step.phase && !['PLAN','TOOLS','EVIDENCE','VERIFY','RESPOND','ABSTAIN'].includes(step.phase)) ||
      !Array.isArray(step.source_record_ids)))
    throw new Error('Unknown trace step');

  if (value.comparison) {
    const c = value.comparison;
    if (!Number.isFinite(c.baseline?.mean) || !Number.isFinite(c.comparison?.mean) ||
        !Number.isFinite(c.difference))
      throw new Error('Invalid comparison');
    if (!c.source_record_ids?.length) throw new Error('Comparison missing sources');
  }

  if (value.status !== 'PASS' && value.comparison !== null)
    throw new Error('Comparison present on non-PASS status');

  return value;
}

/** Validate the exact 180-day response and its source/engine provenance. */
export function validateLongitudinalInvestigation(value) {
  if (!value || value.synthetic !== true ||
      !['investigation.v3', 'investigation.v4'].includes(value.contract_version) ||
      !['SYNTHETIC_LOCAL_ONLY', 'LIVE_SYNTHETIC_ZETARIS'].includes(value.mode) ||
      !['PASS', 'BLOCKED', 'ERROR', 'INSUFFICIENT_DATA'].includes(value.status) ||
      typeof value.run_id !== 'string' || typeof value.summary !== 'string' ||
      !Array.isArray(value.findings) || !Array.isArray(value.series) ||
      !Array.isArray(value.coverage) || !Array.isArray(value.tool_trace) ||
      !Array.isArray(value.sponsor_proofs))
    throw new Error('Invalid 180-day investigation contract');
  const zetaris = value.sponsor_proofs.find(p => p.sponsor === 'zetaris');
  const engine = value.sponsor_proofs.find(p => p.sponsor === 'meterless_engine');
  if (!zetaris || !engine ||
      (value.mode === 'SYNTHETIC_LOCAL_ONLY' && zetaris.status !== 'NOT_CONNECTED') ||
      (value.mode === 'LIVE_SYNTHETIC_ZETARIS' && value.status === 'PASS' && zetaris.status !== 'VERIFIED'))
    throw new Error('Invalid source provenance');
  if (value.scientific_evidence) {
    const evidence = value.scientific_evidence;
    if (value.status !== 'PASS' || evidence.hypothesis_count !== 16 ||
        evidence.signals?.length !== 16 || !/^[a-f0-9]{64}$/.test(evidence.record_digest_sha256) ||
        !/^[a-f0-9]{64}$/.test(evidence.plan_sha256) ||
        evidence.signals.some(s => s.exposure === 'unrelated_count' && s.classification === 'candidate_signal') ||
        engine.status !== 'VERIFIED')
      throw new Error('Invalid Discovery evidence');
    if (value.mode === 'LIVE_SYNTHETIC_ZETARIS') {
      const pages = value.tool_trace.filter(s => s.tool === 'zetaris.query_180d');
      const ids = evidence.source_query?.request_ids;
      const queryIds = evidence.source_query?.query_ids;
      if (pages.length !== 6 || pages.reduce((n, p) => n + p.row_count, 0) !== 1080 ||
          ids?.length !== 6 || ids.some((id, i) => id !== pages[i].trace_id) ||
          new Set(ids).size !== 6 || queryIds?.length !== 6 ||
          new Set(queryIds).size !== 6 || zetaris.trace_id !== ids[0] ||
          pages.some((page, i) => page.status !== 'PASS' ||
            !/^[a-f0-9]{64}$/.test(page.sql_sha256) ||
            queryIds[i] !== page.query_id))
        throw new Error('Untraced Zetaris readback');
    }
  } else if (value.contract_version === 'investigation.v3' && value.status === 'PASS') {
    throw new Error('Missing Discovery evidence');
  }
  if (value.status !== 'PASS' && (value.scientific_evidence || value.comparison || value.series.length))
    throw new Error('Stale evidence after failure');
  if (value.contract_version === 'investigation.v4' &&
      !['NIGHTSHIFT_VERIFIED', 'NIGHTSHIFT_PARTIAL', 'SIMULATED', 'LOCAL DETERMINISTIC MODE', 'BLOCKED']
        .includes(value.planner_mode))
    throw new Error('Unknown planner provenance');
  return value;
}

/**
 * Sends a POST to /api/investigations.
 * Requests the actual 180-day scientific route by default.
 * Validates the response against the contract.
 */
export async function fetchInvestigation(question, {
  scenario = 'opportunity',
  parentRunId = null,
  analysisVersion = 'v3',
  fetcher = fetch,
} = {}) {
  const response = await fetcher('/api/investigations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      scenario,
      ...(parentRunId ? { parent_run_id: parentRunId } : {}),
      ...(analysisVersion !== 'v1' ? { analysis_version: analysisVersion } : {}),
    }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return validateInvestigation(payload);
}
