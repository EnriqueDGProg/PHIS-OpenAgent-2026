/** Real isolated Chrome checks against the local synthetic-only API. */
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'docs', 'evidence');
const { chromium } = await import(pathToFileURL(process.env.PHIS_PLAYWRIGHT_MODULE).href);
const browser = await chromium.launch({
  executablePath: process.env.PHIS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
});
const base = process.env.PHIS_HTTP_BASE || 'http://127.0.0.1:4192';
const errors = [];
const timing = [];
await mkdir(output, { recursive: true });

async function investigate(page) {
  const started = performance.now();
  const response = page.waitForResponse(reply => reply.url().endsWith('/api/investigations') && reply.request().method() === 'POST');
  await page.locator('#ask-button').click();
  const payload = await (await response).json();
  await page.waitForFunction(() => !document.querySelector('#main')?.hasAttribute('aria-busy'));
  timing.push(Math.round(performance.now() - started));
  return payload;
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  desktop.on('pageerror', error => errors.push(error.message));
  await desktop.goto(base);
  const energy = await investigate(desktop);
  assert.equal(energy.status, 'PASS');
  assert.equal(energy.scientific_evidence.hypothesis_count, 16);
  assert.equal(await desktop.locator('#global-study-limit').isVisible(), true);
  assert.equal(await desktop.locator('.finding-card.uncertainty').count(), 0);
  assert.equal(energy.sponsor_proofs.find(proof => proof.sponsor === 'zetaris').status, 'NOT_CONNECTED');
  assert.equal(energy.sponsor_proofs.find(proof => proof.sponsor === 'meterless_engine').status, 'VERIFIED');
  assert.match(await desktop.locator('#question-hint').textContent(), /fixed 180-day fictional record/);
  await desktop.screenshot({ path: path.join(output, 'issue44-energy-desktop.png'), fullPage: true });

  const signalFinding = energy.findings.find(finding => finding.evidence_signal_id && finding.source_record_ids?.length);
  assert.ok(signalFinding);
  const signal = energy.scientific_evidence.signals.find(item => item.signal_id === signalFinding.evidence_signal_id);
  const cardByIndex = desktop.locator('.finding-card').nth(energy.findings.filter(f => f.kind !== 'uncertainty').findIndex(f => f.finding_id === signalFinding.finding_id));
  await cardByIndex.getByRole('button', { name: /Inspect records/ }).click();
  assert.equal(await desktop.locator('#tab-finding').getAttribute('aria-selected'), 'true');
  assert.ok(await desktop.locator(`.source-record-table tr[data-source-id="${signalFinding.source_record_ids[0]}"]`).count());
  await desktop.locator('#tab-signals').click();
  assert.match(await desktop.locator('#dialog-content').textContent(), new RegExp(signal.signal_id));
  assert.equal(await desktop.locator(`.signal-table tr[data-signal-id="${signal.signal_id}"]`).count(), 1);
  await desktop.locator('#tab-finding').click();
  assert.ok(await desktop.locator(`.source-record-table tr[data-source-id="${signalFinding.source_record_ids[0]}"]`).count());
  await desktop.screenshot({ path: path.join(output, 'issue44-evidence-desktop.png'), fullPage: true });
  await desktop.locator('#dialog-close').click();
  await cardByIndex.getByRole('button', { name: /View scientific test/ }).click();
  assert.equal(await desktop.locator('#tab-signals').getAttribute('aria-selected'), 'true');
  assert.match(await desktop.locator('#dialog-content').textContent(), new RegExp(signal.signal_id));
  assert.equal(await desktop.locator('.signal-table tbody tr').count(), 16);
  await desktop.locator('#tab-sponsors').click();
  assert.equal(await desktop.locator('.sponsor-block.sponsor-proof-verified').count(), 1);
  assert.ok(await desktop.locator('.sponsor-block.sponsor-proof-disconnected').count() >= 1);
  await desktop.locator('#dialog-close').click();

  const chartPoint = desktop.locator('.chart-point[data-source-id]').first();
  const chartSource = await chartPoint.getAttribute('data-source-id');
  await chartPoint.click();
  assert.match(await desktop.locator('#dialog-content').textContent(), new RegExp(chartSource));
  assert.match(await desktop.locator('#dialog-content').textContent(), /SELECTED CHART RECORD/);
  await desktop.locator('#dialog-close').click();

  await desktop.locator('#chip-sleep').click();
  assert.equal(await desktop.locator('#followup-banner').isVisible(), false);

  await desktop.locator('#chip-next').click();
  const sleep = await investigate(desktop);
  assert.equal(sleep.status, 'PASS');
  assert.equal(sleep.parent_run_id, energy.run_id);
  assert.ok(sleep.tool_trace.some(step => step.tool === 'meterless.world_model.read'));
  assert.match(await desktop.locator('#trajectory-delta').textContent(), /Broadly stable/);
  assert.match(await desktop.locator('#period-diff-value').textContent(), /broadly stable/i);
  await desktop.screenshot({ path: path.join(output, 'issue44-sleep-followup-desktop.png'), fullPage: true });
  await desktop.locator('#question').fill('Is there a clinical diagnosis here?');
  const clinical = await investigate(desktop);
  assert.equal(clinical.status, 'BLOCKED');
  assert.equal(clinical.comparison, null);

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on('pageerror', error => errors.push(error.message));
  await mobile.goto(base);
  const mobileEnergy = await investigate(mobile);
  assert.equal(mobileEnergy.status, 'PASS');
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, 'issue44-energy-mobile.png'), fullPage: true });
  await mobile.locator('.finding-card').nth(1).getByRole('button', { name: /Inspect records/ }).click();
  assert.equal(await mobile.locator('#evidence-dialog').isVisible(), true);
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, 'issue44-evidence-mobile.png'), fullPage: true });
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ result: 'PASS', timings_ms: timing, energy: energy.run_id,
    sleep_followup: sleep.run_id, clinical: clinical.reason_code, screenshots: 5 }));
} finally {
  await browser.close();
}
