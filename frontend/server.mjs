import { spawn } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const command = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
const child = spawn(command, ['-m', 'phis_open_agent.api'], {
  cwd: root,
  env: { ...process.env, PYTHONPATH: resolve(root, 'src') },
  stdio: 'inherit',
});
child.on('error', error => { console.error(`No se pudo iniciar Python: ${error.message}`); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
