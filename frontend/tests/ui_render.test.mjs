/**
 * UI render unit tests — pure DOM-free logic only.
 * Tests helper functions that are exported for testability.
 *
 * These do NOT run Playwright or open a browser.
 * They verify the contract-level helpers used by app.mjs.
 */
import test from 'node:test';
import assert from 'node:assert/strict';

// ─── Inline copies of pure helpers for isolated testing ───────────────────────
// (Matches the logic in app.mjs without importing it, since app.mjs is browser-only)

function windowDays(run) {
  if (run?.coverage?.length) return run.coverage[0].eligible ?? 84;
  if (run?.window_days) return run.window_days;
  if (run?.window?.start && run?.window?.end) {
    const ms = new Date(run.window.end) - new Date(run.window.start);
    return Math.round(ms / 86_400_000) + 1;
  }
  return 84;
}

function isBenchmarkRun(run) {
  return (
    run?.scientific_evidence?.engine === 'authentic-local-PHIS-Discovery-v1.1'
    && windowDays(run) >= 150
  );
}

function trajectoryClass(difference) {
  return difference < -0.05 ? 'down' : difference > 0.05 ? 'up' : 'flat';
}

function trajectoryArrow(difference) {
  return difference < -0.05 ? '▼' : difference > 0.05 ? '▲' : '→';
}

function kindToLabel(kind) {
  const map = {
    observation:            'OBSERVATION',
    association:            'ASSOCIATION',
    hypothesis:             'HYPOTHESIS',
    candidate_contributor:  'QUALIFIED SIGNAL',
    unsupported_hypothesis: 'NO EVIDENCE',
    uncertainty:            'CONFOUNDING LIMIT',
    abstention:             'ABSTAINED',
  };
  return map[kind] ?? kind.toUpperCase();
}

function diffValueClass(difference) {
  return difference < -0.05 ? 'negative' : difference > 0.05 ? 'positive' : 'neutral';
}

// ─── Tests ────────────────────────────────────────────────────────────────────

test('windowDays returns 84 for standard coverage', () => {
  const run = { coverage: [{ variable: 'energy', observed: 68, eligible: 84 }] };
  assert.equal(windowDays(run), 84);
});

test('windowDays returns 180 for PR #21 benchmark coverage', () => {
  const run = { coverage: [{ variable: 'energy', observed: 161, eligible: 180 }] };
  assert.equal(windowDays(run), 180);
});

test('windowDays falls back to window span', () => {
  const run = { window: { start: '2026-04-25', end: '2026-10-21' } };
  assert.equal(windowDays(run), 180);
});

test('windowDays defaults to 84 when no coverage or window', () => {
  assert.equal(windowDays({}), 84);
  assert.equal(windowDays(null), 84);
});

test('isBenchmarkRun false for 84-day window with Discovery engine', () => {
  const run = {
    scientific_evidence: { engine: 'authentic-local-PHIS-Discovery-v1.1' },
    coverage: [{ eligible: 84 }],
  };
  assert.equal(isBenchmarkRun(run), false);
});

test('isBenchmarkRun true for 180-day window with Discovery engine', () => {
  const run = {
    scientific_evidence: { engine: 'authentic-local-PHIS-Discovery-v1.1' },
    coverage: [{ eligible: 180 }],
  };
  assert.equal(isBenchmarkRun(run), true);
});

test('isBenchmarkRun false when engine is not Discovery', () => {
  const run = {
    scientific_evidence: { engine: 'other-engine' },
    coverage: [{ eligible: 180 }],
  };
  assert.equal(isBenchmarkRun(run), false);
});

test('isBenchmarkRun false when no scientific_evidence', () => {
  const run = { coverage: [{ eligible: 180 }] };
  assert.equal(isBenchmarkRun(run), false);
});

test('trajectoryClass correctly categorises direction', () => {
  assert.equal(trajectoryClass(-0.74), 'down');
  assert.equal(trajectoryClass( 0.30), 'up');
  assert.equal(trajectoryClass( 0.00), 'flat');
  assert.equal(trajectoryClass(-0.03), 'flat');   // within ±0.05 tolerance
});

test('trajectoryArrow matches direction', () => {
  assert.equal(trajectoryArrow(-0.74), '▼');
  assert.equal(trajectoryArrow( 0.30), '▲');
  assert.equal(trajectoryArrow( 0.00), '→');
});

test('kindToLabel maps all supported kinds', () => {
  assert.equal(kindToLabel('observation'),            'OBSERVATION');
  assert.equal(kindToLabel('association'),            'ASSOCIATION');
  assert.equal(kindToLabel('hypothesis'),             'HYPOTHESIS');
  assert.equal(kindToLabel('candidate_contributor'),  'QUALIFIED SIGNAL');
  assert.equal(kindToLabel('unsupported_hypothesis'), 'NO EVIDENCE');
  assert.equal(kindToLabel('uncertainty'),            'CONFOUNDING LIMIT');
  assert.equal(kindToLabel('abstention'),             'ABSTAINED');
});

test('kindToLabel uppercases unknown kinds', () => {
  assert.equal(kindToLabel('some_new_kind'), 'SOME_NEW_KIND');
});

test('diffValueClass categorises correctly', () => {
  assert.equal(diffValueClass(-0.74), 'negative');
  assert.equal(diffValueClass( 0.30), 'positive');
  assert.equal(diffValueClass( 0.01), 'neutral');
});

test('windowDays uses window_days field if present', () => {
  const run = { window_days: 180, coverage: [] };
  assert.equal(windowDays(run), 180);
});

test('windowDays prefers coverage.eligible over window span', () => {
  // Coverage is the most reliable source
  const run = {
    coverage: [{ eligible: 84 }],
    window: { start: '2026-04-25', end: '2026-10-21' }, // spans ~180d
  };
  assert.equal(windowDays(run), 84);
});
