import test from 'node:test';
import assert from 'node:assert/strict';
import { records } from '../fixture.mjs';
import { getVariableCoverage, getLongitudinalTrend, comparePeriods, investigate } from '../tools.mjs';

test('hero observation is calculated from the synthetic source and linked to record IDs', async () => {
  const run = await investigate('¿Por qué ha cambiado mi energía últimamente?');
  assert.equal(run.status,'success');
  assert.deepEqual(run.coverage,getVariableCoverage(records));
  assert.deepEqual(run.periods,comparePeriods(records));
  assert.equal(run.findings[0].kind,'observation');
  assert.equal(run.findings[0].sourceIds.length,run.coverage.energy);
  assert.match(run.summary,/causa sigue sin establecerse/);
  assert.equal(run.trace.find(step => step.id === 'discovery').status,'blocked');
});

test('missing observations remain gaps rather than imputed zeros', () => {
  const trend = getLongitudinalTrend();
  assert.equal(trend.length,42);
  assert.equal(trend[7].energy,null);
  assert.equal(trend[24].energy,null);
  assert.equal(getVariableCoverage().energy,36);
});

test('sparse coverage abstains without a period comparison', async () => {
  const sparse = records.map((row,index) => ({...row,energy:index < 8 ? row.energy : null}));
  const run = await investigate('¿Qué pasó con mi energía?',{data:sparse});
  assert.equal(run.status,'insufficient');
  assert.equal(run.periods,undefined);
  assert.equal(run.findings[0].kind,'abstention');
});

test('clinical request abstains before reading trend', async () => {
  const run = await investigate('¿Debería cambiar mi medicación por la energía?');
  assert.equal(run.status,'unsupported');
  assert.equal(run.trend.length,0);
  assert.equal(run.trace.at(-1).status,'blocked');
});

test('tool error exposes no numeric finding and can be retried', async () => {
  const failed = await investigate('¿Cómo ha cambiado mi energía?',{failTool:true});
  assert.equal(failed.status,'error');
  assert.equal(failed.trend.length,0);
  assert.equal(failed.findings[0].sourceIds.length,0);
  const retried = await investigate('¿Cómo ha cambiado mi energía?');
  assert.equal(retried.status,'success');
});
