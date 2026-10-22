import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve, dirname, extname } from 'node:path';

const root = dirname(fileURLToPath(import.meta.url));
const types = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.mjs':'text/javascript; charset=utf-8' };
const port = Number(process.env.PORT || 4173);
createServer(async (request,response) => {
  const path = new URL(request.url,'http://localhost').pathname;
  const file = path === '/' ? 'index.html' : decodeURIComponent(path).slice(1);
  if (!['index.html','styles.css','app.mjs','tools.mjs','fixture.mjs'].includes(file)) { response.writeHead(404); response.end('Not found'); return; }
  try { const body = await readFile(resolve(root,file)); response.writeHead(200,{'Content-Type':types[extname(file)],'Cache-Control':'no-store'}); response.end(body); }
  catch { response.writeHead(404); response.end('Not found'); }
}).listen(port,'127.0.0.1',() => console.log(`PHIS UI demo: http://127.0.0.1:${port}`));
