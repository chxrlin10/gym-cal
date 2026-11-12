import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { build } from 'esbuild';
await mkdir('www', { recursive: true });
let html = await readFile('index.html', 'utf8');
if (process.env.RC_PUBLIC_KEY) {
 if (!/^goog_[A-Za-z0-9_-]+$/.test(process.env.RC_PUBLIC_KEY)) throw Error('Invalid Android PUBLIC key');
 html = html.replace('const RC_KEY="";', 'const RC_KEY='+JSON.stringify(process.env.RC_PUBLIC_KEY)+';');
}
if (process.env.REQUIRE_BILLING === 'true' && html.includes('const RC_KEY="";')) throw Error('Production billing key missing');
await build({ entryPoints:['scripts/native-bridge.js'], bundle:true, format:'iife', platform:'browser', outfile:'www/native-bridge.js', minify:true });
html = html.replace('<script>', '<script src="native-bridge.js"></script>\n<script>');
await writeFile('www/index.html', html);
for (const file of ['privacidade.html','termos.html','excluir-conta.html','recuperar-senha.html']) await copyFile(file, 'www/'+file);
// Reuse the app's supplied artwork; do not invent a replacement brand.
const icon = html.match(/apple-touch-icon[^>]*href="data:image\/png;base64,([^"]+)"/);
if (!icon) throw Error('Embedded icon missing');
await mkdir('assets', { recursive:true });
await writeFile('assets/icon-only.png', Buffer.from(icon[1], 'base64'));
