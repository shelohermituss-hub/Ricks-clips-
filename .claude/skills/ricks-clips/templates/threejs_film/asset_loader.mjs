// Runtime GLB/glTF and PBR material loader for the RicksClips Three.js film kit.
// All paths must be episode-local. The renderer's single vendored THREE build is reused.
export function createAssetLoader(THREE, episodeBase = './') {
  let gltfLoaderPromise = null;
  const loaded = new Map();
  const loadedTextures = new Map();
  const safeRel = value => {
    const s = String(value || '').replace(/\\/g, '/');
    if (!s || s.startsWith('/') || /^[a-z]+:/i.test(s) || s.split('/').includes('..')) {
      throw new Error(`Unsafe asset path: ${s}`);
    }
    return s;
  };
  const resolve = rel => new URL(safeRel(rel), new URL(episodeBase, window.location.href)).href;
  const getGltfLoader = async () => {
    if (!gltfLoaderPromise) gltfLoaderPromise = import('three/addons/loaders/GLTFLoader.js').then(({ GLTFLoader }) => new GLTFLoader());
    return gltfLoaderPromise;
  };
  const texture = async (rel, colour = false, repeat = null) => {
    const url = resolve(rel);
    const key = `${url}|${colour}|${JSON.stringify(repeat || [])}`;
    if (loadedTextures.has(key)) return loadedTextures.get(key);
    const result = new Promise((resolvePromise, reject) => {
      new THREE.TextureLoader().load(url, resolvePromise, undefined, reject);
    }).then(tex => {
      tex.flipY = false;
      if (colour) tex.colorSpace = THREE.SRGBColorSpace;
      if (repeat && Array.isArray(repeat) && repeat.length === 2) {
        tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
        tex.repeat.set(Number(repeat[0]), Number(repeat[1]));
      }
      tex.anisotropy = 8;
      tex.needsUpdate = true;
      loadedTextures.set(key, tex);
      return tex;
    });
    loadedTextures.set(key, result);
    return result;
  };
  async function load(scene, spec) {
    if (!spec || typeof spec !== 'object') throw new TypeError('Asset spec must be an object');
    const id = String(spec.id || spec.file || 'asset');
    const key = `${id}|${spec.file || ''}`;
    if (loaded.has(key)) return loaded.get(key);
    const ext = String(spec.file || '').split('.').pop().toLowerCase();
    if (!['glb', 'gltf'].includes(ext)) {
      throw new Error(`Three.js runtime accepts .glb/.gltf only; convert ${spec.file} to glTF 2.0/GLB first (Blender import/export).`);
    }
    // Validate and resolve the local path before importing the optional GLTFLoader dependency.
    const assetUrl = resolve(spec.file);
    const loader = await getGltfLoader();
    const gltf = await loader.loadAsync(assetUrl);
    const root = gltf.scene || (gltf.scenes && gltf.scenes[0]);
    if (!root) throw new Error(`No scene in glTF asset ${spec.file}`);
    root.name = spec.name || id;
    const p = spec.position || [0, 0, 0]; // authored in film plan coordinates: [x, y-forward, z-up]
    if (!Array.isArray(p) || p.length !== 3 || p.some(v => !Number.isFinite(Number(v)))) throw new Error(`Invalid position for ${id}`);
    root.position.set(Number(p[0]), Number(p[2]), -Number(p[1]));
    const s = spec.scale === undefined ? 1 : spec.scale;
    if (Array.isArray(s)) root.scale.set(Number(s[0]), Number(s[2] ?? s[1]), Number(s[1]));
    else root.scale.setScalar(Number(s));
    if (![root.scale.x, root.scale.y, root.scale.z].every(Number.isFinite)) throw new Error(`Invalid scale for ${id}`);
    const rot = Number(spec.rotationY ?? spec.yaw ?? 0);
    if (!Number.isFinite(rot)) throw new Error(`Invalid rotation for ${id}`);
    root.rotation.y = -rot * Math.PI / 180;
    root.traverse(obj => {
      if (obj.isMesh) {
        obj.castShadow = spec.castShadow !== false;
        obj.receiveShadow = spec.receiveShadow !== false;
        obj.userData = { ...(obj.userData || {}), ricksAssetId: id, ricksAssetProvider: spec.provider || 'library' };
      }
    });
    root.userData = { ...(root.userData || {}), ricksAssetId: id, ricksAssetProvider: spec.provider || 'library', ricksAssetLicense: spec.license || 'see ASSET_MANIFEST.json' };
    root.updateMatrixWorld(true);
    scene.add(root);
    const rec = { root, animations: gltf.animations || [], scene: gltf };
    loaded.set(key, rec);
    return rec;
  }
  async function applyMaterials(scene, specs = []) {
    if (!Array.isArray(specs)) throw new TypeError('place.materials must be an array');
    const result = { applied: [], failed: [] };
    for (const spec of specs) {
      try {
        const maps = spec.maps || {};
        const channelMap = {};
        for (const [channel, path] of Object.entries(maps)) {
          if (path) channelMap[channel] = await texture(path, channel === 'color', spec.repeat || null);
        }
        const targets = new Set((spec.target_materials || []).map(x => String(x).toLowerCase()));
        if (!targets.size) throw new Error(`Material asset ${spec.id || 'unnamed'} has no target_materials; refusing to alter every material in the scene`);
        let matched = 0;
        scene.traverse(obj => {
          if (!obj.isMesh || !obj.material) return;
          const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
          let changed = false;
          for (const mat of mats) {
            if (!targets.has(String(mat.name || '').toLowerCase())) continue;
            if (channelMap.color) mat.map = channelMap.color;
            if (channelMap.normal) mat.normalMap = channelMap.normal;
            if (channelMap.roughness) mat.roughnessMap = channelMap.roughness;
            if (channelMap.metalness) mat.metalnessMap = channelMap.metalness;
            if (channelMap.ao) mat.aoMap = channelMap.ao;
            if (channelMap.displacement) mat.displacementMap = channelMap.displacement;
            if (spec.roughnessFactor !== undefined && 'roughness' in mat) mat.roughness = Number(spec.roughnessFactor);
            if (spec.metalnessFactor !== undefined && 'metalness' in mat) mat.metalness = Number(spec.metalnessFactor);
            if (spec.normalScale && mat.normalScale) mat.normalScale.set(Number(spec.normalScale[0]), Number(spec.normalScale[1]));
            mat.needsUpdate = true;
            changed = true;
          }
          if (changed) matched++;
        });
        if (!matched) throw new Error(`No mesh material matched targets: ${[...targets].join(', ')}`);
        result.applied.push({ id: spec.id || spec.asset_id || 'material', matched_meshes: matched, channels: Object.keys(channelMap) });
      } catch (error) {
        result.failed.push({ id: spec && (spec.id || spec.asset_id), error: String(error.message || error), required: !!(spec && spec.required) });
        if (spec && spec.required) throw new Error(`Required material ${spec.id || spec.asset_id} failed: ${error.message || error}`);
        console.warn('[RicksClips PBR material]', error);
      }
    }
    return result;
  }
  async function loadMany(scene, specs = []) {
    if (!Array.isArray(specs)) throw new TypeError('place.assets must be an array');
    const result = { loaded: [], failed: [] };
    for (const spec of specs) {
      try { const r = await load(scene, spec); result.loaded.push({ id: spec.id || spec.file, root: r.root, animations: r.animations }); }
      catch (error) {
        result.failed.push({ id: spec && (spec.id || spec.file), error: String(error.message || error), required: !!(spec && spec.required) });
        if (spec && spec.required) throw new Error(`Required asset ${spec.id || spec.file} failed: ${error.message || error}`);
        console.warn('[RicksClips asset]', error);
      }
    }
    return result;
  }
  return { load, loadMany, applyMaterials, resolve, loaded, loadedTextures };
}
