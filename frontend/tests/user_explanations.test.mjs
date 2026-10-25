import test from 'node:test';
import assert from 'node:assert/strict';
import { canContinueFrom, comparisonExplanation, displayChange, findingExplanation,
  longitudinalPresentation,
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
    comparison: { ...run.comparison.comparison, mean: 5.6 } } }).text, /−0\.50 points.*energy decreased/);
});

test('near-zero sleep is broadly stable under the documented display-only band', () => {
  const sleep = { ...run, comparison: { ...run.comparison, variable: 'sleep_hours',
    unit: 'hours', difference: -0.01,
    baseline: { ...run.comparison.baseline, mean: 7.01 },
    comparison: { ...run.comparison.comparison, mean: 7.00 } } };
  assert.equal(displayChange(-0.01), 'flat');
  assert.equal(displayChange(-0.05), 'flat');
  assert.equal(displayChange(-0.051), 'down');
  assert.match(comparisonExplanation(sleep).title, /broadly stable/i);
  assert.match(comparisonExplanation(sleep).text, /−0\.01 hours.*±0\.05 display band/);
  assert.doesNotMatch(comparisonExplanation(sleep).text, /sleep decreased/);
});

test('same-day supported association stays distinct from unstable next-day test', () => {
  const sameDay = { signal_id: 'same-day', exposure: 'sleep_hours', outcome: 'energy_central',
    lag_days: 0, effect: 0.5, classification: 'candidate_signal' };
  const nextDay = { ...sameDay, signal_id: 'next-day', lag_days: 1,
    classification: 'unstable_candidate', temporal_state: 'unstable' };
  const pairedRun = { ...run, scientific_evidence: { signals: [sameDay, nextDay] } };
  const finding = { kind: 'association', evidence_signal_id: 'next-day', text: 'Technical result' };
  assert.match(signalExplanation(sameDay).title, /same day.*Supported association/i);
  assert.match(signalExplanation(nextDay).title, /next day.*Exploratory only/i);
  assert.match(findingExplanation(pairedRun, finding).text, /different test from the supported same-day/i);
});

test('whole-history summary formats only six returned missing-aware 30-day means', () => {
  const windows = Array.from({ length: 6 }, (_, index) => ({
    start: new Date(Date.UTC(2026, 3, 25 + index * 30)).toISOString().slice(0, 10),
    end: new Date(Date.UTC(2026, 3, 54 + index * 30)).toISOString().slice(0, 10),
    observed: 28, eligible: 30, mean: 5.1 + index * 0.1,
  }));
  const longitudinal = { ...run, window: { start: windows[0].start, end: windows[5].end },
    series: [{ variable: 'energy_central', unit: 'score/10' }],
    coverage: [{ variable: 'energy_central', observed: 168, eligible: 180 }],
    longitudinal: { variable: 'energy_central', method: 'arithmetic_mean_observed_days',
      inference: 'descriptive_only', windows, first_to_last_difference: 0.5 } };
  const view = longitudinalPresentation(longitudinal);
  assert.equal(view.windows.length, 6);
  assert.equal(view.coverage, '168 of 180 days recorded');
  assert.match(view.comparison, /\+0\.50\/10.*Descriptive difference only/);
  assert.equal(longitudinalPresentation({ ...longitudinal,
    longitudinal: { ...longitudinal.longitudinal, windows: windows.slice(1) } }), null);
  assert.equal(longitudinalPresentation({ ...longitudinal,
    coverage: [{ variable: 'energy_central', observed: 180, eligible: 180 }] }), null);
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
