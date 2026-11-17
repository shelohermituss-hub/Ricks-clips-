// LE DERNIER PHARE — set "coast": a rocky headland at night in a storm, the last lighthouse, the sea breaking on the rocks.
// Cloud validation film (2026-11-17). Kit API: PBR_FEATURES.md (ctx.sky / ctx.terrain / ctx.detail / ctx.atmosphere / ctx.fx.bolt / ctx.pbr / ctx.relief).
// Plan coordinates: metres, Z up, Y away from the opening camera. Lina stands on the ledge top at z = 0, the lighthouse on the island behind her.
// Story events (frames) come from film.json places.coast.events: out = the lamp dies with the lightning, on = it comes back.
export function build(THREE, scene, film, ctx) {
  const { B2T, toon } = ctx, P = ctx.place || {}, EV = P.events || { out: 68, on: 152, levee: 112 };
  const V = (x, y, z) => B2T([x, y, z]), n = {};
  const add = (m, name, role, o = {}) => { n[name] = (n[name] || 0) + 1; m.name = n[name] > 1 ? `${name}_${String(n[name]).padStart(2, '0')}` : name; m.userData.role = role; if (o.mat) m.userData.mat = o.mat; m.castShadow = o.cast ?? true; m.receiveShadow = o.receive ?? true; (o.parent || scene).add(m); return m; };
  let seed = 9173; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647, rr = (a, b) => a + rnd() * (b - a);
  const relief = (kind, col, o = {}) => ctx.relief ? ctx.relief(kind, col, o) : toon(col);
  const canvasTex = (w, h, draw) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const glowTex = canvasTex(128, 128, (g, w) => { const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.25, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, w); });
  const glow = (col, size, op, at, parent = scene) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); s.scale.setScalar(size); s.position.copy(at); s.userData.noExport = true; parent.add(s); return s; };

  // ---------------- sky, fog, wind ----------------
  const clouds = ctx.sky && ctx.sky.on ? ctx.sky.clouds({ kind: 'night-storm', seed: 41, sunDir: [.45, .35, -.6], coverage: 1.15 }) : null;
  if (ctx.atmosphere) { ctx.atmosphere.setFog({ color: '#1b2547', near: 28, far: 230 }); ctx.atmosphere.setWind({ direction: [1, .3], strength: .95, gust: .45, speed: 1.4 }); }

  // ---------------- the sea: a displaced wet surface, swell from the open sea, chop on top ----------------
  const SEA_Z = -1.7, SEA = new THREE.PlaneGeometry(260, 260, 150, 150); SEA.rotateX(-Math.PI / 2);
  const seaMat = ctx.pbr ? ctx.pbr.metal('wet', { color: '#0d2733', rough: .2, env: .9, coat: 1, coatRough: .12 }) : toon('#123446');
  const sea = add(new THREE.Mesh(SEA, seaMat), 'sea', 'water', { cast: false, mat: 'water' }); sea.position.copy(V(0, 60, SEA_Z));
  const seaBase = SEA.attributes.position.array.slice();
  const wave = (x, z, t) => { const d = -z; return .55 * Math.sin(.21 * x + .34 * d - 1.5 * t) + .32 * Math.sin(-.37 * x + .26 * d - 2.1 * t + 1.3) + .14 * Math.sin(.9 * x - .7 * d - 3.4 * t) + .07 * Math.sin(1.7 * x + 1.3 * d - 4.6 * t); };
  // foam: soft white patches that ride the crests near the rocks, and spray bursts where the swell hits
  const foamTex = canvasTex(256, 256, (g, w) => { g.clearRect(0, 0, w, w); for (let i = 0; i < 260; i++) { const x = rr(0, w), y = rr(0, w), r = rr(2, 14); const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(255,255,255,.75)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); } });
  const foams = [];
  for (const [x, y, s] of [[-1.5, 4.2, 9], [9, 6.5, 10], [2.5, 2.8, 7], [11, 15, 9], [-6, 12, 10], [-4, 3.2, 6], [6, 3.5, 6]]) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(s, s * .55), new THREE.MeshBasicMaterial({ map: foamTex, color: '#dfe9ff', transparent: true, opacity: .5, depthWrite: false, fog: true }));
    m.rotation.x = -Math.PI / 2; m.position.copy(V(x, y, SEA_Z + .5)); m.userData.noExport = true; m.name = 'sea_foam'; scene.add(m); foams.push({ m, x, y, ph: rr(0, 6.3) });
  }
  const spray = []; for (let i = 0; i < 70; i++) { const s = glow('#cfdcff', rr(.35, 1.1), 0, V(0, 0, 0)); s.material.fog = true; const site = [[-1.2, 3.8], [8.5, 6], [2.5, 2.6], [-4.2, 3.4]][i % 4]; spray.push({ s, site, ph: rr(0, 1), per: Math.round(rr(46, 74)), dx: rr(-1.4, 1.4), dy: rr(-.6, .6), h: rr(1.2, 3.4) }); }

  // ---------------- the rocks: Lina's ledge, the island, boulders (material "cliff_rock" takes the Asset Hub PBR maps) ----------------
  const rockMat = new THREE.MeshStandardMaterial({ name: 'cliff_rock', color: '#9aa0a8', roughness: .92, metalness: 0 });
  const rockGeo = (r, sx, sy, sz, sd) => { const g = new THREE.IcosahedronGeometry(r, 3), p = g.attributes.position, v = new THREE.Vector3(); let s2 = sd; const h = () => (s2 = (s2 * 16807) % 2147483647) / 2147483647;
    const k = [h(), h(), h(), h()].map(q => q * 6.28); for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); const d = 1 + .18 * Math.sin(v.x * 2.1 + k[0]) * Math.sin(v.y * 1.7 + k[1]) + .1 * Math.sin(v.z * 3.3 + k[2]) + .06 * Math.sin((v.x + v.z) * 6 + k[3]); v.multiplyScalar(d); v.set(v.x * sx, v.y * sy, v.z * sz); p.setXYZ(i, v.x, v.y, v.z); }
    g.computeVertexNormals(); return g; };
  const boulder = (name, at, r, s, sd, rot = 0) => { const m = add(new THREE.Mesh(rockGeo(r, ...s, sd), rockMat), name, 'stone', { mat: 'rock' }); m.position.copy(V(...at)); m.rotation.y = rot; return m; };
  // the ledge Lina stands on: a broad flat-topped slab, top at z = 0
  const ledge = add(new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.8, 2.2, 28, 3), rockMat), 'ledge', 'stone', { mat: 'rock' }); ledge.position.copy(V(0, .4, -1.1));
  { const p = ledge.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y < 1.05) { const a = Math.atan2(p.getZ(i), p.getX(i)); const k = 1 + .12 * Math.sin(a * 5 + y) + .07 * Math.sin(a * 11); p.setX(i, p.getX(i) * k); p.setZ(i, p.getZ(i) * k); } } ledge.geometry.computeVertexNormals(); }
  boulder('ledge_boulder', [-2.4, 1.6, -.4], 1.05, [1.2, .8, 1], 11, .4); boulder('ledge_boulder', [2.2, -.2, -.9], .9, [1.3, .7, 1.1], 12, 1.2); boulder('ledge_boulder', [-1.6, -1.3, -1.2], .8, [1.4, .6, 1], 13);
  boulder('shore_rock', [-4.5, 3.6, -1.6], 1.4, [1.4, .7, 1.1], 21, .3); boulder('shore_rock', [3.6, 2.8, -1.7], 1.2, [1.6, .6, 1.2], 22, 2.1); boulder('shore_rock', [-1.2, 4.6, -2], 1.1, [1.3, .5, 1], 23);
  // the island the lighthouse stands on
  const island = ctx.terrain ? ctx.terrain.hill({ at: [6, 13, SEA_Z - .6], width: 22, depth: 18, height: 5.2, segments: 90, seed: 12, baseColor: '#3e4048', grassColor: '#3d4a36', rockColor: '#6a6b72' }) : null;
  for (let i = 0; i < 9; i++) { const a = i / 9 * 6.28, r = rr(7, 9.5); boulder('island_rock', [6 + Math.cos(a) * r, 13 + Math.sin(a) * r * .8, SEA_Z + rr(-.2, .8)], rr(1.2, 2.2), [1.3, .75, 1.1], 30 + i, rr(0, 6)); }
  if (ctx.detail && island) { ctx.detail.rocks({ at: [6, 13, 0], surface: island, count: 70, radius: 7, size: .32, seed: 8, colors: ['#5d5e66', '#6f6e72', '#4c4d55'] }); ctx.detail.grass({ at: [6, 12, 0], surface: island, count: 340, radius: 6.5, height: .45, seed: 9 }); }

  // ---------------- the lighthouse ----------------
  const LH = [6.4, 14, 3.4], H = 13, lh = new THREE.Group(); lh.name = 'lighthouse'; lh.position.copy(V(...LH)); scene.add(lh);
  const white = relief('plaster', '#e9e4da', { seed: 4 }), red = relief('plaster', '#b3332e', { seed: 5 });
  const tower = add(new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.7, H, 40, 1), white), 'tower', 'plaster', { parent: lh, mat: 'plaster' }); tower.position.y = H / 2;
  for (const [y0, y1] of [[3.2, 5.0], [8.2, 10.0]]) { const r = y => 1.7 - (1.7 - 1.15) * (y / H) + .015; const b = add(new THREE.Mesh(new THREE.CylinderGeometry(r(y1), r(y0), y1 - y0, 40, 1), red), 'tower_band', 'plaster', { parent: lh, mat: 'plaster' }); b.position.y = (y0 + y1) / 2; }
  const plinth = add(new THREE.Mesh(new THREE.CylinderGeometry(2.1, 2.3, .9, 32), relief('stone', '#8d8a86', { seed: 3 })), 'tower_plinth', 'stone', { parent: lh, mat: 'stone' }); plinth.position.y = .2;
  const iron = ctx.pbr ? ctx.pbr.metal('iron', { color: '#2a2c33', rust: .35, rough: .5 }) : toon('#2a2c33');
  const door = add(new THREE.Mesh(new THREE.BoxGeometry(.8, 1.7, .12), relief('wood', '#4a2e22', { seed: 7 })), 'tower_door', 'wood', { parent: lh }); door.position.set(0, 1.5, 1.66);
  for (const y of [4.1, 6.8, 9.3]) { const w = add(new THREE.Mesh(new THREE.BoxGeometry(.38, .6, .1), new THREE.MeshBasicMaterial({ color: '#1a1d29' })), 'tower_window', 'glass', { parent: lh }); const r = 1.7 - .55 * (y / H); w.position.set(0, y, r - .01); }
  const gallery = add(new THREE.Mesh(new THREE.CylinderGeometry(1.75, 1.55, .25, 36), iron), 'gallery_deck', 'metal', { parent: lh, mat: 'metal' }); gallery.position.y = H + .12;
  const rail = add(new THREE.Mesh(new THREE.TorusGeometry(1.72, .035, 6, 48), iron), 'gallery_rail', 'metal', { parent: lh }); rail.rotation.x = Math.PI / 2; rail.position.y = H + 1.05;
  for (let i = 0; i < 20; i++) { const a = i / 20 * 6.28, p = add(new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, .9, 5), iron), 'gallery_post', 'metal', { parent: lh, cast: false }); p.position.set(Math.cos(a) * 1.72, H + .6, Math.sin(a) * 1.72); }
  const glassMat = new THREE.MeshPhysicalMaterial({ color: '#a9c4e6', roughness: .08, metalness: 0, transparent: true, opacity: .32, depthWrite: false });
  const lantern = add(new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 1.7, 16, 1, true), glassMat), 'lantern_glass', 'glass', { parent: lh, cast: false }); lantern.position.y = H + 1.1;
  for (let i = 0; i < 8; i++) { const a = i / 8 * 6.28, m = add(new THREE.Mesh(new THREE.BoxGeometry(.06, 1.7, .06), iron), 'lantern_mullion', 'metal', { parent: lh, cast: false }); m.position.set(Math.cos(a) * 1.0, H + 1.1, Math.sin(a) * 1.0); }
  const dome = add(new THREE.Mesh(new THREE.SphereGeometry(1.1, 24, 10, 0, 6.29, 0, Math.PI / 2), ctx.pbr ? ctx.pbr.metal('bronze', { color: '#3e5a4e', patina: .6 }) : toon('#3e5a4e')), 'lantern_dome', 'metal', { parent: lh, mat: 'metal' }); dome.position.y = H + 1.95;
  const vent = add(new THREE.Mesh(new THREE.SphereGeometry(.22, 12, 8), iron), 'dome_vent', 'metal', { parent: lh }); vent.position.y = H + 3.15;
  const rod = add(new THREE.Mesh(new THREE.CylinderGeometry(.02, .02, 1.2, 5), iron), 'lightning_rod', 'metal', { parent: lh, cast: false }); rod.position.y = H + 3.8;
  // the lamp: a bright core, a halo, a point light, and two beams that sweep round
  const LAMP_Y = H + 1.1, lampCore = add(new THREE.Mesh(new THREE.SphereGeometry(.34, 16, 12), new THREE.MeshBasicMaterial({ color: '#fff3c8', fog: false })), 'lamp_core', 'lamp', { parent: lh, cast: false }); lampCore.position.y = LAMP_Y;
  const halo = glow('#ffe2a0', 7, 1, new THREE.Vector3(0, LAMP_Y, 0), lh), halo2 = glow('#ffd27a', 22, .35, new THREE.Vector3(0, LAMP_Y, 0), lh);
  const lampLight = new THREE.PointLight('#ffd99a', 60, 60, 1.6); lampLight.position.set(0, LAMP_Y, 0); lh.add(lampLight);
  const beamTex = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.7, 'rgba(255,255,255,.35)'); gr.addColorStop(1, 'rgba(255,255,255,1)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
  const beamRig = new THREE.Group(); beamRig.position.y = LAMP_Y; beamRig.userData.noExport = true; lh.add(beamRig); const beams = [];
  for (const s of [1, -1]) { const geo = new THREE.ConeGeometry(4.2, 70, 24, 1, true); geo.translate(0, -35, 0); geo.rotateZ(s * Math.PI / 2); const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: beamTex, color: '#fff0c4', transparent: true, opacity: .32, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false })); m.rotation.z = s * -.06; m.name = 'lamp_beam'; m.userData.noExport = true; beamRig.add(m); beams.push(m); }
  // keeper's cottage at the foot of the tower, one warm window
  const cot = new THREE.Group(); cot.name = 'keeper_cottage'; cot.position.copy(V(LH[0] - 3.4, LH[1] - .6, LH[2] - .3)); cot.rotation.y = .35; scene.add(cot);
  const cw = add(new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.2, 2.6), relief('stone', '#9b958b', { seed: 31 })), 'cottage_walls', 'stone', { parent: cot, mat: 'stone' }); cw.position.y = 1.1;
  const roofG = new THREE.CylinderGeometry(.01, 2.1, 1.3, 4, 1); roofG.rotateY(Math.PI / 4); const roof = add(new THREE.Mesh(roofG, relief('tile', '#5a3a36', { seed: 33 })), 'cottage_roof', 'roof', { parent: cot, mat: 'roof_tile' }); roof.scale.set(1.15, 1, .95); roof.position.y = 2.85;
  const ch = add(new THREE.Mesh(new THREE.BoxGeometry(.4, 1, .4), relief('brick', '#7a4a3c', { seed: 35 })), 'cottage_chimney', 'brick', { parent: cot }); ch.position.set(.8, 3.2, -.3);
  const win = add(new THREE.Mesh(new THREE.BoxGeometry(.6, .55, .06), new THREE.MeshBasicMaterial({ color: '#ffb35a' })), 'cottage_window', 'lamp', { parent: cot, cast: false }); win.position.set(-.6, 1.3, 1.31);
  glow('#ffa040', 1.4, .55, new THREE.Vector3(-.6, 1.3, 1.45), cot); const winL = new THREE.PointLight('#ffa64a', 6, 6, 1.6); winL.position.set(-.6, 1.3, 2); cot.add(winL);
  // Lina's lantern light (her drawn lantern is the motion-library prop; this is its warm light on the rocks and on her)
  const linaL = new THREE.PointLight('#ffb760', 2.5, 5, 1.5); linaL.position.copy(V(.35, -.25, .55)); scene.add(linaL); 

  // ---------------- rain: streaks that fall in the wind around the camera ----------------
  const RN = 900, rainM = new THREE.InstancedMesh(new THREE.BoxGeometry(.008, .55, .008), new THREE.MeshBasicMaterial({ color: '#b9c9f0', transparent: true, opacity: .42, depthWrite: false, blending: THREE.AdditiveBlending, fog: false }), RN);
  rainM.name = 'rain'; rainM.userData.noExport = true; rainM.frustumCulled = false; scene.add(rainM);
  const drops = [...Array(RN)].map(() => ({ x: rr(-9, 9), y: rr(-6, 6), z: rr(-3, 22), ph: rr(0, 1), v: rr(.85, 1.15) }));
  const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, -.22)), S1 = new THREE.Vector3(1, 1, 1), Pv = new THREE.Vector3();

  // ---------------- lightning: the strike that kills the lamp, a far one when it comes back ----------------
  let bolt = null, bolt2 = null;
  if (ctx.fx && ctx.fx.bolt) {
    bolt = ctx.fx.bolt({ plan: true, from: [-14, 110, 70], to: [3, 44, SEA_Z], frame: EV.out - 1, leader: 4, restrikes: 3, after: 8, width: .5, glow: '#a8c0ff', branches: 9, levels: 3, seed: 17, point: 120, reach: 70, light: 3.4, lift: .7, clouds: clouds || undefined });
    bolt2 = ctx.fx.bolt({ plan: true, from: [40, 160, 80], to: [26, 120, SEA_Z], frame: EV.on + 58, leader: 3, restrikes: 1, after: 6, far: true, haze: .35, width: .6, glow: '#b4c4ff', branches: 6, levels: 2, seed: 29, clouds: clouds || undefined });
  }
  const lampK = f => { if (f < EV.out - 1) return 1; if (f < EV.out + 7) return [1, .2, .9, .1, .6, 0, .25, 0][f - EV.out + 1] ?? 0;   // dies in a stutter with the strike
    if (f < EV.on) return 0; const k = f - EV.on; return k < 10 ? [.15, 0, .4, .2, .7, .5, .9, .8, 1, 1][k] : 1; };   // and catches again, flickering up

  const update = (f, t, R) => {
    // sea swell + foam + spray
    const p = SEA.attributes.position, sx = sea.position.x, sz = sea.position.z;
    for (let i = 0; i < p.count; i++) { const x = seaBase[i * 3] + sx, z = seaBase[i * 3 + 2] + sz; const dist = Math.hypot(x, z); const damp = dist > 110 ? .4 : 1; p.setY(i, wave(x, z, t) * damp); }
    p.needsUpdate = true; SEA.computeVertexNormals();
    for (const F of foams) { F.m.position.y = SEA_Z + .45 + wave(F.m.position.x, F.m.position.z, t) * .9; F.m.material.opacity = .25 + .3 * Math.max(0, Math.sin(t * 1.5 + F.ph)); }
    for (const s of spray) { const q = ((f / s.per) + s.ph) % 1, up = q < .35 ? q / .35 : 1 - (q - .35) / .65; const at = V(s.site[0] + s.dx * q, s.site[1] + s.dy, SEA_Z + .4 + s.h * Math.sin(Math.min(q, .5) * Math.PI)); s.s.position.copy(at); s.s.material.opacity = Math.max(0, up) * .3; s.s.scale.setScalar(.4 + q * 1.6); }
    // lamp and beams
    const k = lampK(f); lampCore.material.color.setRGB(.25 + .75 * k, .23 + .72 * k, .2 + .58 * k); halo.material.opacity = k; halo2.material.opacity = .35 * k; lampLight.intensity = 60 * k;
    beamRig.rotation.y = -t * 1.35 + 2.2; for (const b of beams) b.material.opacity = .32 * k;
    // Lina's lantern: brighter once she raises it
    const lift = Math.min(1, Math.max(0, (f - EV.levee) / 12)); linaL.intensity = 2.2 + 3.2 * lift + .4 * Math.sin(t * 13); linaL.position.copy(V(.35, -.25, .55 + .45 * lift)); 
    // rain around the camera
    const cam = R && R.camera; const c = cam ? cam.position : new THREE.Vector3(0, 1.5, 4);
    for (let i = 0; i < RN; i++) { const d = drops[i], fall = ((t * 1.6 * d.v + d.ph) % 1); Pv.set(c.x + d.x + fall * 2.2, c.y + 8 - fall * 16, c.z - d.z); M4.compose(Pv, Q, S1); rainM.setMatrixAt(i, M4); }
    rainM.instanceMatrix.needsUpdate = true;
    // the clouds glow from inside around each bolt
    if (ctx.sky && ctx.sky.flash && cam) { const s1 = bolt && bolt.state ? bolt.state.light || 0 : 0, s2 = bolt2 && bolt2.state ? bolt2.state.light || 0 : 0;
      ctx.sky.flash(V(-24, 100, 60).sub(cam.position), Math.min(1.2, s1 * .5), { slot: 0, spread: .45 }); ctx.sky.flash(V(36, 150, 70).sub(cam.position), Math.min(.8, s2 * .4), { slot: 1, spread: .35 }); }
  };
  return { update, anchors: { lighthouse: [LH[0], LH[1], LH[2] + H + 1.1], lamp: [LH[0], LH[1], LH[2] + LAMP_Y], ledge: [0, .4, 0] } };
}
