/** @typedef {import('../contracts/investigation.v1.d.ts').InvestigationV1} InvestigationV1 */

export function validateInvestigation(value) {
  if (!value || value.contract_version !== 'investigation.v1' || !['SYNTHETIC_LOCAL_ONLY','LIVE_SYNTHETIC_ZETARIS'].includes(value.mode)) throw new Error('Unsupported contract or mode');
  if (!['PASS','EXECUTED_PARTIAL','INSUFFICIENT_DATA','BLOCKED','ERROR'].includes(value.status)) throw new Error('Unknown status');
  if (typeof value.run_id !== 'string' || typeof value.summary !== 'string' || !value.window?.start || !value.window?.end) throw new Error('Incomplete run');
  if (!Array.isArray(value.coverage) || !Array.isArray(value.series) || !Array.isArray(value.findings) || !Array.isArray(value.tool_trace) || !Array.isArray(value.sponsor_proofs)) throw new Error('Missing collections');
  const zetaris = value.sponsor_proofs.find(proof => proof.sponsor === 'zetaris');
  if (value.sponsor_proofs.some(proof => proof.sponsor !== 'zetaris' && (proof.status !== 'NOT_CONNECTED' || proof.trace_id !== null))) throw new Error('Unexpected sponsor proof');
  if (value.mode === 'SYNTHETIC_LOCAL_ONLY' && value.sponsor_proofs.some(proof => proof.status !== 'NOT_CONNECTED' || proof.trace_id !== null)) throw new Error('Unexpected sponsor proof');
  if (value.mode === 'LIVE_SYNTHETIC_ZETARIS') {
    if (!zetaris) throw new Error('Missing Zetaris proof');
    const query = value.tool_trace.find(step => step.tool === 'zetaris.synthetic_query' && step.trace_id === zetaris.trace_id);
    if (zetaris.status === 'VERIFIED' && (!zetaris.trace_id || !query || query.status !== 'PASS' || query.source_record_ids.length !== 156 || !query.query_id || !/^[0-9a-f]{64}$/.test(query.sql_sha256))) throw new Error('Untraceable Zetaris proof');
    if (value.status === 'PASS') {
      if (zetaris.status !== 'VERIFIED') throw new Error('Untraceable Zetaris proof');
    }
    if (value.reason_code === 'source_error' && (value.status !== 'ERROR' || value.coverage.length || value.series.length || value.comparison !== null || zetaris.status === 'VERIFIED')) throw new Error('Zetaris failure with unverified data');
  }
  for (const series of value.series) {
    if (!['energy','sleep_hours'].includes(series.variable) || !['score/10','hours'].includes(series.unit)) throw new Error('Invalid variable or unit');
    if (!Array.isArray(series.points)) throw new Error('Invalid series');
    for (const point of series.points) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(point.local_date)) throw new Error('Invalid date');
      if (point.value === null && point.source_record_id !== null) throw new Error('Missing day has a source');
      if (point.value !== null && (!Number.isFinite(point.value) || !/^SYN-[A-Z0-9_-]+$/.test(point.source_record_id))) throw new Error('Value without a source');
    }
  }
  if (value.findings.some(finding => !['observation','association','hypothesis','uncertainty','abstention'].includes(finding.kind))) throw new Error('Unknown finding type');
  if (value.tool_trace.some(step => !['PASS','BLOCKED','ERROR'].includes(step.status)
    || (step.phase && !['PLAN','TOOLS','EVIDENCE','VERIFY','RESPOND','ABSTAIN'].includes(step.phase))
    || !Array.isArray(step.source_record_ids))) throw new Error('Unknown trace');
  if (value.comparison) {
    const c = value.comparison;
    if (!Number.isFinite(c.baseline?.mean) || !Number.isFinite(c.comparison?.mean) || !Number.isFinite(c.difference)) throw new Error('Invalid comparison');
    if (!c.source_record_ids?.length) throw new Error('Comparison without sources');
  }
  if (value.status !== 'PASS' && value.comparison !== null) throw new Error('Comparison in an invalid state');
  return value;
}

export async function fetchInvestigation(question, { scenario = 'normal', parentRunId = null, fetcher = fetch } = {}) {
  const response = await fetcher('/api/investigations', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, scenario, ...(parentRunId ? { parent_run_id: parentRunId } : {}) }),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
  return validateInvestigation(payload);
}
