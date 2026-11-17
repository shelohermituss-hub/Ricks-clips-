#!/usr/bin/env node
// Offline smoke tests for the episode-local Three.js asset and PBR loader.
import assert from 'node:assert/strict';
import { createAssetLoader } from '../templates/threejs_film/asset_loader.mjs';

globalThis.window = { location: { href: 'file:///C:/RicksClips/film_page.html' } };
const textureRequests = [];
class TextureLoader {
  load(url, onLoad) {
    textureRequests.push(url);
    const tex = { flipY: true, colorSpace: '', anisotropy: 0, needsUpdate: false,
      wrapS: null, wrapT: null, repeat: { set(x, y) { this.x = x; this.y = y; } } };
    onLoad(tex);
  }
}
const THREE = { TextureLoader, SRGBColorSpace: 'srgb', RepeatWrapping: 'repeat' };
const loader = createAssetLoader(THREE, 'episodes/demo/');

const material = { name: 'wet_stone', roughness: 1, metalness: 0,
  normalScale: { set(x, y) { this.x = x; this.y = y; } }, needsUpdate: false };
const mesh = { isMesh: true, material };
const scene = { traverse(fn) { fn(mesh); } };
const applied = await loader.applyMaterials(scene, [{
  id: 'stone_surface', maps: { color: 'assets/stone_color.jpg', normal: 'assets/stone_normal.png', roughness: 'assets/stone_roughness.png' },
  target_materials: ['wet_stone'], repeat: [2, 3], normalScale: [0.8, 0.8]
}]);
assert.equal(applied.applied.length, 1);
assert.equal(applied.failed.length, 0);
assert.equal(textureRequests.length, 3);
assert.equal(material.map.colorSpace, 'srgb');
assert.equal(material.map.repeat.x, 2);
assert.equal(material.normalMap.flipY, false);
assert.equal(material.roughnessMap.anisotropy, 8);
assert.equal(material.normalScale.x, 0.8);
assert.equal(material.needsUpdate, true);

const originalWarn = console.warn;
console.warn = () => {};
const refused = await loader.applyMaterials(scene, [{ id: 'untargeted', maps: { color: 'assets/a.jpg' }, target_materials: [] }]);
console.warn = originalWarn;
assert.equal(refused.failed.length, 1);
assert.match(refused.failed[0].error, /no target_materials/i);
await assert.rejects(() => loader.load(scene, { id: 'escape', file: '../outside.glb' }), /Unsafe asset path/);
await assert.rejects(() => loader.load(scene, { id: 'wrong-format', file: 'assets/model.fbx' }), /accepts .glb\/\.gltf only/);
console.log('ASSET_LOADER_TESTS_PASS: PBR maps, target-material safety, episode-relative paths and format guards');
