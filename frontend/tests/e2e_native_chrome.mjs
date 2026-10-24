/** Native Chrome to native localhost HTTP. Requires installed Chrome and Playwright. */
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'docs', 'evidence');
const modulePath = process.env.PHIS_PLAYWRIGHT_MODULE;
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : 'playwright');
const chromePath = process.env.PHIS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const base = process.env.PHIS_HTTP_BASE || 'http://127.0.0.1:4173';
const live = process.env.PHIS_EXPECT_MODE === 'LIVE_SYNTHETIC_ZETARIS';
const prefix = live ? 'integration-live' : 'integration-native';
await mkdir(output, { recursive: true });
const browser = await chromium.launch({ executablePath: chromePath, headless: true });
const errors = [];

async function submit(page) {
  await page.locator('#question-form button[type="submit"]').click();
  await page.waitForFunction(() => /RESPONSE RECEIVED|ABSTENTION|INSUFFICIENT COVERAGE|SOURCE OR TOOL UNAVAILABLE/.test(
    document.querySelector('#agent-phase')?.textContent || ''));
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  desktop.on('pageerror', error => errors.push(error.message));
  await desktop.goto(base);
  assert.equal(await desktop.locator('html').getAttribute('lang'), 'en');
  await submit(desktop);
  assert.equal(await desktop.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.match(await desktop.locator('.mode-pill').textContent(), live ? /LOCAL ZETARIS/ : /SYNTHETIC · LOCAL/);
  assert.match(await desktop.locator('#coverage-label').textContent(), /180 days/);
  assert.ok(await desktop.locator('.chart-point').count() > 50);
  const parent = await desktop.locator('#run-id').textContent();
  await desktop.screenshot({ path: path.join(output, `${prefix}-desktop.png`), fullPage: true });
  await desktop.getByRole('button', { name: 'Open evidence' }).click();
  const proofText = await desktop.locator('#dialog-content').textContent();
  assert.match(proofText, /meterless_engine: VERIFIED/);
  assert.match(proofText, live ? /zetaris: VERIFIED/ : /zetaris: NOT_CONNECTED/);
  assert.match(proofText, /meterless_runtime: NOT_CONNECTED/);
  assert.match(proofText, /nemotron: NOT_CONNECTED/);
  await desktop.screenshot({ path: path.join(output, `${prefix}-evidence.png`), fullPage: true });
  await desktop.getByRole('button', { name: 'Close evidence panel' }).click();
  await desktop.reload();
  await desktop.getByRole('button', { name: "What's next?" }).click();
  assert.match(await desktop.locator('#followup-context').textContent(), new RegExp(parent));
  await submit(desktop);
  assert.equal(await desktop.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.match(await desktop.locator('#trace-list').textContent(), /meterless.world_model.read/);
  await desktop.screenshot({ path: path.join(output, `${prefix}-followup.png`), fullPage: true });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true,
    hasTouch: true });
  mobile.on('pageerror', error => errors.push(error.message));
  await mobile.goto(base);
  await submit(mobile);
  assert.equal(await mobile.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobile.screenshot({ path: path.join(output, `${prefix}-mobile.png`), fullPage: true });

  if (!live) {
    await desktop.goto(base + '/?scenario=insufficient');
    await submit(desktop);
    assert.equal(await desktop.locator('#status-label').textContent(), 'INSUFFICIENT EVIDENCE');
    await desktop.screenshot({ path: path.join(output, `${prefix}-insufficient.png`), fullPage: true });
    await desktop.goto(base + '/?scenario=tool_error');
    await submit(desktop);
    assert.equal(await desktop.locator('#status-label').textContent(), 'TOOL UNAVAILABLE');
    assert.equal(await desktop.locator('.chart-point').count(), 0);
    await desktop.screenshot({ path: path.join(output, `${prefix}-tool-error.png`), fullPage: true });
  }
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ result: 'PASS', transport: 'native localhost HTTP', mode: live ? 'LIVE_SYNTHETIC_ZETARIS' : 'SYNTHETIC_LOCAL_ONLY',
    browser: 'installed Chrome', parentRunId: parent,
    screenshots: live ? ['desktop', 'evidence', 'followup', 'mobile'] : ['desktop', 'evidence', 'followup', 'mobile', 'insufficient', 'tool-error'] }));
} finally {
  await browser.close();
}
