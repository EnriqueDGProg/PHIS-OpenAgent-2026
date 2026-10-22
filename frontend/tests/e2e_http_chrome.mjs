/** Native HTTP Chrome check. Requires an existing Chrome and Playwright installation. */
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdir, mkdtemp, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'docs', 'evidence');
const modulePath = process.env.PHIS_PLAYWRIGHT_MODULE;
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : 'playwright');
const chromePath = process.env.PHIS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const liveSuccess = process.argv.includes('--live');
const port = Number(process.env.PHIS_E2E_PORT || 4187);
const url = `http://127.0.0.1:${port}`;
let child, browser;

async function start(mode, state, clearCredentials = false) {
  const env = { ...process.env, PYTHONPATH: 'src', PYTHONIOENCODING: 'utf-8',
    PORT: String(port), PHIS_DATA_MODE: mode, PHIS_SYNTHETIC_STATE_FILE: state };
  if (clearCredentials) for (const key of ['ZETARIS_REST_URL','ZETARIS_ORG_ID','ZETARIS_API_KEY']) delete env[key];
  child = spawn(process.env.PHIS_PYTHON || 'python', ['-m', 'phis_open_agent.api'],
    { cwd: root, env, windowsHide: true, stdio: 'ignore' });
  for (let attempt = 0; attempt < 50; attempt++) {
    if (child.exitCode !== null) throw new Error('PHIS API exited before it became ready');
    try {
      const response = await fetch(url + '/api/health');
      if (response.ok) {
        assert.equal((await response.json()).mode, mode);
        return;
      }
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('PHIS API did not become ready over native HTTP');
}

async function stop() {
  if (!child) return;
  const process = child;
  child = null;
  process.kill();
  await new Promise(resolve => process.once('exit', resolve));
}

async function submit(page) {
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/investigations'));
  await page.getByRole('button', { name: /investigate records/i }).click();
  const response = await responsePromise;
  assert.equal(response.status(), 200);
  return response.json();
}

await mkdir(output, { recursive: true });
await mkdir(path.join(root, '.local-state'), { recursive: true });
const temp = await mkdtemp(path.join(root, '.local-state', 'http-chrome-'));
const state = path.join(temp, 'events.jsonl');
try {
  browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await desktop.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));

  await start('SYNTHETIC_LOCAL_ONLY', state);
  await page.goto(url);
  const parent = await submit(page);
  assert.equal(parent.status, 'PASS');
  assert.equal(parent.series[0].points.length, 84);
  assert.equal(parent.sponsor_proofs.find(proof => proof.sponsor === 'zetaris').status, 'NOT_CONNECTED');
  assert.equal(await page.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  await page.screenshot({ path: path.join(output, 'consolidated-http-desktop.png'), fullPage: true });
  await stop();

  await start('SYNTHETIC_LOCAL_ONLY', state);
  await page.reload();
  await page.getByRole('button', { name: 'Explore sleep' }).click();
  const followup = await submit(page);
  assert.equal(followup.status, 'PASS');
  assert.equal(followup.parent_run_id, parent.run_id);
  assert.equal(followup.series[0].variable, 'sleep_hours');
  assert.equal(followup.tool_trace.some(step => step.parent_event_id), true);
  await page.screenshot({ path: path.join(output, 'consolidated-http-followup.png'), fullPage: true });

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  const mobilePage = await mobile.newPage();
  mobilePage.on('pageerror', error => pageErrors.push(error.message));
  await mobilePage.goto(url);
  assert.equal((await submit(mobilePage)).status, 'PASS');
  assert.equal(await mobilePage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
  await mobilePage.screenshot({ path: path.join(output, 'consolidated-http-mobile.png'), fullPage: true });
  await stop();

  await start('LIVE_SYNTHETIC_ZETARIS', state, true);
  await page.goto(url);
  const unavailable = await submit(page);
  assert.equal(unavailable.status, 'ERROR');
  assert.equal(unavailable.reason_code, 'source_error');
  assert.equal(unavailable.series.length, 0);
  assert.equal(unavailable.coverage.length, 0);
  assert.equal(unavailable.comparison, null);
  assert.equal(unavailable.sponsor_proofs.find(proof => proof.sponsor === 'zetaris').status, 'NOT_CONNECTED');
  assert.equal(await page.locator('#status-label').textContent(), 'ZETARIS SOURCE UNAVAILABLE');
  assert.match(await page.locator('#result-context').textContent(), /no records published/);
  assert.doesNotMatch(await page.locator('#result-context').textContent(), /rows queried/);
  await page.screenshot({ path: path.join(output, 'consolidated-http-source-error.png'), fullPage: true });
  await stop();

  if (liveSuccess) {
    await start('LIVE_SYNTHETIC_ZETARIS', state);
    await page.goto(url);
    const verified = await submit(page);
    assert.equal(verified.status, 'PASS');
    assert.equal(verified.sponsor_proofs.find(proof => proof.sponsor === 'zetaris').status, 'VERIFIED');
    const query = verified.tool_trace.find(step => step.tool === 'zetaris.synthetic_query');
    assert.equal(query.trace_id, verified.sponsor_proofs.find(proof => proof.sponsor === 'zetaris').trace_id);
    assert.equal(query.source_record_ids.length, 156);
    await page.screenshot({ path: path.join(output, 'consolidated-http-zetaris-verified.png'), fullPage: true });
    await stop();
  }
  assert.deepEqual(pageErrors, []);
  console.log('PASS Chrome native HTTP desktop/mobile, persisted follow-up, live-source failure without fallback' +
    (liveSuccess ? ', and verified Zetaris query' : ''));
} finally {
  await stop();
  await browser?.close();
  await rm(temp, { recursive: true, force: true });
}
