import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchInvestigation, validateLongitudinalInvestigation } from '../client.mjs';

const hash = 'a'.repeat(64);
const id = i => `request-${i}`;
const query = i => `query-${i}`;
const live = () => ({
  contract_version: 'investigation.v3', synthetic: true,
  mode: 'LIVE_SYNTHETIC_ZETARIS', status: 'PASS', run_id: 'SYN-RUN-check',
  summary: 'Observed change', findings: [], series: [], coverage: [], comparison: null,
  tool_trace: [200, 200, 200, 200, 200, 80].map((row_count, i) => ({
    tool: 'zetaris.query_180d', phase: 'TOOLS', status: 'PASS', row_count,
    trace_id: id(i), query_id: query(i), sql_sha256: hash,
  })),
  sponsor_proofs: [
    { sponsor: 'zetaris', status: 'VERIFIED', trace_id: id(0) },
    { sponsor: 'meterless_engine', status: 'VERIFIED', trace_id: hash },
  ],
  scientific_evidence: {
    hypothesis_count: 16, plan_sha256: hash, record_digest_sha256: hash,
    signals: Array.from({ length: 16 }, () => ({ exposure: 'sleep_hours', classification: 'weak_candidate' })),
    source_query: { request_ids: [0,1,2,3,4,5].map(id), query_ids: [0,1,2,3,4,5].map(query) },
  },
});

test('default client route requests the 180-day v3 investigation', async () => {
  let posted;
  const result = await fetchInvestigation('Why energy?', { fetcher: async (_url, options) => {
    posted = JSON.parse(options.body);
    return { ok: true, json: async () => live() };
  } });
  assert.equal(posted.analysis_version, 'v3');
  assert.equal(posted.scenario, 'opportunity');
  assert.equal(result.status, 'PASS');
});

test('v3 rejects missing client-sent query IDs and broken six-page lineage', () => {
  const missing = live(); delete missing.scientific_evidence.source_query.query_ids;
  assert.throws(() => validateLongitudinalInvestigation(missing), /Zetaris readback/);
  const broken = live(); broken.tool_trace[5].row_count = 79;
  assert.throws(() => validateLongitudinalInvestigation(broken), /Zetaris readback/);
});

test('v4 keeps local planner separate from live sponsor proof', () => {
  const result = live(); result.contract_version = 'investigation.v4';
  result.planner_mode = 'LOCAL DETERMINISTIC MODE';
  result.sponsor_proofs.push({ sponsor: 'meterless_runtime', status: 'NOT_CONNECTED', trace_id: null });
  assert.equal(validateLongitudinalInvestigation(result).planner_mode, 'LOCAL DETERMINISTIC MODE');
  result.sponsor_proofs[0].status = 'NOT_CONNECTED';
  assert.throws(() => validateLongitudinalInvestigation(result), /source provenance/);
});
