#!/usr/bin/env node
// Motion-library integrity and sampled-pose QA. This is a deterministic preflight,
// not a substitute for reviewing rendered animation at full size.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const LIB_PATH = path.join(ROOT, 'templates', 'motion_styles', 'library.mjs');
const MOVES = path.join(ROOT, 'templates', 'motion_styles', 'moves');
const args = process.argv.slice(2);
const outArg = args.indexOf('--json');
const jsonPath = outArg >= 0 && args[outArg + 1] ? path.resolve(args[outArg + 1]) : null;
const { LIB } = await import(pathToFileURL(LIB_PATH).href);

const modules = [...new Set(LIB.map(x => String(x.module).split('#')[0]))].sort();
const issues = [];
const warnings = [];
const context = {
  form: 'standard', bodyTop: 333, bodyBot: 640, ground: 900, K: 1.5,
  hipY: 610, legL: 300, sh: [120, 430], armL: 250, handX: 120, hipW: 13,
};
let imported = 0, stylesChecked = 0, posesChecked = 0, refsChecked = 0;
const moduleCache = new Map();

function issue(where, message) { issues.push({ where, message }); }
function scanNumbers(value, where, depth = 0) {
  if (depth > 14) { issue(where, 'pose object nesting exceeds 14 levels'); return; }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) issue(where, 'non-finite numeric value');
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((v, i) => scanNumbers(v, `${where}[${i}]`, depth + 1));
    return;
  }
  if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) scanNumbers(child, `${where}.${key}`, depth + 1);
  }
}
function styleExports(mod) {
  return Object.entries(mod).filter(([, value]) => value && Array.isArray(value.styles));
}
function checkPose(pose, where) {
  posesChecked++;
  if (!pose || typeof pose !== 'object' || Array.isArray(pose)) {
    issue(where, 'pose() did not return an object');
    return;
  }
  scanNumbers(pose, where);
  const p = pose.poses ? pose.poses[0] : pose;
  if (!p || typeof p !== 'object') issue(where, 'pose.poses[0] is not an object');
  if (p?.view && !['side', 'front', '34', 'back'].includes(p.view)) issue(where, `unsupported view "${p.view}"`);
  if (p?.feet != null) {
    if (!Array.isArray(p.feet)) issue(where, 'feet is not an array');
    else p.feet.forEach((foot, i) => {
      if (!foot || typeof foot !== 'object') { issue(`${where}.feet[${i}]`, 'foot is not an object'); return; }
      if (!Number.isFinite(foot.x)) issue(`${where}.feet[${i}]`, 'foot.x is missing or non-numeric');
      if (foot.lift != null && !Number.isFinite(foot.lift)) issue(`${where}.feet[${i}]`, 'foot.lift is non-numeric');
      if (foot.down != null && typeof foot.down !== 'boolean') issue(`${where}.feet[${i}]`, 'foot.down must be boolean when supplied');
    });
  }
  if (p?.hands != null && !Array.isArray(p.hands)) issue(where, 'hands is not an array');
  if (Array.isArray(p?.hands)) p.hands.forEach((hand, i) => {
    if (hand == null) return;
    if (typeof hand !== 'object') issue(`${where}.hands[${i}]`, 'hand is not an object');
    for (const key of ['f', 'd', 'wx', 'wy', 'lx', 'ly']) {
      if (hand[key] != null && !Number.isFinite(hand[key])) issue(`${where}.hands[${i}]`, `${key} is non-numeric`);
    }
  });
}

for (const name of modules) {
  const file = path.join(MOVES, `${name}.mjs`);
  if (!fs.existsSync(file)) { issue(name, `registered module file missing: ${path.relative(ROOT, file)}`); continue; }
  try {
    const mod = await import(pathToFileURL(file).href);
    moduleCache.set(name, mod); imported++;
    const exports = styleExports(mod);
    if (!exports.length) issue(name, 'module exports no object with a styles array');
    for (const [exportName, movement] of exports) {
      for (const style of movement.styles) {
        stylesChecked++;
        if (!style || typeof style.pose !== 'function') { issue(`${name}#${exportName}`, `style ${style?.key ?? '(no key)'} has no pose() function`); continue; }
        const duration = Number(movement.dur || 6);
        if (!(duration > 0 && Number.isFinite(duration))) { issue(`${name}#${exportName}/${style.key}`, 'invalid movement duration'); continue; }
        const sampleTimes = [...new Set([0, 1 / 30, 1 / 10, duration * .25, duration * .5, duration * .75, Math.max(0, duration - 1 / 30), duration])];
        for (const t of sampleTimes) {
          const where = `${name}#${exportName}/${style.key}@${t.toFixed(3)}s`;
          try { checkPose(style.pose(t, context), where); }
          catch (error) { issue(where, `pose() threw: ${error?.stack || error}`); }
        }
      }
    }
  } catch (error) { issue(name, `module import failed: ${error?.stack || error}`); }
}

// Validate each public library record against the renderer's actual module/export/style lookup.
for (const item of LIB) {
  refsChecked++;
  const [moduleName, exportName = 'default'] = String(item.module).split('#');
  const mod = moduleCache.get(moduleName);
  if (!mod) { issue(item.id, `LIB module ${moduleName} failed to load`); continue; }
  const target = mod[exportName];
  if (!target || !Array.isArray(target.styles)) { issue(item.id, `LIB export ${moduleName}#${exportName} is missing or has no styles`); continue; }
  if (!target.styles.some(style => style.key === item.style)) issue(item.id, `LIB style "${item.style}" is missing in ${moduleName}#${exportName}`);
  if (!Array.isArray(item.views) || !item.views.length || item.views.some(v => !['side', 'front', '34', 'back'].includes(v))) issue(item.id, 'LIB record has invalid or empty views');
}

const report = {
  schema: 'ricksclips.motion-quality.v1',
  generated_at: new Date().toISOString(),
  summary: { modules_expected: modules.length, modules_imported: imported, library_entries: LIB.length, library_references_checked: refsChecked, exported_styles_checked: stylesChecked, pose_samples_checked: posesChecked, errors: issues.length, warnings: warnings.length },
  status: issues.length ? 'FAIL' : 'PASS',
  issues, warnings,
  notes: [
    'Deterministic sampled-pose and library-integrity checks only.',
    'Rendered foot contact, silhouette, timing, overlap and acting still require frame review / GPU frame checks.',
  ],
};
if (jsonPath) {
  fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
  fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2) + '\n');
}
console.log(`Motion QA: ${report.status}`);
console.log(`Modules ${imported}/${modules.length} | LIB refs ${refsChecked}/${LIB.length} | styles ${stylesChecked} | sampled poses ${posesChecked}`);
if (issues.length) for (const item of issues.slice(0, 60)) console.log(`FAIL ${item.where}: ${item.message}`);
if (issues.length > 60) console.log(`... ${issues.length - 60} more errors (see JSON report)`);
if (!issues.length) console.log('No missing library references, invalid views, malformed contacts/hands, thrown pose functions or non-finite pose numbers found.');
process.exit(issues.length ? 1 : 0);
