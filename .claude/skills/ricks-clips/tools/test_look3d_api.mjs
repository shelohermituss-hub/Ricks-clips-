#!/usr/bin/env node
// Headless object-graph smoke test for the additive kit3d APIs (no GPU render).
import assert from 'node:assert/strict';
import * as THREE from '../templates/threejs_film/vendor/three.module.js';
import { makeKit3d } from '../templates/threejs_film/look3d.mjs';
import { build as buildPlatform } from '../templates/threejs_film/sets/platform.js';

const ctx2d = {
  clearRect() {}, save() {}, translate() {}, rotate() {}, beginPath() {}, ellipse() {}, fill() {},
  moveTo() {}, lineTo() {}, stroke() {}, arc() {}, restore() {},
};
globalThis.document = { createElement: () => ({ width: 0, height: 0, getContext: () => ctx2d }) };
const scene = new THREE.Scene();
const light = { dir: [-3, 10, 4], sun: '#fff1df', hor: '#9eb5cf', amb: '#aabbcc', ai: .5, si: 2 };
const toon = color => new THREE.MeshToonMaterial({ color });
const kit = makeKit3d(THREE, scene, light, { pbr: true, relief: true, sky: true, trees: true }, toon);
const hill = kit.terrain.hill({ width: 70, depth: 50, height: 8, segments: 24, seed: 7 });
const ridge = kit.terrain.ridge({ width: 110, depth: 60, height: 24, segments: 32, seed: 8, at: [0, 30, 0] });
const mountain = kit.terrain.mountain({ width: 150, depth: 80, height: 48, segments: 40, seed: 9, at: [0, 70, 0], snowColor: '#e8eef5' });
const rocks = kit.detail.rocks({ at: [0, 0, 0], surface: hill, count: 25, radius: 8, seed: 3 });
const grass = kit.detail.grass({ at: [0, 0, 0], surface: hill, count: 40, radius: 7, seed: 4 });
const pine = kit.trees.tree({ kind: 'pine', seed: 5, at: [4, 2, 0] });
const birch = kit.trees.tree({ kind: 'birch', seed: 6, at: [-4, 2, 0] });
const wind = kit.atmosphere.setWind({ direction: [0.8, 0.6], strength: .9, gust: .25, speed: 1.2 });
assert(Math.abs(Math.hypot(...wind.direction) - 1) < 1e-6, 'wind direction should be normalized');
kit.atmosphere.setFog({ color: '#a0b3c6', near: 20, far: 180 });
assert(scene.fog instanceof THREE.Fog, 'linear fog should be applied');
const B2T = p => new THREE.Vector3(p[0], p[2], -p[1]);
const setResult = buildPlatform(THREE, scene, { places: { platform: { sky_kind: 'clear-day' } } }, {
  B2T, toon, light, pbr: kit.pbr, relief: kit.relief, sky: kit.sky, trees: kit.trees,
  terrain: kit.terrain, detail: kit.detail, atmosphere: kit.atmosphere,
});
assert(setResult && setResult.anchors && setResult.anchors.clock, 'starter platform set should build with the enhanced environment API');
assert(scene.children.some(o => o.name === 'terrain_hill'), 'starter platform should include its terrain layer');
assert(scene.children.some(o => o.name.startsWith('tree_')), 'starter platform should use the detailed tree builder');
assert(scene.children.some(o => o.name === 'kit_clouds'), 'starter platform should build the weather-matched cloud layer');
assert.equal(typeof kit.finish, 'function', 'finish should remain callable by the live renderer');
if (typeof setResult.update === 'function') setResult.update(1, 1.25);
// Exercise the frame tick without triggering the PMREM bake, which intentionally needs a real WebGLRenderer.
const tickKit = makeKit3d(THREE, new THREE.Scene(), light, { pbr: false, relief: false, sky: false, trees: true }, toon);
tickKit.trees.tree({ kind: 'pine', seed: 12 });
const update = tickKit.finish(null, () => null);
assert.equal(typeof update, 'function', 'finish should return the time-update wrapper when frame ticks are registered');
update(1, 1.25, null);
for (const mesh of [hill, ridge, mountain]) {
  assert(mesh.isMesh, `${mesh.name} should be a mesh`);
  assert(mesh.geometry.attributes.position.count > 0, `${mesh.name} should contain vertices`);
  assert(mesh.geometry.attributes.color.count > 0, `${mesh.name} should contain vertex colours`);
}
assert.equal(rocks.count, 25); assert.equal(grass.count, 40);
const sampleInstanceYs = mesh => Array.from({ length: mesh.count }, (_, i) => { const m = new THREE.Matrix4().fromArray(mesh.instanceMatrix.array, i * 16); return m.elements[13]; });
const rockYs = sampleInstanceYs(rocks), grassYs = sampleInstanceYs(grass);
assert(Math.max(...rockYs) - Math.min(...rockYs) > .05, 'rocks should follow terrain height variation');
assert(Math.max(...grassYs) - Math.min(...grassYs) > .05, 'grass should follow terrain height variation');
assert(pine.children.some(o => o.name === 'tree_leaves'), 'pine foliage should exist');
assert(birch.children.some(o => o.name === 'tree_leaves'), 'birch foliage should exist');
console.log('LOOK3D API SMOKE PASS: terrain hill/ridge/mountain, surface-conformed rocks/grass, pine/birch, PBR starter-platform set, wind, fog and update tick.');
