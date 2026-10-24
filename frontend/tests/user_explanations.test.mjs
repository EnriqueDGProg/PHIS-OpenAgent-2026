import test from 'node:test';
import assert from 'node:assert/strict';
import { canContinueFrom, comparisonExplanation, findingExplanation,
  signalExplanation, TRACE_GROUPS } from '../presentation.mjs';

const run = {
  status: 'PASS', contract_version: 'investigation.v3', run_id: 'SYN-RUN-test',
  comparison: { variable: 'energy_central', unit: 'score', difference: 0.30,
    baseline: { mean: 5.8, observed: 26, start: '2026-08-27', end: '2026-09-23' },
    comparison: { mean: 6.1, observed: 27, start: '2026-09-24', end: '2026-10-21' } },
  sponsor_proofs: [{ sponsor: 'meterless_engine', status: 'VERIFIED' }],
  scientific_evidence: { signals: [
    { signal_id: 'sleep', exposure: 'sleep_hours', outcome: 'energy_central',
      effect: 0.56, lag_days: 0, classification: 'candidate_signal' },
    { signal_id: 'stress', exposure: 'stress_score', outcome: 'energy_central',
      effect: -0.517, lag_days: 1, classification: 'candidate_signal' },
  ] },
};

test('positive energy change stays positive, dated and descriptive', () => {
  const explanation = comparisonExplanation(run);
  assert.match(explanation.title, /increased/);
  assert.match(explanation.text, /5\.80\/10 earlier and 6\.10\/10 recently/);
  assert.match(explanation.text, /Using unrounded averages/);
  assert.match(explanation.text, /0\.30 points/);
  assert.doesNotMatch(explanation.text, /fatigue|tired|caused/i);
  assert.match(explanation.coverage, /26 of 28 days.*27 of 28 days/);
  assert.equal(explanation.earlier, '27 Aug 2026–23 Sept 2026');
  assert.equal(explanation.recent, '24 Sept 2026–21 Oct 2026');
  assert.match(comparisonExplanation({ ...run, comparison: { ...run.comparison,
    difference: -0.5, baseline: { ...run.comparison.baseline, mean: 6.1 },
    comparison: { ...run.comparison.comparison, mean: 5.6 } } }).text, /decreased by 0\.50/);
});

test('qualified findings use original typed signal and preserve temporal direction', () => {
  assert.match(signalExplanation(run.scientific_evidence.signals[0]).text,
    /higher recorded energy on the same day/);
  assert.match(signalExplanation(run.scientific_evidence.signals[1]).text,
    /lower recorded energy 1 day later/);
  const finding = { kind: 'candidate_contributor', evidence_signal_id: 'stress',
    title: 'Raw technical title', text: 'r=-0.517' };
  assert.match(findingExplanation(run, finding).text, /lower recorded energy/);
  assert.equal(findingExplanation({ ...run, scientific_evidence: null }, finding).text,
    'r=-0.517');
  assert.equal(signalExplanation({ ...run.scientific_evidence.signals[0], effect: Number.NaN }), null);
});

test('follow-up action requires a verified persisted scientific parent', () => {
  assert.equal(canContinueFrom(run), true);
  assert.equal(canContinueFrom({ ...run, status: 'BLOCKED' }), false);
  assert.equal(canContinueFrom({ ...run, scientific_evidence: null }), false);
  assert.equal(canContinueFrom({ ...run, sponsor_proofs: [{ sponsor: 'meterless_engine', status: 'NOT_CONNECTED' }] }), false);
  assert.equal(canContinueFrom({ ...run, contract_version: 'investigation.v1' }), false);
});

test('primary trace groups only recorded phases and retains the four-step order', () => {
  assert.deepEqual(TRACE_GROUPS.flatMap(group => group.phases),
    ['PLAN', 'TOOLS', 'EVIDENCE', 'VERIFY', 'RESPOND', 'ABSTAIN']);
});
