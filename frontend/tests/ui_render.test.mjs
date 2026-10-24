import test from 'node:test';
import assert from 'node:assert/strict';
import { isOfflineScientificRun, sourceLabel, windowDays,
         trajectoryArrow, trajectoryClass } from '../presentation.mjs';

const base = {
  mode: 'SYNTHETIC_LOCAL_ONLY',
  window: { start: '2026-04-25', end: '2026-10-21' },
  scientific_evidence: { engine: 'authentic-local-PHIS-Discovery-v1.1' },
  sponsor_proofs: [{ sponsor: 'zetaris', status: 'NOT_CONNECTED' }],
};

test('offline label depends on sponsor proof and mode, never duration', () => {
  assert.equal(windowDays(base), 180);
  assert.equal(isOfflineScientificRun(base), true);
  assert.equal(sourceLabel(base), 'SYNTHETIC · LOCAL');
  const live = { ...base, mode: 'LIVE_SYNTHETIC_ZETARIS',
    sponsor_proofs: [{ sponsor: 'zetaris', status: 'VERIFIED' }] };
  assert.equal(windowDays(live), 180);
  assert.equal(isOfflineScientificRun(live), false);
  assert.equal(sourceLabel(live), 'SYNTHETIC · LIVE ZETARIS');
  assert.equal(sourceLabel({ ...live, sponsor_proofs: [{ sponsor: 'zetaris', status: 'FAILED' }] }),
    'SYNTHETIC · ZETARIS FAILED');
});

test('trajectory arrows and classes retain observed direction', () => {
  assert.equal(trajectoryClass(-0.74), 'down');
  assert.equal(trajectoryArrow(-0.74), '▼');
  assert.equal(trajectoryClass(0.30), 'up');
  assert.equal(trajectoryArrow(0), '→');
});
