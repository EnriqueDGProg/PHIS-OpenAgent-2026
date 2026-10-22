/** @typedef {import('../contracts/investigation.v1.d.ts').InvestigationV1} InvestigationV1 */

export function validateInvestigation(value) {
  if (!value || value.contract_version !== 'investigation.v1' || !['SYNTHETIC_LOCAL_ONLY','LIVE_SYNTHETIC_ZETARIS'].includes(value.mode)) throw new Error('Contrato o modo no admitido');
  if (!['PASS','EXECUTED_PARTIAL','INSUFFICIENT_DATA','BLOCKED','ERROR'].includes(value.status)) throw new Error('Estado desconocido');
  if (typeof value.run_id !== 'string' || typeof value.summary !== 'string' || !value.window?.start || !value.window?.end) throw new Error('Ejecución incompleta');
  if (!Array.isArray(value.coverage) || !Array.isArray(value.series) || !Array.isArray(value.findings) || !Array.isArray(value.tool_trace) || !Array.isArray(value.sponsor_proofs)) throw new Error('Colecciones ausentes');
  const zetaris = value.sponsor_proofs.find(proof => proof.sponsor === 'zetaris');
  if (value.sponsor_proofs.some(proof => proof.sponsor !== 'zetaris' && (proof.status !== 'NOT_CONNECTED' || proof.trace_id !== null))) throw new Error('Prueba de patrocinador inesperada');
  if (value.mode === 'SYNTHETIC_LOCAL_ONLY' && value.sponsor_proofs.some(proof => proof.status !== 'NOT_CONNECTED' || proof.trace_id !== null)) throw new Error('Prueba de patrocinador inesperada');
  if (value.mode === 'LIVE_SYNTHETIC_ZETARIS') {
    if (!zetaris) throw new Error('Falta prueba Zetaris');
    const query = value.tool_trace.find(step => step.tool === 'zetaris.synthetic_query' && step.trace_id === zetaris.trace_id);
    if (zetaris.status === 'VERIFIED' && (!zetaris.trace_id || !query || query.status !== 'PASS' || query.source_record_ids.length !== 156 || !query.query_id || !/^[0-9a-f]{64}$/.test(query.sql_sha256))) throw new Error('Prueba Zetaris no trazable');
    if (value.status === 'PASS') {
      if (zetaris.status !== 'VERIFIED') throw new Error('Prueba Zetaris no trazable');
    }
    if (value.reason_code === 'source_error' && (value.status !== 'ERROR' || value.coverage.length || value.series.length || value.comparison !== null || zetaris.status === 'VERIFIED')) throw new Error('Fallo Zetaris con datos no verificados');
  }
  for (const series of value.series) {
    if (!['energy','sleep_hours'].includes(series.variable) || !['score/10','hours'].includes(series.unit)) throw new Error('Variable o unidad inválida');
    if (!Array.isArray(series.points)) throw new Error('Serie inválida');
    for (const point of series.points) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(point.local_date)) throw new Error('Fecha inválida');
      if (point.value === null && point.source_record_id !== null) throw new Error('Hueco con fuente');
      if (point.value !== null && (!Number.isFinite(point.value) || !/^SYN-[A-Z0-9_-]+$/.test(point.source_record_id))) throw new Error('Valor sin fuente');
    }
  }
  if (value.findings.some(finding => !['observation','association','hypothesis','uncertainty','abstention'].includes(finding.kind))) throw new Error('Hallazgo desconocido');
  if (value.tool_trace.some(step => !['PASS','BLOCKED','ERROR'].includes(step.status)
    || (step.phase && !['PLAN','TOOLS','EVIDENCE','VERIFY','RESPOND','ABSTAIN'].includes(step.phase))
    || !Array.isArray(step.source_record_ids))) throw new Error('Traza desconocida');
  if (value.comparison) {
    const c = value.comparison;
    if (!Number.isFinite(c.baseline?.mean) || !Number.isFinite(c.comparison?.mean) || !Number.isFinite(c.difference)) throw new Error('Comparación inválida');
    if (!c.source_record_ids?.length) throw new Error('Comparación sin fuentes');
  }
  if (value.status !== 'PASS' && value.comparison !== null) throw new Error('Comparación en estado no válido');
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
