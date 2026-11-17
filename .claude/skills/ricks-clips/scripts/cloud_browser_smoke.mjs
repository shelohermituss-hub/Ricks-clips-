#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(ROOT, 'templates/threejs_film/node_modules/playwright'));
const executablePath = process.env.CHROME_PATH || '/usr/bin/google-chrome';
const browser = await chromium.launch({ executablePath, headless: true, timeout: 30000,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
try {
  const page = await browser.newPage();
  const info = await page.evaluate(() => {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return { ok: false, reason: 'WebGL context unavailable' };
    const ext = gl.getExtension('WEBGL_debug_renderer_info');
    return { ok: true, version: gl.getParameter(gl.VERSION), renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'masked' };
  });
  if (!info.ok) throw new Error(info.reason);
  console.log(`[PASS] Chrome + Playwright + WebGL: ${info.version}; renderer=${info.renderer}`);
} finally { await browser.close(); }
