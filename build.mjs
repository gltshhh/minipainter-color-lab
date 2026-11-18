#!/usr/bin/env node
// Pracownia barw: builds data.js and index.html from a minipainter installation.
//
//   node build.mjs [--catalog <dir>] [--inventory <file>] [--extras <file>]
//
// Defaults:
//   --catalog    <npm root -g>/minipainter/data/catalog
//   --inventory  ~/.minipainting/inventory.json   (or $MINIPAINTER_INVENTORY)
//   --extras     ./extras.json                    (optional, paints missing from the catalog)
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { homedir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const arg = name => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : undefined; };

function findCatalog() {
  if (arg('catalog')) return resolve(arg('catalog'));
  const candidates = [join(here, 'node_modules', 'minipainter', 'data', 'catalog')];
  try { candidates.push(join(execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(), 'minipainter', 'data', 'catalog')); } catch {}
  const found = candidates.find(existsSync);
  if (!found) {
    console.error('Cannot find the minipainter catalog. Install it with "npm install -g minipainter" or pass --catalog <dir>.');
    process.exit(1);
  }
  return found;
}
const catalogDir = findCatalog();
const inventoryPath = resolve(arg('inventory') || process.env.MINIPAINTER_INVENTORY || join(homedir(), '.minipainting', 'inventory.json'));
const extrasPath = resolve(arg('extras') || join(here, 'extras.json'));

let owned = [];
if (existsSync(inventoryPath)) owned = JSON.parse(readFileSync(inventoryPath, 'utf8')).owned || [];
else console.warn(`No inventory at ${inventoryPath}. Mark paints with "mpaint inventory own <id>" first; building with an empty collection.`);

// The catalog does not flag every metallic, so known Citadel metallics are listed here.
const METALLIC = new Set([
  'leadbelcher', 'retributor-armour', 'stormhost-silver', 'ironbreaker', 'runefang-steel',
  'balthasar-gold', 'auric-armour-gold', 'liberator-gold', 'gehennas-gold', 'warplock-bronze',
  'brass-scorpion', 'sycorax-bronze', 'hashut-copper', 'fulgurite-copper', 'iron-hands-steel',
  'canoptek-alloy', 'castellax-bronze', 'grey-knights-steel', 'necron-compound', 'skullcrusher-brass',
]);
const ROLE_ORDER = ['metallic', 'technical', 'contrast', 'speedpaint', 'shade', 'ink', 'dry', 'air', 'layer', 'base'];
const brands = {};
const catalog = [];
for (const f of readdirSync(catalogDir).filter(f => f.endsWith('.json'))) {
  const d = JSON.parse(readFileSync(join(catalogDir, f), 'utf8'));
  brands[d.provider.id] = d.provider.name;
  for (const p of d.paints) {
    let role = ROLE_ORDER.find(r => p.usage_roles.includes(r)) || 'base';
    if (METALLIC.has(p.id.split('/')[1]) || p.color_families.includes('metallic')) role = 'metallic';
    catalog.push([p.id, p.name, p.provider, role, p.rgb.r, p.rgb.g, p.rgb.b]);
  }
}

// extras.json: paints missing from the catalog.
//   [{ "name": "Dewpath", "brand": "Army Painter", "series": "Warpaints Fanatic", "hex": "#007969", "role": "layer" }]
// "owned" defaults to true. With "owned": false the paint joins the catalog (shop, search) instead of your collection.
const extras = [];
let extraCatalog = 0;
const slug = s => s.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
if (existsSync(extrasPath)) {
  const seen = new Set();
  for (const e of JSON.parse(readFileSync(extrasPath, 'utf8'))) {
    if (!/^#[0-9a-f]{6}$/i.test(e.hex || '')) { console.warn(`Skipping extra paint "${e.name}": hex must look like #4c8284`); continue; }
    const n = parseInt(e.hex.slice(1), 16);
    const brand = e.series ? `${e.brand}, ${e.series}` : e.brand;
    const id = `extra-${slug(brand)}/${slug(e.name)}`;
    if (seen.has(id)) { console.warn(`Skipping duplicate extra paint "${e.name}" (${brand})`); continue; }
    seen.add(id);
    const row = [id, e.name, brand, e.role || 'layer', n >> 16, (n >> 8) & 255, n & 255];
    if (e.owned === false) { catalog.push(row); extraCatalog++; } else extras.push(row);
  }
}

const data = { generated: new Date().toISOString().slice(0, 10), brands, owned, extras, catalog };
writeFileSync(join(here, 'data.js'), 'window.PALETA = ' + JSON.stringify(data) + ';\n');

// index.html = app.html wrapped in a full document, so it opens straight from disk.
const app = readFileSync(join(here, 'app.html'), 'utf8');
writeFileSync(join(here, 'index.html'),
  '<!doctype html>\n<html lang="pl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' +
  app.replace(/(<\/style>)/, '$1\n</head>\n<body>') + '\n</body>\n</html>\n');

console.log(`Catalog: ${catalog.length} paints (${catalogDir})`);
console.log(`Owned: ${owned.length} from ${inventoryPath}, extra owned: ${extras.length}, extra in catalog: ${extraCatalog}`);
console.log(`Open ${join(here, 'index.html')} in your browser.`);
