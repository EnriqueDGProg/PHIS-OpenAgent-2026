/** Real local Chrome check. Uses an existing Playwright installation; installs nothing. */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'docs', 'evidence');
const modulePath = process.env.PHIS_PLAYWRIGHT_MODULE;
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : 'playwright');
const chromePath = process.env.PHIS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const url = 'http://phis.test/';
let browser;
const bridgePids = [];

async function routeRequest(route) {
  const request = route.request();
  const pathname = new URL(request.url()).pathname;
  if (pathname === '/api/investigations' && request.method() === 'POST') {
    const child = spawnSync(process.env.PHIS_PYTHON || 'python', ['tests/api_bridge_cli.py'], {
      cwd: root, input: request.postData(), encoding: 'utf8', windowsHide: true,
      env: { ...process.env, PYTHONPATH: 'src', PYTHONIOENCODING: 'utf-8', PHIS_DATA_MODE: 'SYNTHETIC_LOCAL_ONLY',
        PHIS_SYNTHETIC_STATE_FILE: path.join(root, '.local-state', 'e2e-events.jsonl') },
    });
    if (child.status !== 0) throw new Error(`Python bridge failed: ${child.stderr}`);
    bridgePids.push(child.pid);
    const response = JSON.parse(child.stdout);
    await route.fulfill({ status: response.code, contentType: 'application/json; charset=utf-8',
      body: JSON.stringify(response.body) });
    return;
  }
  const files = { '/': ['index.html', 'text/html; charset=utf-8'],
    '/styles.css': ['styles.css', 'text/css; charset=utf-8'],
    '/app.mjs': ['app.mjs', 'text/javascript; charset=utf-8'],
    '/client.mjs': ['client.mjs', 'text/javascript; charset=utf-8'] };
  if (request.method() === 'GET' && files[pathname]) {
    const [filename, contentType] = files[pathname];
    await route.fulfill({ status: 200, contentType,
      body: await readFile(path.join(root, 'frontend', filename)) });
    return;
  }
  await route.abort();
}

async function submit(page) {
  await page.locator('#question-form button[type="submit"]').click();
  await page.waitForFunction(() => /RESPONSE RECEIVED|ABSTAINED|INSUFFICIENT COVERAGE|LOCAL FAILURE/.test(
    document.querySelector('#agent-phase')?.textContent || ''));
  const visibleText = await page.locator('body').innerText();
  assert.doesNotMatch(visibleText, /[¿¡áéíóúñÁÉÍÓÚÑ]|\b(?:días|registros|herramientas|evidencia|comparación|ejecución|seguimiento|abstención|fuentes|pregunta|resultado)\b/i);
}

try {
  await mkdir(output, { recursive: true });
  browser = await chromium.launch({ executablePath: chromePath, headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  await context.route('**/*', routeRequest);
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(url);
  assert.equal(await page.locator('html').getAttribute('lang'), 'en');
  assert.equal(await page.getByRole('heading', { level: 1 }).count(), 1);
  assert.equal(await page.getByRole('textbox', { name: /your question/i }).count(), 1);
  assert.equal(await page.getByRole('button', { name: /investigate records/i }).count(), 1);
  await submit(page);
  assert.equal(await page.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.match(await page.locator('#coverage-label').textContent(), /84 days/);
  assert.equal(await page.locator('.chart-point').count() > 50, true);
  assert.match(await page.locator('#trace-list').textContent(), /PLAN|plan/i);
  const firstPoint = page.locator('.chart-point').first();
  const sourceId = await firstPoint.getAttribute('data-source-id');
  await firstPoint.focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.getByRole('dialog', { name: 'Point provenance.' }).count(), 1);
  assert.match(await page.locator('#dialog-content').textContent(), new RegExp(sourceId));
  assert.match(await page.locator('#dialog-content').textContent(), /zetaris: NOT_CONNECTED/);
  await page.screenshot({ path: path.join(output, 'en-desktop-evidence.png'), fullPage: true });
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('#evidence-dialog').evaluate(el => el.open), false);
  await page.screenshot({ path: path.join(output, 'en-desktop-pass.png'), fullPage: true });
  const parentId = await page.locator('#run-id').textContent();
  // Every POST uses a fresh Python process; the next run must read JSONL from disk.
  await page.reload();
  await page.getByRole('button', { name: 'Explore sleep' }).click();
  assert.match(await page.locator('#followup-context').textContent(), new RegExp(parentId));
  await submit(page);
  assert.equal(await page.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.match(await page.locator('#result-context').textContent(), /World Model/);
  assert.match(await page.locator('#trace-list').textContent(), /get_variable_coverage/);
  assert.notEqual(bridgePids[0], bridgePids[1]);
  await page.screenshot({ path: path.join(output, 'en-desktop-followup.png'), fullPage: true });

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1,
    isMobile: true, hasTouch: true });
  await mobile.route('**/*', routeRequest);
  const mobilePage = await mobile.newPage();
  mobilePage.on('pageerror', error => pageErrors.push(error.message));
  await mobilePage.goto(url);
  await submit(mobilePage);
  assert.equal(await mobilePage.locator('#status-label').textContent(), 'OBSERVATION AVAILABLE');
  assert.equal(await mobilePage.locator('html').getAttribute('lang'), 'en');
  await mobilePage.screenshot({ path: path.join(output, 'en-mobile-pass.png'), fullPage: true });
  assert.equal(await mobilePage.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);

  await page.goto(url + '?scenario=insufficient');
  await submit(page);
  assert.equal(await page.locator('#status-label').textContent(), 'INSUFFICIENT EVIDENCE');
  await page.screenshot({ path: path.join(output, 'en-desktop-insufficient.png'), fullPage: true });
  await page.goto(url + '?scenario=tool_error');
  await submit(page);
  assert.equal(await page.locator('#status-label').textContent(), 'LOCAL TOOL UNAVAILABLE');
  await page.screenshot({ path: path.join(output, 'en-desktop-error.png'), fullPage: true });
  await page.goto(url);
  await page.getByRole('button', { name: 'Clinical request' }).click();
  await submit(page);
  assert.equal(await page.locator('#status-label').textContent(), 'AGENT ABSTAINED');
  await page.screenshot({ path: path.join(output, 'en-desktop-abstention.png'), fullPage: true });
  assert.deepEqual(pageErrors, []);
  console.log('PASS Chrome desktop/mobile, keyboard evidence, persisted follow-up, sparse, error, and abstention; screenshots in docs/evidence');
} finally {
  await browser?.close();
}
