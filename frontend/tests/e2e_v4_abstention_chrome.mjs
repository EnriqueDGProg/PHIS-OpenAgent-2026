/** Installed Chrome against a SIMULATED contradictory critique, never sponsor proof. */
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
await mkdir(output, { recursive: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(process.env.PHIS_V4_INVALID_BASE || 'http://127.0.0.1:4198/?analysis=v4');
  const pending = page.waitForResponse(reply =>
    reply.url().endsWith('/api/investigations') && reply.request().method() === 'POST');
  await page.locator('#ask-button').click();
  const run = await (await pending).json();
  await page.waitForFunction(() => !document.querySelector('#main')?.hasAttribute('aria-busy'));
  assert.equal(run.status, 'BLOCKED');
  assert.equal(run.reason_code, 'invalid_critique');
  assert.equal(run.scientific_evidence, null);
  assert.equal(run.scientific_audit.scientific_evidence.hypothesis_count, 16);
  assert.equal(run.review, null);
  assert.equal(run.sponsor_proofs.find(p => p.sponsor === 'nemotron').status, 'NOT_CONNECTED');
  assert.equal(await page.locator('#longitudinal-summary').isVisible(), true);
  assert.equal(await page.locator('#longitudinal-windows .longitudinal-window').count(), 6);
  assert.equal(await page.locator('.chart-point').count(), 170);
  assert.match(await page.locator('#findings-title').textContent(), /Model review failed/);
  assert.match(await page.locator('#result-context').textContent(), /model review failed validation/);
  assert.equal(await page.locator('#recent-changes').getAttribute('open'), null);
  await page.locator('#model-review-details summary').click();
  assert.doesNotMatch(await page.locator('#model-review').textContent(), /merely exploratory/);
  await page.screenshot({ path: path.join(output, 'nemotron-sprint-v4-invalid-abstention-desktop.png'),
    fullPage: true });
  await page.locator('#evidence-button').click();
  await page.locator('#tab-signals').click();
  assert.equal(await page.locator('.signal-table tbody tr').count(), 16);
  assert.match(await page.locator('#dialog-content').textContent(), /retained technical audit/);
  console.log(JSON.stringify({ result: 'PASS', status: run.status,
    reason: run.reason_code, model: 'SIMULATED', observed: 170, auditSignals: 16 }));
} finally {
  await browser.close();
}
