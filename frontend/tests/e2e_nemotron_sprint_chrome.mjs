/** Installed Chrome, real localhost HTTP and real PHIS Discovery.
 * v4 server uses an explicitly injected SIMULATED model transport.
 */
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'docs', 'evidence');
const modulePath = process.env.PHIS_PLAYWRIGHT_MODULE;
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : 'playwright');
const browser = await chromium.launch({
  executablePath: process.env.PHIS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
});
const local = process.env.PHIS_V3_BASE || 'http://127.0.0.1:4195/';
const simulated = process.env.PHIS_V4_SIM_BASE || 'http://127.0.0.1:4196/?analysis=v4';
const errors = [];
await mkdir(output, { recursive: true });

async function investigate(page, family) {
  await page.locator('.entry-option').nth(family === 'energy' ? 0 : 1).click();
  const pending = page.waitForResponse(reply =>
    reply.url().endsWith('/api/investigations') && reply.request().method() === 'POST');
  await page.locator('#ask-button').click();
  const result = await (await pending).json();
  await page.waitForFunction(() => !document.querySelector('#main')?.hasAttribute('aria-busy'));
  assert.equal(result.status, 'PASS');
  assert.equal(result.scientific_evidence.family, family);
  assert.equal(result.longitudinal.windows.length, 6);
  assert.equal(result.coverage.find(item => item.variable ===
    (family === 'energy' ? 'energy_central' : 'sleep_hours')).eligible, 180);
  assert.equal(await page.locator('#recent-changes').getAttribute('open'), null);
  assert.equal(await page.locator('#longitudinal-windows').locator('.longitudinal-window').count(), 6);
  return result;
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  desktop.on('pageerror', error => errors.push(error.message));
  await desktop.goto(local);
  const localEnergy = await investigate(desktop, 'energy');
  assert.equal(localEnergy.contract_version, 'investigation.v3');
  assert.equal(await desktop.locator('#model-review').isVisible(), false);
  await desktop.screenshot({ path: path.join(output, 'nemotron-sprint-v3-energy-desktop.png'), fullPage: true });

  await desktop.goto(simulated);
  const modelEnergy = await investigate(desktop, 'energy');
  assert.equal(modelEnergy.contract_version, 'investigation.v4');
  assert.deepEqual(modelEnergy.scientific_evidence, localEnergy.scientific_evidence);
  assert.deepEqual(modelEnergy.longitudinal, localEnergy.longitudinal);
  assert.equal(modelEnergy.planner_mode, 'SIMULATED');
  assert.equal(modelEnergy.review.decision, 'accept');
  assert.equal(modelEnergy.sponsor_proofs.find(p => p.sponsor === 'nemotron').status, 'NOT_CONNECTED');
  await desktop.locator('#model-review-details summary').click();
  assert.match(await desktop.locator('#model-review').textContent(), /Cited PHIS signal IDs/);
  assert.equal(await desktop.locator('#model-review').isVisible(), true);
  assert.equal(await desktop.locator('#recent-changes').getAttribute('open'), null);
  await desktop.screenshot({ path: path.join(output, 'nemotron-sprint-v4-energy-desktop.png'), fullPage: true });
  const firstFinding = modelEnergy.findings.find(item => item.kind === 'candidate_contributor');
  await desktop.locator('#findings .finding-card').first().getByRole('button', { name: /Inspect records/ }).click();
  assert.equal(await desktop.locator('.source-record-table tbody tr').count(), firstFinding.source_record_ids.length);
  assert.equal(await desktop.locator('.source-record-table tbody tr').first().getAttribute('data-source-id'),
    firstFinding.source_record_ids[0]);
  await desktop.locator('#dialog-close').click();
  await desktop.locator('#findings .finding-card').first().getByRole('button', { name: /View scientific test/ }).click();
  assert.match(await desktop.locator('#dialog-content').textContent(), /16 PRE-PLANNED SCIENTIFIC TESTS/);
  await desktop.screenshot({ path: path.join(output, 'nemotron-sprint-v4-evidence-desktop.png'), fullPage: true });
  await desktop.locator('#dialog-close').click();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on('pageerror', error => errors.push(error.message));
  await mobile.goto(local);
  const localSleep = await investigate(mobile, 'sleep');
  assert.equal(localSleep.contract_version, 'investigation.v3');
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, 'nemotron-sprint-v3-sleep-mobile.png'), fullPage: true });
  await mobile.goto(simulated);
  const modelSleep = await investigate(mobile, 'sleep');
  assert.equal(modelSleep.contract_version, 'investigation.v4');
  assert.deepEqual(modelSleep.scientific_evidence, localSleep.scientific_evidence);
  assert.deepEqual(modelSleep.longitudinal, localSleep.longitudinal);
  assert.equal(modelSleep.review.decision, 'accept');
  assert.equal(modelSleep.sponsor_proofs.find(p => p.sponsor === 'nemotron').status, 'NOT_CONNECTED');
  await mobile.locator('#model-review-details summary').click();
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, 'nemotron-sprint-v4-sleep-mobile.png'), fullPage: true });

  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ result: 'PASS', chrome: 'installed', v3: ['energy', 'sleep'],
    v4: ['energy', 'sleep'], v4Inference: 'SIMULATED', screenshots: 5 }));
} finally {
  await browser.close();
}
