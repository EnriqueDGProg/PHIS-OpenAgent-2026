/** Installed Chrome against an isolated local synthetic API. No sponsor calls. */
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
const base = process.env.PHIS_HTTP_BASE || 'http://127.0.0.1:4187';
const errors = [];
await mkdir(output, { recursive: true });

async function investigate(page) {
  const response = page.waitForResponse(reply => reply.url().endsWith('/api/investigations') && reply.request().method() === 'POST');
  await page.locator('#ask-button').click();
  const payload = await (await response).json();
  await page.waitForFunction(() => !document.querySelector('#main')?.hasAttribute('aria-busy'));
  return payload;
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  desktop.on('pageerror', error => errors.push(error.message));
  await desktop.goto(base);
  assert.equal(await desktop.locator('#followup-actions').isVisible(), false);
  assert.equal(await desktop.locator('.entry-option').count(), 2);
  assert.match(await desktop.locator('#question-hint').textContent(), /fixed 180-day fictional record/);

  const energy = await investigate(desktop);
  assert.equal(energy.status, 'PASS');
  assert.equal(energy.family, 'energy');
  assert.equal(energy.mode, 'SYNTHETIC_LOCAL_ONLY');
  assert.equal(energy.scientific_evidence.hypothesis_count, 16);
  assert.equal(energy.sponsor_proofs.find(p => p.sponsor === 'zetaris').status, 'NOT_CONNECTED');
  assert.equal(energy.sponsor_proofs.find(p => p.sponsor === 'meterless_engine').status, 'VERIFIED');
  assert.match(await desktop.locator('#period-earlier-dates').textContent(), /27 Aug 2026.*23 Sept 2026/);
  assert.match(await desktop.locator('#period-recent-dates').textContent(), /24 Sept 2026.*21 Oct 2026/);
  assert.match(await desktop.locator('#findings').textContent(), /recorded energy|Recorded energy/i);
  assert.doesNotMatch(await desktop.locator('#findings').textContent(), /fatigue|more tired/i);
  assert.ok(Number(await desktop.locator('.chart-shade-earlier').getAttribute('x')) > 32);
  assert.match(await desktop.locator('.chart-footer').textContent(), /Earlier 28-day mean/);
  assert.equal(await desktop.locator('#trace-list > li').count(), 4);
  assert.equal(await desktop.locator('#followup-actions').isVisible(), true);
  assert.match(await desktop.locator('#chip-next').textContent(), /Continue with sleep using this run's memory/);
  await desktop.screenshot({ path: path.join(output, 'user-first-energy-desktop.png'), fullPage: true });
  await desktop.locator('#chip-sleep').click();
  assert.equal(await desktop.locator('#followup-banner').isVisible(), false);

  await desktop.locator('#evidence-button').click();
  assert.equal(await desktop.locator('#dialog-title').textContent(), 'Evidence & verification');
  await desktop.locator('#tab-signals').click();
  assert.match(await desktop.locator('#dialog-content').textContent(), /16 PRE-PLANNED SCIENTIFIC TESTS/);
  assert.equal(await desktop.locator('.signal-table tbody tr').count(), 16);
  await desktop.locator('#tab-trace').click();
  assert.match(await desktop.locator('#dialog-content').textContent(), /Meterless Engine event ID/);
  await desktop.screenshot({ path: path.join(output, 'user-first-evidence-desktop.png'), fullPage: true });
  await desktop.locator('#dialog-close').click();

  await desktop.locator('#chip-next').click();
  assert.match(await desktop.locator('#followup-banner').textContent(), new RegExp(energy.run_id));
  const followup = await investigate(desktop);
  assert.equal(followup.status, 'PASS');
  assert.equal(followup.family, 'sleep');
  assert.equal(followup.parent_run_id, energy.run_id);
  assert.match(await desktop.locator('#chip-next').textContent(), /Continue with energy using this run's memory/);
  assert.ok(followup.tool_trace.some(step => step.tool === 'meterless.world_model.read'));
  assert.match(await desktop.locator('#result-context').textContent(), /prior investigation saved in agent memory/);
  assert.match(await desktop.locator('#period-earlier').textContent(), /^\d+\.\d{2} h$/);
  assert.match(await desktop.locator('#period-recent').textContent(), /^\d+\.\d{2} h$/);
  await desktop.screenshot({ path: path.join(output, 'user-first-sleep-followup-desktop.png'), fullPage: true });

  await desktop.locator('#question').fill('Is there a clinical diagnosis here?');
  const clinical = await investigate(desktop);
  assert.equal(clinical.status, 'BLOCKED');
  assert.equal(clinical.comparison, null);
  assert.equal(await desktop.locator('.chart-point').count(), 0);
  assert.equal(await desktop.locator('#followup-actions').isVisible(), false);

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on('pageerror', error => errors.push(error.message));
  await mobile.goto(base);
  await mobile.locator('.entry-option').nth(0).click();
  const mobileEnergy = await investigate(mobile);
  assert.equal(mobileEnergy.status, 'PASS');
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, 'user-first-energy-mobile.png'), fullPage: true });
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ result: 'PASS', energy: energy.run_id, sleepFollowup: followup.run_id,
    clinical: clinical.reason_code, screenshots: 4 }));
} finally {
  await browser.close();
}
