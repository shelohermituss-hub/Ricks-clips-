// THE GHOST ARMY — one set module for every place of the film (set-builder + props-hero, rough board v1, 2026-11-17).
// film.json places.<name> = { "set": "ghost", "zone": "field" | "camp" | "road" | "radio" | "cafe" | "photo" | "river" | "bedroom" | "attic", "light": ... }.
// Each place is its own three.js scene; every zone is built round the origin. Plan coordinates: metres, Z up, Y away from the first camera.
// Hero objects are built here in code (the Asset Hub refuses military models on purpose): the INFLATABLE SHERMAN (rubberised canvas, valve,
// patch, track-print skirt), the SOUND HALF-TRACK (giant speaker horn, disc turntable), the cargo truck, the bulldozer with its track-mark beam.
// Story events come from places.<name>.events (frames). Real models (CC-BY, Sketchfab via Asset Hub) come in through places.<name>.assets.
export async function build(THREE, scene, film, ctx) {   /* V3: async, the inflatable decoy is a Blender GLB */
  const { B2T, toon } = ctx, P = ctx.place || {}, Z = P.zone || 'field', EV = P.events || {};
  const V = (x, y, z) => B2T([x, y, z]), n = {};
  let seed = 4417 + Z.length * 31; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647, rr = (a, b) => a + rnd() * (b - a);
  const add = (m, name, role, o = {}) => { n[name] = (n[name] || 0) + 1; m.name = n[name] > 1 ? `${name}_${String(n[name]).padStart(2, '0')}` : name; m.userData.role = role; if (o.mat) m.userData.mat = o.mat; m.castShadow = o.cast ?? true; m.receiveShadow = o.receive ?? true; (o.parent || scene).add(m); return m; };
  const relief = (kind, col, o = {}) => ctx.relief ? ctx.relief(kind, col, o) : toon(col);
  const metal = (kind, col, o = {}) => ctx.pbr ? ctx.pbr.metal(kind, { color: col, ...o }) : toon(col);
  const std = (col, o = {}) => new THREE.MeshStandardMaterial({ color: col, roughness: o.rough ?? .8, metalness: o.metal ?? 0, ...(o.extra || {}) });
  const basic = (col, o = {}) => new THREE.MeshBasicMaterial({ color: col, ...o });
  const box = (name, role, w, d, h, at, mat, o = {}) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat), name, role, o); m.position.copy(V(at[0], at[1], at[2] + h / 2)); if (o.rot) m.rotation.y = o.rot; return m; };
  const cyl = (name, role, r, h, at, mat, o = {}) => { const m = add(new THREE.Mesh(new THREE.CylinderGeometry(o.r2 ?? r, r, h, o.seg ?? 20), mat), name, role, o); m.position.copy(V(at[0], at[1], at[2] + h / 2)); return m; };
  const canvasTex = (w, h, draw) => { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const glowTex = canvasTex(128, 128, (g, w) => { const r = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.3, 'rgba(255,255,255,.5)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, w); });
  const glow = (col, size, op, at, parent = scene) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); s.scale.setScalar(size); s.position.copy(at); s.userData.noExport = true; parent.add(s); return s; };
  const ups = [];   // per-frame updates
  const sm = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);

  // ======================= HERO: THE INFLATABLE SHERMAN =======================
  // Rubberised canvas: olive, satin sheen, faint wrinkle normal; seams along every edge; a brass valve on the rear deck; a patch; white star.
  const rubberTex = canvasTex(256, 256, (g, w) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, w); for (let i = 0; i < 60; i++) { g.strokeStyle = `rgba(${rnd() < .5 ? '255,255,255' : '0,0,0'},.18)`; g.lineWidth = rr(1, 4); g.beginPath(); const x = rr(0, w), y = rr(0, w); g.moveTo(x, y); g.bezierCurveTo(x + rr(-60, 60), y + rr(-20, 20), x + rr(-60, 60), y + rr(-20, 20), x + rr(-90, 90), y + rr(-30, 30)); g.stroke(); } });
  rubberTex.wrapS = rubberTex.wrapT = THREE.RepeatWrapping; rubberTex.colorSpace = THREE.NoColorSpace;
  const rubber = (col) => new THREE.MeshStandardMaterial({ name: 'rubber_canvas', color: col, roughness: .55, metalness: 0, bumpMap: rubberTex, bumpScale: .6 });
  const starTex = canvasTex(256, 256, (g, w) => { g.clearRect(0, 0, w, w); g.fillStyle = '#f2efe4'; g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? w * .19 : w * .46; g.lineTo(w / 2 + Math.cos(a) * r, w / 2 + Math.sin(a) * r); } g.closePath(); g.fill(); g.lineWidth = 10; g.strokeStyle = '#f2efe4'; g.beginPath(); g.arc(w / 2, w / 2, w * .47, 0, 7); g.stroke(); });
  const treadTex = canvasTex(64, 512, (g, w, h) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 16) { g.fillStyle = '#d0d0d0'; g.fillRect(0, y, w, 7); g.fillStyle = '#404040'; g.fillRect(0, y + 7, w, 2); } });
  treadTex.wrapS = treadTex.wrapT = THREE.RepeatWrapping; treadTex.repeat.set(6, 1); treadTex.colorSpace = THREE.NoColorSpace;
  const stencilTex = ['3A-27', 'USA 30117', '6-B-41', 'W-3088'].map(txt => canvasTex(256, 74, (g, w, h) => { g.clearRect(0, 0, w, h); g.fillStyle = 'rgba(236,232,214,.92)'; g.font = 'bold 44px monospace'; g.textAlign = 'center'; g.fillText(txt, w / 2, 54); }));
  /* ---- V3 step 1 (2026-11-18): the INFLATABLE DECOY is a custom Blender model, not a primitive assembly.
     Source: library/assets/custom/inflatable_tank/build_inflatable_tank.py -> episodes/ghost-army/assets/inflatable_tank.glb (hero, close-ups)
     and inflatable_tank_lod.glb (rows of decoys). Bladders, sewn seams, tread tie-seams, wheel cushions, brass valves, stitched patches,
     webbing straps, lift loops, a sausage-segment gun. A fictional film prop. The procedural build below stays for the REAL tanks only. */
  const GLB = {};
  { const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js'), L = new GLTFLoader();
    for (const k of ['inflatable_tank', 'inflatable_tank_lod', 'crawler_dozer', 'sound_halftrack', 'field_radio', 'morse_key', 'light_table']) GLB[k] = (await L.loadAsync(new URL('../assets/' + k + '.glb', import.meta.url).href)).scene; }
  const TRK = new THREE.MeshStandardMaterial({ name: 'rubber_canvas', color: '#34352e', roughness: .8, bumpMap: treadTex, bumpScale: 1.2 });
  const BRASS = metal('brass', '#d8b25a', { rough: .25 });
  const ray = new THREE.Raycaster();
  function inflatable(name, opts = {}) {
    const hero = /^(inflatable_sherman|deflated_skin)$/.test(name) || opts.hero;
    const g = new THREE.Group(); g.name = name; const body = GLB[hero ? 'inflatable_tank' : 'inflatable_tank_lod'].clone(true); body.name = name + '_model'; g.add(body);
    const VR = opts.vary ?? Math.abs(Math.sin((opts.at ? opts.at[0] * 12.9 + opts.at[1] * 78.2 : 1) * 43758.5)) % 1;
    const col = new THREE.Color(opts.col || '#5d6538'); if (!opts.col) col.offsetHSL((VR - .5) * .03, (VR - .5) * .1, (VR - .5) * .08);
    const M = rubber(col), MD = rubber(col.clone().multiplyScalar(.74)), MP = rubber(col.clone().offsetHSL(.015, .05, .06));
    body.traverse(o => { if (!o.isMesh) return; const k = o.material.name;
      o.material = k === 'rubber_body' ? M : k === 'rubber_dark' ? MD : k === 'rubber_track' ? TRK : k === 'patch' ? MP : k === 'brass' ? BRASS : o.material;   /* V3.1: GLB metals had no env map and rendered near black */
      o.userData.role = 'cloth'; o.userData.mat = 'rubber'; o.castShadow = opts.cast ?? true; o.receiveShadow = true; });
    const turret = body.getObjectByName('turret'), gun = body.getObjectByName('gun_pivot'), valve = body.getObjectByName('valve_main');
    const hull = body.getObjectByName('hull_bladder'); body.updateMatrixWorld(true);
    // painted markings, laid on the real surface with a ray (they follow the inflated bulge)
    const decal = (tex, w, h, from, dir, nm) => { ray.set(new THREE.Vector3(...from), new THREE.Vector3(...dir).normalize()); const hit = ray.intersectObject(hull, false)[0]; if (!hit) return null;
      const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ map: tex, color: '#d6d0bc', transparent: true, alphaTest: .4, roughness: .75, polygonOffset: true, polygonOffsetFactor: -4 })), nm, 'cloth', { parent: g, cast: false });   /* painted off-white, never bloom-hot */
      const nrm = hit.face.normal.clone().transformDirection(hull.matrixWorld); m.position.copy(hit.point).addScaledVector(nrm, .012); m.lookAt(hit.point.clone().addScaledVector(nrm, 1)); return m; };
    for (const s of [-1, 1]) decal(starTex, .8, .8, [-.75, 1.42, s * 3], [0, 0, -s], 'tank_star');
    decal(stencilTex[Math.floor(VR * stencilTex.length) % stencilTex.length], .9, .26, [5, 1.3, -.45], [-1, -.35, 0], 'tank_stencil');
    if (turret) turret.rotation.y = (VR - .5) * .25;
    const t0 = turret ? turret.scale.clone() : null;
    g.userData.droop = 0; g.userData.sag = 0;
    g.userData.set = (droop = 0, sag = 0) => { if (gun) gun.rotation.z = -droop * .9; g.scale.y = (opts.scale || 1) * (1 - .45 * sag); if (turret) { turret.scale.set(t0.x * (1 + .06 * sag), t0.y * (1 - .4 * sag), t0.z * (1 + .06 * sag)); } };
    g.userData.valve = valve; g.userData.gun = gun; g.userData.barrel = gun;
    if (opts.at) g.position.copy(V(...opts.at)); g.rotation.y = opts.rot || 0; if (opts.scale) g.scale.setScalar(opts.scale);
    (opts.parent || scene).add(g); return g;
  }
  /* ---- V3 step 2 (2026-11-18): a decoy FIELD, not a grid of clones. Rows that bend and break, every balloon with its own
     tint, size, heading and inflation (some still soft, one half collapsed), camouflage nets thrown over a few, unit pennants
     on poles at the row ends, flapping in the wind. Same model, so the camp still reads as one unit's work. */
  const DECOY_TINTS = ['#5d6538', '#535a33', '#646b3e', '#5a5a3a', '#4f5a36', '#666a40'];
  const netTex = canvasTex(256, 256, (g, w) => { g.clearRect(0, 0, w, w); g.strokeStyle = 'rgba(40,46,28,.95)'; g.lineWidth = 3;
    for (let i = -w; i < 2 * w; i += 22) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + w, w); g.stroke(); g.beginPath(); g.moveTo(i, w); g.lineTo(i + w, 0); g.stroke(); }
    for (let i = 0; i < 150; i++) { g.fillStyle = ['#4b5a2c', '#6b6a3a', '#3c4a26', '#7a6e44'][i % 4]; g.beginPath(); g.ellipse(rr(0, w), rr(0, w), rr(4, 11), rr(2, 6), rr(0, 3), 0, 7); g.fill(); } });
  netTex.wrapS = netTex.wrapT = THREE.RepeatWrapping; netTex.repeat.set(3, 2);
  const netMat = new THREE.MeshStandardMaterial({ map: netTex, alphaTest: .35, transparent: true, side: THREE.DoubleSide, roughness: .95 });
  function camoNet(t) {   /* a net draped over one decoy: high on the turret, sagging to pegs on the ground */
    const geo = new THREE.PlaneGeometry(8.4, 5.6, 28, 20), q = geo.attributes.position;
    for (let i = 0; i < q.count; i++) { const x = q.getX(i), y = q.getY(i); q.setZ(i, Math.max(.04, 3.0 * Math.exp(-(x * x / 9 + y * y / 3.2)) + .12 * Math.sin(x * 2.1 + y * 1.3))); }
    geo.computeVertexNormals(); const m = add(new THREE.Mesh(geo, netMat), 'camo_net', 'cloth', { cast: true });
    m.rotation.x = -Math.PI / 2; m.position.copy(t.position); m.rotation.z = t.rotation.y; m.position.y += .02; return m; }
  const pennants = [];
  function pennant(at, col, col2) {
    const pole = cyl('pennant_pole', 'wood', .035, 4.2, [at[0], at[1], 2.1], std('#6b5a3c', { rough: .9 }));
    const geo = new THREE.PlaneGeometry(1.2, .55, 10, 3), q = geo.attributes.position;
    for (let i = 0; i < q.count; i++) { const x = q.getX(i) + .6; q.setY(i, q.getY(i) * (1 - x / 1.25)); q.setX(i, x); }
    const tex = canvasTex(64, 32, (g, w, h) => { g.fillStyle = col; g.fillRect(0, 0, w, h); g.fillStyle = col2; g.fillRect(0, h * .38, w, h * .24); });
    const fl = add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: .85 })), 'unit_pennant', 'cloth', { cast: true });
    fl.position.copy(V(at[0], at[1], 3.95)); fl.userData.b = geo.attributes.position.array.slice(); pennants.push(fl); return fl; }
  ups.push((f) => { for (const fl of pennants) { const q = fl.geometry.attributes.position, b = fl.userData.b; for (let i = 0; i < q.count; i++) { const x = b[i * 3]; q.setZ(i, .09 * x * Math.sin(x * 4 - f * .32 + fl.id)); } q.needsUpdate = true; } });
  function decoyField(name, x0, y0, cols, rowsN, dx, dy, opts = {}) {
    const out = [], fixed = opts.fixed || [];   /* fixed: [x, y, rot] decoys a camera station is built on (e.g. the 'up close' insert) */
    for (const [fx, fy, fr] of fixed) { const t = sherman(name, { at: [fx, fy, 0], rot: fr, col: DECOY_TINTS[0], vary: .5 }); t.userData.s0 = 1; t.userData.sagV = 0; out.push(t); }
    for (let r = 0; r < rowsN; r++) { const bend = rr(-1.2, 1.2), shift = rr(-2, 2);
      for (let c = 0; c < cols; c++) { if (rnd() < (opts.gaps ?? .08)) continue;
        const x = x0 + c * dx + shift + rr(-1.1, 1.1), y = y0 + r * dy + bend * Math.sin(c * .9 + r) + rr(-1.3, 1.3);
        if (fixed.some(([fx, fy]) => Math.hypot(x - fx, y - fy) < 5.5)) continue;
        const odd = rnd() < .12, k = rnd();
        const t = sherman(name, { at: [x, y, 0], rot: (odd ? Math.PI / 2 + rr(-.3, .3) : rr(-.45, .45)) + (opts.rot0 || 0), col: DECOY_TINTS[Math.floor(rnd() * DECOY_TINTS.length)], vary: rnd() });
        const s0 = rr(.9, 1.07); t.scale.setScalar(s0); t.userData.s0 = s0;
        const sag = k < .62 ? rr(0, .08) : k < .85 ? rr(.18, .4) : k < .95 ? rr(.5, .65) : .78; t.userData.sagV = sag;
        t.userData.set(sag > .7 ? .9 : sag > .45 ? .35 : 0, sag); t.scale.x = t.scale.z = s0; t.scale.y *= s0;
        out.push(t); }
      if (opts.pennants !== false && r % 2 === 0) pennant([x0 - dx * .8, y0 + r * dy], ['#b8312a', '#e0c23a', '#2a5ca8'][r % 3], '#f2efe4'); }
    const nets = opts.nets ?? 2; for (let i = 0; i < nets && out.length; i++) camoNet(out[Math.floor(rr(0, out.length))]);
    return out; }
  function sherman(name, opts = {}) { return name === 'real_tank' || opts.real ? shermanCode(name, opts) : inflatable(name, opts); }
  function shermanCode(name, opts = {}) {
    const g = new THREE.Group(); g.name = name; const col = opts.col || '#5d6538', M = rubber(col), MD = rubber(new THREE.Color(col).multiplyScalar(.72).getStyle()), MT = rubber('#3a3b34');
    const part = (nm, geo, mat, x, y, z, o = {}) => { const m = add(new THREE.Mesh(geo, mat), nm, 'cloth', { parent: g, mat: 'rubber', cast: opts.cast ?? true }); m.position.set(x, y, z); if (o.rx) m.rotation.x = o.rx; if (o.rz) m.rotation.z = o.rz; if (o.ry) m.rotation.y = o.ry; return m; };
    const rbox = (w, h, d, r = .12) => { const s = new THREE.Shape(), x = -w / 2, y = -h / 2; s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h); s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); const geo = new THREE.ExtrudeGeometry(s, { depth: d, bevelEnabled: true, bevelSize: .06, bevelThickness: .06, bevelSegments: 3, curveSegments: 6 }); geo.translate(0, 0, -d / 2); return geo; };
    // tracks + road wheels (the "tracks" are a printed rubber skirt: the wheels are painted discs)
    for (const s of [-1, 1]) { part('tank_track', rbox(5.6, .95, .55, .42), MT, 0, .5, s * 1.18); for (let i = 0; i < 6; i++) { const w = part('tank_wheel', new THREE.CylinderGeometry(.3, .3, .06, 20), MD, -2.0 + i * .8, .42, s * 1.47, { rx: Math.PI / 2 }); } }
    // hull: sloped front glacis, flat deck
    const hull = new THREE.Shape(); hull.moveTo(-2.7, 0); hull.lineTo(2.2, 0); hull.lineTo(2.9, .55); hull.lineTo(1.6, 1.25); hull.lineTo(-2.6, 1.25); hull.lineTo(-2.85, .7); hull.closePath();
    const hg = new THREE.ExtrudeGeometry(hull, { depth: 2.3, bevelEnabled: true, bevelSize: .09, bevelThickness: .09, bevelSegments: 3 }); hg.translate(0, 0, -1.15);
    const hm = part('tank_hull', hg, M, 0, .75, 0);
    const turret = part('tank_turret', new THREE.SphereGeometry(1.0, 28, 14, 0, Math.PI * 2, 0, Math.PI * .55), M, -.35, 1.95, 0); turret.scale.set(1.25, .85, 1.0);
    part('tank_turret_ring', new THREE.CylinderGeometry(1.15, 1.2, .18, 28), MD, -.35, 2.0, 0);
    part('tank_hatch', new THREE.CylinderGeometry(.32, .34, .12, 18), MD, -.75, 2.78, .3);
    const gun = new THREE.Group(); gun.position.set(.55, 2.25, 0); g.add(gun); gun.name = 'tank_gun_pivot';
    const barrel = add(new THREE.Mesh(new THREE.CylinderGeometry(.11, .13, 3.2, 14), M), 'tank_gun', 'cloth', { parent: gun, mat: 'rubber' }); barrel.rotation.z = -Math.PI / 2; barrel.position.x = 1.6;
    add(new THREE.Mesh(new THREE.CylinderGeometry(.25, .25, .5, 16), MD), 'tank_mantlet', 'cloth', { parent: gun }).rotation.z = -Math.PI / 2;
    // the giveaways for close-ups: brass valve, a patch, white stars, seams
    const valve = part('tank_valve', new THREE.CylinderGeometry(.07, .09, .22, 12), metal('brass', '#c8a24a', { rough: .3 }), -2.2, 2.12, -.6);
    part('tank_patch', new THREE.CircleGeometry(.28, 18), rubber('#6c7444'), -1.4, 1.45, 1.21);
    // star decal (v1 note: half buried in the track skirt): smaller, higher, on the flat hull side, alpha-cut so it never smears
    for (const s of [-1, 1]) { const st = add(new THREE.Mesh(new THREE.PlaneGeometry(.78, .78), new THREE.MeshBasicMaterial({ map: starTex, transparent: true, alphaTest: .4, polygonOffset: true, polygonOffsetFactor: -4 })), 'tank_star', 'cloth', { parent: g, cast: false }); st.position.set(-.8, 1.55, s * 1.265); if (s < 0) st.rotation.y = Math.PI; }
    // ---- detail pass (v1 notes 1 + 4): running gear, fenders, stowage, lights, hull MG, deck grille, antenna, stencils; per-tank variation ----
    const VR = opts.vary ?? Math.abs(Math.sin((opts.at ? opts.at[0] * 12.9 + opts.at[1] * 78.2 : 1) * 43758.5)) % 1;   // 0..1, stable per tank
    const TR = new THREE.MeshStandardMaterial({ name: 'rubber_canvas', color: '#34352e', roughness: .8, bumpMap: treadTex, bumpScale: 1.2 });
    for (const s of [-1, 1]) { if (s < 0) g.children.filter(o => /^tank_track/.test(o.name)).forEach(o => { o.material = TR; });
      part('tank_sprocket', new THREE.CylinderGeometry(.42, .42, .14, 12), MD, 2.45, .62, s * 1.47, { rx: Math.PI / 2 }); part('tank_idler', new THREE.CylinderGeometry(.36, .36, .12, 18), MD, -2.45, .55, s * 1.47, { rx: Math.PI / 2 });
      for (let i = 0; i < 3; i++) part('tank_return_roller', new THREE.CylinderGeometry(.11, .11, .1, 12), MT, -1.3 + i * 1.3, .99, s * 1.47, { rx: Math.PI / 2 });
      for (let i = 0; i < 3; i++) part('tank_bogie_arm', new THREE.BoxGeometry(.75, .16, .08), MD, -1.6 + i * 1.6, .55, s * 1.51);
      part('tank_fender', new THREE.BoxGeometry(5.5, .05, .42), MD, 0, 1.03, s * 1.36);
      if (VR > .25 || s > 0) part('tank_stowage_box', new THREE.BoxGeometry(.7, .32, .34), M, -2.2 + VR * .3, 1.22, s * 1.36);
      if (VR > .55) part('tank_bedroll', new THREE.CylinderGeometry(.14, .14, .9, 12), rubber('#6a6448'), 1.2, 1.2, s * 1.33, { rz: Math.PI / 2 }); }
    for (const z of [-.75, .75]) { part('tank_headlight', new THREE.CylinderGeometry(.09, .1, .14, 14), metal('steel', '#9a9c94', { rough: .4 }), 2.55, 1.45, z, { rz: Math.PI / 2 }); part('tank_light_guard', new THREE.TorusGeometry(.13, .015, 6, 14, Math.PI), MD, 2.6, 1.5, z, { ry: Math.PI / 2 }); }
    part('tank_hull_mg', new THREE.CylinderGeometry(.04, .05, .5, 8), MD, 2.62, 1.55, .45, { rz: -Math.PI / 2 - .5 }); part('tank_mg_ball', new THREE.SphereGeometry(.12, 12, 8), MD, 2.45, 1.45, .45);
    for (let i = 0; i < 5; i++) part('tank_spare_track', new THREE.BoxGeometry(.12, .05, .38), TR, 2.15 - i * .02, 1.78 - i * .0, -.55 + i * .27, { rz: -.55 });
    for (let i = 0; i < 7; i++) part('tank_deck_grille', new THREE.BoxGeometry(.05, .03, 1.5), MD, -2.45 + i * .14, 2.02, 0);
    for (const z of [-.6, .6]) part('tank_tow_hook', new THREE.TorusGeometry(.09, .025, 6, 12), MD, 2.92, .9, z);
    part('tank_periscope', new THREE.BoxGeometry(.18, .12, .1), MD, .2, 2.62, -.45); part('tank_cupola', new THREE.CylinderGeometry(.36, .4, .22, 16), M, -.75, 2.66, .3);
    for (const z of [-.7, .7]) part('tank_lift_ring', new THREE.TorusGeometry(.07, .02, 6, 10), MD, -.35, 2.42, z, { rx: Math.PI / 2 });
    const ant = part('tank_antenna', new THREE.CylinderGeometry(.012, .02, 1.6 + VR * 1.2, 5), std('#2a2a24'), -1.3, 2.8 + (.8 + VR * .6), -.55); ant.rotation.z = -.08 - VR * .1;
    const stc = add(new THREE.Mesh(new THREE.PlaneGeometry(.9, .26), new THREE.MeshBasicMaterial({ map: stencilTex[Math.floor(VR * stencilTex.length) % stencilTex.length], transparent: true, alphaTest: .4, polygonOffset: true, polygonOffsetFactor: -4 })), 'tank_stencil', 'cloth', { parent: g, cast: false });
    stc.position.set(2.62, 1.2, -.35); stc.rotation.y = Math.PI / 2; stc.rotation.x = 0; stc.rotation.z = 0; stc.rotateX(-.66);
    // variation: tint, slight turret traverse, barrel angle
    if (!opts.col) { const c = new THREE.Color('#5d6538').offsetHSL((VR - .5) * .02, (VR - .5) * .08, (VR - .5) * .06); M.color.copy(c); }
    turret.rotation.y = (VR - .5) * .25;
    const sx = add(new THREE.Mesh(new THREE.TorusGeometry(.62, .02, 6, 40), rubber('#454a2c')), 'tank_seam', 'cloth', { parent: g, cast: false }); sx.position.set(-.35, 2.15, 0); sx.rotation.x = Math.PI / 2;
    g.userData.droop = 0; g.userData.sag = 0;
    g.userData.set = (droop = 0, sag = 0) => { gun.rotation.z = -droop * .9; g.scale.y = 1 - .45 * sag; turret.scale.y = .85 * (1 - .4 * sag); };
    g.userData.valve = valve; g.userData.gun = gun; g.userData.barrel = barrel;
    if (opts.at) g.position.copy(V(...opts.at)); g.rotation.y = opts.rot || 0; if (opts.scale) g.scale.setScalar(opts.scale);
    (opts.parent || scene).add(g); return g;
  }

  // ======================= HERO: THE SOUND HALF-TRACK =======================
  function halftrack(name, at, rot = 0) {
    const g = new THREE.Group(); g.name = name; g.position.copy(V(...at)); g.rotation.y = rot; scene.add(g);
    const OD = metal('iron', '#4d5634', { rough: .7, rust: .15 }), DARK = std('#22241e', { rough: .9 }), TYRE = std('#1c1c1c', { rough: .95 });
    const p = (nm, geo, mat, x, y, z, o = {}) => { const m = add(new THREE.Mesh(geo, mat), nm, 'metal', { parent: g, mat: 'painted_metal_chipped' }); m.position.set(x, y, z); if (o.rx) m.rotation.x = o.rx; if (o.rz) m.rotation.z = o.rz; return m; };
    /* V3 (2026-11-18): the vehicle itself is a custom Blender model (library/assets/custom/sound_halftrack/build_sound_halftrack.py): treaded front tyres,
       armoured radiator shutters, panelled hood, fenders with headlights and brush guards, open armoured cab, windshield armour with vision slits,
       bed with racks and jerry cans, rubber band tracks with chevron cleats on two bogies. A sound truck: no weapon. The horn rig below stays in code (animated). */
    { const body = GLB.sound_halftrack.clone(true); body.name = name + '_model'; g.add(body);
      const MAT = { paint: OD, paint_dark: metal('iron', '#3e452a', { rough: .75, rust: .2 }), steel_dark: metal('iron', '#2e302a', { rough: .5 }), rubber: TYRE, chrome: metal('steel', '#c8c8c0', { rough: .3 }), wood: relief('wood', '#7a6444', { seed: 14 }) };
      body.traverse(o => { if (!o.isMesh) return; const m = MAT[o.material.name]; if (m) o.material = m; o.userData.role = 'metal'; o.userData.mat = 'painted_metal_chipped'; o.castShadow = true; o.receiveShadow = true; }); }
    // the giant speaker: a horn on a frame over the bed + the disc turntable and cables
    const prof = []; for (let i = 0; i <= 24; i++) { const y = i / 24 * 1.7; prof.push(new THREE.Vector2(.2 + .82 * Math.pow(y / 1.7, 2.6), y - .85)); }
    const HM = metal('steel', '#a3a99c', { rough: .42, finish: 'brushed' }); HM.side = THREE.DoubleSide;
    const horn = p('ht_speaker_horn', new THREE.LatheGeometry(prof, 48), HM, -1.15, 2.8, 0, { rz: -Math.PI / 2 });
    for (const [k, r] of [[.25, .27], [.5, .36], [.75, .56]]) p('ht_horn_rib', new THREE.TorusGeometry(r + .02, .025, 8, 40), OD, -1.15 - .85 + k * 1.7, 2.8, 0).rotation.y = Math.PI / 2;
    p('ht_horn_rim', new THREE.TorusGeometry(1.03, .05, 10, 48), OD, -1.15 + .85, 2.8, 0).rotation.y = Math.PI / 2;
    const throat = p('ht_horn_throat', new THREE.CircleGeometry(.95, 40), std('#121410', { rough: 1 }), -1.15 + .5, 2.8, 0); throat.rotation.y = Math.PI / 2;   // dark inside of the bell
    p('ht_speaker_driver', new THREE.CylinderGeometry(.3, .34, .55, 20), OD, -2.25, 2.8, 0, { rz: -Math.PI / 2 }); p('ht_driver_cap', new THREE.SphereGeometry(.3, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), OD, -2.52, 2.8, 0, { rz: Math.PI / 2 });
    for (const z of [-.45, .45]) p('ht_speaker_frame', new THREE.BoxGeometry(.1, 1.35, .1), OD, -1.7, 1.73, z);   /* V3: posts stand on the new bed floor (z 1.05) */ p('ht_speaker_cradle', new THREE.BoxGeometry(1.4, .1, 1.0), OD, -1.6, 2.4, 0);
    const cab = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(-2.5, 2.8, .2), new THREE.Vector3(-2.6, 2.0, .6), new THREE.Vector3(-1.4, 1.8, .7), new THREE.Vector3(-.4, 1.25, -.4)]), 24, .03, 6), DARK); add(cab, 'ht_speaker_cable', 'rubber', { parent: g });
    // armoured body detail: bed sides, fenders, headlights, winch roller, a "SONIC" crate
    const sc = p('ht_sonic_crate', new THREE.BoxGeometry(.8, .5, .6), relief('wood', '#7a6444', { seed: 13 }), -2.0, 1.3, .55);
    const disc = p('ht_disc', new THREE.CylinderGeometry(.42, .42, .02, 32), std('#111111', { rough: .3 }), -.6, 1.6, -.5); p('ht_turntable', new THREE.BoxGeometry(.9, .5, .8), relief('wood', '#5a4636', { seed: 15 }), -.6, 1.3, -.5);   /* V3: a turntable cabinet on the bed floor */
    g.userData.disc = disc; g.userData.horn = horn; return g;
  }

  // ======================= the cargo truck (the hook) =======================
  function cargoTruck(name, at, rot = 0) {
    const g = new THREE.Group(); g.name = name; g.position.copy(V(...at)); g.rotation.y = rot; scene.add(g);
    const OD = metal('iron', '#545c38', { rough: .75 }), TYRE = std('#1c1c1c', { rough: .95 }), WOOD = relief('wood', '#7a6a4a', { seed: 12 });
    const p = (nm, geo, mat, x, y, z, o = {}) => { const m = add(new THREE.Mesh(geo, mat), nm, 'metal', { parent: g }); m.position.set(x, y, z); if (o.rx) m.rotation.x = o.rx; return m; };
    p('truck_bed', new THREE.BoxGeometry(4.6, .25, 2.3), WOOD, -.9, 1.2, 0); p('truck_cab', new THREE.BoxGeometry(1.5, 1.4, 2.0), OD, 2.0, 1.8, 0); p('truck_hood', new THREE.BoxGeometry(1.3, .9, 1.7), OD, 3.3, 1.5, 0);
    for (const s of [-1, 1]) { p('truck_side', new THREE.BoxGeometry(4.6, .5, .08), WOOD, -.9, 1.55, s * 1.15); for (const x of [3.2, -.2, -1.6, -3.0]) p('truck_wheel', new THREE.CylinderGeometry(.5, .5, .35, 22), TYRE, x, .5, s * 1.0, { rx: Math.PI / 2 }); }
    return g;
  }
  /* V3 (user request 2026-11-18): the bulldozer is a custom Blender model (library/assets/custom/crawler_dozer/build_crawler_dozer.py):
     a 1940s crawler with real track chains, rollers, louvred hood, radiator, exhaust and air cleaner, open seat and levers, canopy,
     cable-lift A-frame, curved blade, and the toothed beam dragged behind to draw fake tank tracks. Worn olive paint, metal with the sky env. */
  function bulldozer(name, at, rot = 0) {
    const g = new THREE.Group(); g.name = name; g.position.copy(V(...at)); g.rotation.y = rot; scene.add(g);
    const body = GLB.crawler_dozer.clone(true); body.name = name + '_model'; g.add(body);
    const MAT = { paint: metal('iron', '#7d7440', { rough: .62, rust: .12 }), paint_worn: metal('iron', '#6a6236', { rough: .72, rust: .25 }), steel_dark: metal('iron', '#3a3a36', { rough: .5 }),
      track: metal('iron', '#2c2b28', { rough: .7, rust: .3 }), exhaust: metal('iron', '#22201e', { rough: .6, rust: .4 }), rust: metal('iron', '#6a3e24', { rough: .85, rust: .8 }) };
    body.traverse(o => { if (!o.isMesh) return; const m = MAT[o.material.name]; if (m) o.material = m; o.userData.role = 'metal'; o.userData.mat = 'painted_metal'; o.castShadow = true; o.receiveShadow = true; });
    return g;
  }
  // a printed track-mark strip on the ground (the fake tracks that fool the photos)
  const trackTex = canvasTex(64, 256, (g, w, h) => { g.fillStyle = 'rgba(0,0,0,0)'; g.clearRect(0, 0, w, h); for (let y = 0; y < h; y += 16) { g.fillStyle = 'rgba(40,30,20,.55)'; g.fillRect(4, y, w - 8, 9); } });
  trackTex.wrapT = THREE.RepeatWrapping;
  const trackMarks = (name, from, to, gauge = 1.18) => { const dx = to[0] - from[0], dy = to[1] - from[1], L = Math.hypot(dx, dy), a = Math.atan2(dx, dy); const t = trackTex.clone(); t.needsUpdate = true; t.repeat.set(1, L / 1.2);
    for (const s of [-1, 1]) { const m = add(new THREE.Mesh(new THREE.PlaneGeometry(.55, L), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2 })), name, 'ground', { cast: false });
      m.rotation.x = -Math.PI / 2; m.rotation.z = -a; const cx = (from[0] + to[0]) / 2 + Math.cos(a) * s * gauge, cy = (from[1] + to[1]) / 2 - Math.sin(a) * s * gauge; m.position.copy(V(cx, cy, .02)); } };

  // ======================= shared outdoor pieces =======================
  const ground = (col, kind = 'grass', size = 400, o = {}) => { const geo = new THREE.PlaneGeometry(size, size, 200, 200), gp = geo.attributes.position, cols = new Float32Array(gp.count * 3), C0 = new THREE.Color(col), C = new THREE.Color();
    const nz = (x, y) => Math.sin(x * .071 + Math.sin(y * .043) * 2.1) * Math.cos(y * .067 - Math.sin(x * .037) * 1.7) * .5 + Math.sin(x * .19 + y * .23) * .25 + Math.sin(x * .53 - y * .41) * .12;
    for (let i = 0; i < gp.count; i++) { const x = gp.getX(i), y = -gp.getY(i), k = nz(x, y), far = Math.min(1, Math.max(0, (Math.hypot(x, y) - 22) / 30));
      gp.setZ(i, o.roll ? o.roll * far * (nz(x * .5, y * .5) + .3) : 0);   // optional soft undulation (off: roads, water and props sit on z 0)
      const k2 = nz(x * 3.1 + 17, y * 2.7 - 9); C.copy(C0).offsetHSL(.012 * k, .05 * k, .09 * k + .05 * k2 + (o.dry ? .03 * Math.sin(x * .9) * Math.sin(y * 1.1) : 0)); cols[i * 3] = C.r / C0.r; cols[i * 3 + 1] = C.g / C0.g; cols[i * 3 + 2] = C.b / C0.b; }
    geo.setAttribute('color', new THREE.BufferAttribute(cols, 3)); geo.computeVertexNormals();
    const mat = relief(kind, col, { seed: 21, size: o.tile || 9 }); mat.vertexColors = true; mat.needsUpdate = true;
    const m = add(new THREE.Mesh(geo, mat), 'ground', 'ground', { cast: false, mat: 'turf' }); m.rotation.x = -Math.PI / 2; return m; };
  const leafTex = canvasTex(256, 256, (g, w) => { g.fillStyle = '#7a7a7a'; g.fillRect(0, 0, w, w); for (let i = 0; i < 900; i++) { const x = rr(0, w), y = rr(0, w), r = rr(3, 9), a = rr(0, 6.3); g.fillStyle = `rgb(${rr(90, 230) | 0},${rr(90, 230) | 0},${rr(90, 230) | 0})`; g.beginPath(); g.ellipse(x, y, r, r * .55, a, 0, 6.3); g.fill(); } });
  leafTex.wrapS = leafTex.wrapT = THREE.RepeatWrapping; leafTex.colorSpace = THREE.NoColorSpace;
  const hedge = (name, from, to, h = 2.2) => { const dx = to[0] - from[0], dy = to[1] - from[1], L = Math.hypot(dx, dy); const m = add(new THREE.Mesh(new THREE.BoxGeometry(L, h, 1.6, Math.ceil(L), 3, 2), relief('grass', '#3f5a2c', { seed: 31, size: 2 })), name, 'foliage', { mat: 'foliage' });
    const p = m.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); p.setY(i, y + (y > 0 ? rr(-.25, .35) : 0)); p.setZ(i, p.getZ(i) * rr(.85, 1.2)); } m.geometry.computeVertexNormals();
    m.position.copy(V((from[0] + to[0]) / 2, (from[1] + to[1]) / 2, h / 2)); m.rotation.y = -Math.atan2(dy, dx); m.scale.set(1, .72, .8);
    // bocage: an earth bank under a row of rounded leaf clumps with light and shade (no more box silhouette)
    const n = Math.ceil(L * 2.6), g = new THREE.SphereGeometry(1, 18, 12), gp = g.attributes.position;
    for (let i = 0; i < gp.count; i++) { const k = 1 + .16 * Math.sin(gp.getX(i) * 5.1 + gp.getY(i) * 3.7) * Math.cos(gp.getZ(i) * 4.3) + .07 * Math.sin(gp.getX(i) * 13.0 + gp.getZ(i) * 11.0); gp.setXYZ(i, gp.getX(i) * k, gp.getY(i) * k, gp.getZ(i) * k); } g.computeVertexNormals();
    const im = new THREE.InstancedMesh(g, new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .9, bumpMap: leafTex, bumpScale: 2.5 }), n), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), C = new THREE.Color();
    for (let i = 0; i < n; i++) { const t = (i + rr(-.3, .3)) / n, r = i % 3 ? rr(.7, 1.3) : rr(.35, .6), side = rr(-.55, .55);
      const P = V(from[0] + dx * t - dy / L * side, from[1] + dy * t + dx / L * side, h * rr(.55, .95));
      Q.setFromEuler(new THREE.Euler(rr(0, 6), rr(0, 6), rr(0, 6))); M4.compose(P, Q, new THREE.Vector3(r, r * rr(.75, 1.0), r)); im.setMatrixAt(i, M4);
      im.setColorAt(i, C.set(['#3f6a2a', '#4d7a30', '#5a8a36', '#365c26', '#6a9440', '#7a9a3e', '#2f5222'][(i * 7 + (i >> 2)) % 7]).offsetHSL(rr(-.01, .01), 0, rr(-.04, .04))); }
    im.castShadow = true; im.receiveShadow = true; add(im, name + '_clumps', 'foliage', { mat: 'foliage' }); return m; };
  const tree = (at, h, kind = 'oak', sd = 1) => ctx.trees ? ctx.trees.tree({ kind, at, height: h, seed: sd }) : cyl('tree', 'foliage', .3, h, at, toon('#3a5a2a'));
  const farmhouse = (at, rot = 0) => { const g = new THREE.Group(); g.position.copy(V(...at)); g.rotation.y = rot; scene.add(g); const w = add(new THREE.Mesh(new THREE.BoxGeometry(9, 4.2, 6), relief('stone', '#b8ad96', { seed: 41 })), 'farm_walls', 'stone', { parent: g, mat: 'stone' }); w.position.y = 2.1;
    const r = new THREE.CylinderGeometry(.01, 6.4, 3.0, 4, 1); r.rotateY(Math.PI / 4); const roof = add(new THREE.Mesh(r, relief('tile', '#6a4a3e', { seed: 42 })), 'farm_roof', 'roof', { parent: g, mat: 'roof_tile' }); roof.scale.set(1.0, 1, .7); roof.position.y = 5.7;
    for (const x of [-2.8, 0, 2.8]) { const win = add(new THREE.Mesh(new THREE.BoxGeometry(.9, 1.1, .1), std('#3a4a5a', { rough: .3 })), 'farm_window', 'glass', { parent: g }); win.position.set(x, 2.4, 3.02); const sh = add(new THREE.Mesh(new THREE.BoxGeometry(.5, 1.2, .08), relief('wood', '#4f6f5a', { seed: 43 })), 'farm_shutter', 'wood', { parent: g }); sh.position.set(x - .72, 2.4, 3.05); }
    const door = add(new THREE.Mesh(new THREE.BoxGeometry(1.1, 2.1, .12), relief('wood', '#5a3a26', { seed: 44 })), 'farm_door', 'wood', { parent: g }); door.position.set(3.6, 1.05, 3.04); return g; };
  const pole = (at) => { cyl('telegraph_pole', 'wood', .09, 7, at, relief('wood', '#5a4632', { seed: 51 }), { r2: .07 }); box('telegraph_bar', 'wood', 1.4, .1, .1, [at[0], at[1], at[2] + 6.4], relief('wood', '#5a4632', { seed: 52 })); };

  /* ---- V3 step 3 (2026-11-18): exteriors at three scales, after the fortress reference.
     meadow(): dense curved grass clumps up to the lens (5 tapered blades per clump, dark base -> light tip, wind in the vertex shader)
     instead of the kit's thin 3-blade tufts that read as green sticks. farLandscape(): a ring of rolling hills out to 480 m with a
     patchwork of fields in several tints, dark hedgerow lines, copses, farms and a church spire, fading into the place's haze. */
  /* V3.1 (lock fix 2026-11-18): remove instances that fail a plan-space test by packing the kept ones and lowering im.count.
     Zero-scale matrices decompose to NaN rotations, which the glTF exporter wrote into the lock and Blender refused to import. */
  const dropInstances = (im, drop) => { if (!im || !im.isInstancedMesh) return im; const M4 = new THREE.Matrix4(), q = new THREE.Vector3(), C = new THREE.Color(); let k = 0;
    for (let i = 0; i < im.count; i++) { im.getMatrixAt(i, M4); q.setFromMatrixPosition(M4); const x = im.position.x + q.x, y = -(im.position.z + q.z); if (drop(x, y)) continue;
      if (k !== i) { im.setMatrixAt(k, M4); if (im.instanceColor) { im.getColorAt(i, C); im.setColorAt(k, C); } } k++; }
    im.count = k; im.instanceMatrix.needsUpdate = true; if (im.instanceColor) im.instanceColor.needsUpdate = true; return im; };
  const windT = { value: 0 }; ups.push((f) => { windT.value = f / 30; });
  function meadow(o = {}) {
    const blades = o.blades || 5, segs = 3, pos = [], col = [], idx = []; let vi = 0;
    for (let b = 0; b < blades; b++) { const a = b / blades * 6.283 + rr(-.3, .3), r = rr(0, .1), bx = Math.cos(a) * r, bz = Math.sin(a) * r, lean = rr(.08, .3), dir = rr(0, 6.283), w = rr(.018, .03), h = rr(.65, 1);
      for (let k = 0; k <= segs; k++) { const t = k / segs, y = h * t, off = lean * t * t, ww = w * (1 - t * .92), cx = bx + Math.cos(dir) * off, cz = bz + Math.sin(dir) * off, px = -Math.sin(dir) * ww, pz = Math.cos(dir) * ww;
        pos.push(cx - px, y, cz - pz, cx + px, y, cz + pz); const c = new THREE.Color('#2c4a1e').lerp(new THREE.Color('#a4b85e'), Math.pow(t, .8)); col.push(c.r, c.g, c.b, c.r, c.g, c.b);
        if (k) idx.push(vi - 2, vi - 1, vi, vi - 1, vi + 1, vi); vi += 2; } }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); geo.setIndex(idx); geo.computeVertexNormals();
    const mat = new THREE.MeshStandardMaterial({ vertexColors: true, side: THREE.DoubleSide, roughness: .85 });
    mat.onBeforeCompile = sh => { sh.uniforms.uWind = windT; sh.vertexShader = 'uniform float uWind;\n' + sh.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\n#ifdef USE_INSTANCING\n float ph = instanceMatrix[3].x * .37 + instanceMatrix[3].z * .23;\n#else\n float ph = 0.;\n#endif\n transformed.x += sin(uWind * 1.9 + ph) * .07 * position.y * position.y; transformed.z += cos(uWind * 1.3 + ph * 1.7) * .035 * position.y * position.y;'); };
    const n = o.count || 3000, im = new THREE.InstancedMesh(geo, mat, n), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), C = new THREE.Color(), at = o.at || [0, 0, 0];
    const tints = o.tints || ['#ffffff', '#e8f0d0', '#f4e8c0', '#d8e8c8', '#fff4d8'];
    for (let i = 0; i < n; i++) { const a = rr(0, 6.283), r = Math.sqrt(rnd()) * (o.radius || 20), x = at[0] + Math.cos(a) * r, y = at[1] + Math.sin(a) * r, hh = (o.height || .5) * rr(.6, 1.35) * (o.patchy ? (.55 + .9 * Math.abs(Math.sin(x * .21) * Math.cos(y * .17))) : 1);
      Q.setFromEuler(new THREE.Euler(0, rr(0, 6.283), 0)); M4.compose(V(x, y, 0), Q, new THREE.Vector3(rr(.8, 1.3), hh, rr(.8, 1.3))); im.setMatrixAt(i, M4); im.setColorAt(i, C.set(tints[i % tints.length]).multiplyScalar(rr(.82, 1.08))); }
    im.castShadow = false; im.receiveShadow = true; add(im, o.name || 'meadow_grass', 'foliage', { cast: false, mat: 'foliage' }); return im; }
  function farLandscape(o = {}) {
    const r0 = o.r0 || 150, r1 = o.r1 || 480, cx = o.at ? o.at[0] : 0, cy = o.at ? o.at[1] : 0, segA = 220, segR = 60;
    const fields = (o.tints || ['#7a9a46', '#9aa852', '#b8b066', '#6a8a3e', '#c4a65a', '#8aa04a', '#5f7f3a', '#a89a58']).map(c => new THREE.Color(c));
    const hedge = new THREE.Color(o.hedge || '#3a5226'), pos = [], col = [], idx = [], C = new THREE.Color();
    const hill = (x, y) => { const d = Math.hypot(x - cx, y - cy), k = Math.min(1, Math.max(0, (d - r0) / 90)); return k * (9 * Math.sin(x * .011 + 1.3) * Math.cos(y * .009 - .4) + 6 * Math.sin(x * .023 - y * .019) + 14 + (d - r0) * .05 * (.6 + .4 * Math.sin(x * .004 + y * .006))); };
    for (let j = 0; j <= segR; j++) for (let i = 0; i <= segA; i++) {
      const a = i / segA * 6.283, d = r0 + (r1 - r0) * Math.pow(j / segR, 1.35), x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d; const P = V(x, y, hill(x, y)); pos.push(P.x, P.y, P.z);
      const u = x * .028 + Math.sin(y * .011) * 1.6, v = y * .031 + Math.sin(x * .013) * 1.3, fu = u - Math.floor(u), fv = v - Math.floor(v);
      const cell = Math.abs(Math.floor(u) * 73 + Math.floor(v) * 151) % fields.length, edge = Math.min(fu, 1 - fu, fv, 1 - fv) < .07;
      C.copy(edge ? hedge : fields[cell]).offsetHSL(0, 0, .04 * Math.sin(x * .3 + y * .2)); col.push(C.r, C.g, C.b); }
    for (let j = 0; j < segR; j++) for (let i = 0; i < segA; i++) { const a = j * (segA + 1) + i, b = a + 1, c = a + segA + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); geo.setIndex(idx); geo.computeVertexNormals();
    const land = add(new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .95 })), 'far_landscape', 'ground', { cast: false, mat: 'grass' });
    // copses and hedgerow trees: instanced leafy blobs on the hills, two tones
    const tg = new THREE.IcosahedronGeometry(1, 1), tp = tg.attributes.position; for (let i = 0; i < tp.count; i++) { const k = 1 + .14 * Math.sin(tp.getX(i) * 5 + tp.getY(i) * 3) * Math.cos(tp.getZ(i) * 4); tp.setXYZ(i, tp.getX(i) * k, tp.getY(i) * k, tp.getZ(i) * k); } tg.computeVertexNormals();
    const nT = o.trees || 900, tm = new THREE.InstancedMesh(tg, new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .95 }), nT), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion();
    for (let i = 0; i < nT; i++) { const a = rr(0, 6.283), d = rr(r0 + 15, r1 - 40), x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d, cl = i % 9 < 6, s = cl ? rr(3, 6.5) : rr(2.5, 4.5);
      const xx = cl ? x + rr(-12, 12) : x, yy = cl ? y + rr(-12, 12) : y; M4.compose(V(xx, yy, hill(xx, yy) + s * .8), Q.identity(), new THREE.Vector3(s, s * rr(.8, 1.15), s)); tm.setMatrixAt(i, M4); tm.setColorAt(i, C.set(['#3c5a28', '#4a6a2e', '#2f4c22', '#566e34'][i % 4])); }
    add(tm, 'far_copses', 'foliage', { cast: false, mat: 'foliage' });
    // farms with red-brown roofs and one church spire, so the eye finds landmarks
    const wallM = std('#d8cdb2', { rough: .9 }), roofM = std('#7a4a3a', { rough: .85 });
    for (let i = 0; i < (o.farms || 26); i++) { const a = rr(0, 6.283), d = rr(r0 + 20, r1 * .7), x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d, z = hill(x, y), w = rr(7, 13), dd = rr(5, 8), rot = rr(0, 3);
      const g = new THREE.Group(); g.position.copy(V(x, y, z)); g.rotation.y = rot; scene.add(g); g.name = 'far_farm';
      const wall = new THREE.Mesh(new THREE.BoxGeometry(w, 4, dd), wallM); wall.position.y = 2; g.add(wall); const rf = new THREE.Mesh(new THREE.CylinderGeometry(.01, dd * .78, 3, 4, 1), roofM); rf.rotation.y = Math.PI / 4; rf.scale.set(w / dd, 1, 1); rf.position.y = 5.5; g.add(rf); }
    { const a = o.spire ?? .35, d = r0 + 70, x = cx + Math.cos(a) * d, y = cy + Math.sin(a) * d, z = hill(x, y), g = new THREE.Group(); g.position.copy(V(x, y, z)); scene.add(g); g.name = 'far_church';
      const nave = new THREE.Mesh(new THREE.BoxGeometry(16, 8, 8), wallM); nave.position.y = 4; g.add(nave); const tw = new THREE.Mesh(new THREE.BoxGeometry(4.5, 16, 4.5), wallM); tw.position.set(-8, 8, 0); g.add(tw);
      const sp = new THREE.Mesh(new THREE.ConeGeometry(3.4, 11, 8), std('#5a5f66', { rough: .6 })); sp.position.set(-8, 21.5, 0); g.add(sp); }
    return land; }
  // VFX audit: wind per place and light (dawn calm, open camp breezy, night road gusty in the poplars, river wind over the water)
  if (ctx.atmosphere && ctx.atmosphere.setWind) { const WN = { field: [.32, .12], camp: [.5, .2], road: [.62, .3], river: [.7, .3] }[Z]; if (WN) ctx.atmosphere.setWind({ direction: [1, .3], strength: WN[0], gust: WN[1], speed: 1 }); }
  let anchors = {};
  // ============================================================ ZONES ============================================================
  if (Z === 'field' || Z === 'camp') {
    // P1 Normandy bocage at dawn (hook) and P2 the same meadow as the ghost camp (overcast day)
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'clear-day', seed: Z === 'field' ? 11 : 12, coverage: Z === 'field' ? .7 : 1.4 });
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: Z === 'field' ? '#e6d6bc' : '#bcc6cc', near: 70, far: 560 });   /* V3: haze reaches the far landscape progressively (was a wall at 260 m) */
    farLandscape({ at: [0, 20], r0: 160, r1: 470, spire: Z === 'field' ? 1.45 : 1.2 });
    ground('#6f8a46'); const road = add(new THREE.Mesh(new THREE.PlaneGeometry(4.2, 200), relief('mud', '#8a7656', { seed: 61, size: 3 })), 'dirt_road', 'ground', { cast: false, mat: 'mud' }); road.rotation.x = -Math.PI / 2; road.position.copy(V(-7, 40, .01));
    hedge('hedge', [-60, 14], [-9.5, 14]); hedge('hedge', [-4.5, 14], [60, 14]); hedge('hedge', [-9.5, -30], [-9.5, 14]); hedge('hedge', [-4.5, 14], [-4.5, 90]); hedge('hedge', [14, 14], [14, 90]);
    for (const [x, y, h, s] of [[-14, 18, 9, 3], [8, 20, 11, 4], [22, 30, 10, 5], [-26, 34, 12, 6], [4, 46, 9, 7], [-40, 10, 10, 8], [30, 8, 9, 9]]) tree([x, y, 0], h, 'oak', s);
    for (const [x, y] of [[16, 10], [19, 6], [24, 11]]) tree([x, y, 0], 4.5, 'olive', Math.round(x));   // apple orchard stand-ins
    farmhouse([24, 34, 0], -.4); for (let i = 0; i < 6; i++) pole([-4.2, -10 + i * 22, 0]);
    /* V3 (user request): the poles carry their wires - porcelain insulators on each crossarm and three sagging lines from pole to pole, running on past both ends */
    { const INS = std('#e8e4da', { rough: .25 }), WIRE = std('#1c1c1a', { rough: .5 }), xs = [-.55, 0, .55], ys = [-32, -10, 12, 34, 56, 78, 100, 122];
      for (let i = 0; i < 6; i++) for (const dx of xs) cyl('pole_insulator', 'glass', .045, .16, [-4.2 + dx, -10 + i * 22, 6.45], INS, { r2: .03 });
      for (const dx of xs) for (let i = 0; i < ys.length - 1; i++) { const a = V(-4.2 + dx, ys[i], 6.6), c = V(-4.2 + dx, ys[i + 1], 6.6), pts = [];
        for (let k = 0; k <= 24; k++) { const u = k / 24, q = a.clone().lerp(c, u); q.y -= .55 * 4 * u * (1 - u); pts.push(q); }
        add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, .012, 5), WIRE), 'power_line', 'metal', { cast: false }); } }
    const offRoad = (x, y) => Math.abs(x + 7) < 2.8 || Math.hypot(x - 5, y + 3.6) < 4.5 || Math.hypot(x + 3.4, y + 6.6) < 3;   // the dirt road and the lens of the low hook camera stay clear
    const clearBand = (im) => dropInstances(im, (x, y) => offRoad(x, y));   /* V3.1: kept instances are packed and the count lowered (zero-scale ones exported NaN rotations into the lock GLB) */
    if (ctx.detail) { clearBand(meadow({ name: 'meadow_near', at: [2, 4], radius: 20, count: 5200, height: .42, patchy: true })); clearBand(meadow({ name: 'meadow_mid', at: [0, 32], radius: 46, count: 5200, height: .55, patchy: true }));   /* V3 step 3: dense curved grass (was kit tufts reading as sticks) */ clearBand(ctx.detail.rocks({ at: [-6, 8, 0], count: 40, radius: 18, size: .14, seed: 74 })); }
    { const fl = new THREE.InstancedMesh(new THREE.SphereGeometry(.035, 6, 4), new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .8 }), 500), M4 = new THREE.Matrix4(), C = new THREE.Color();   // wild flowers: buttercups, daisies, clover
      for (let i = 0; i < 500; i++) { let a = rr(0, 6.3), r = rr(2, 30); while (offRoad(Math.cos(a) * r, 6 + Math.sin(a) * r)) { a = rr(0, 6.3); r = rr(2, 30); } M4.makeTranslation(...V(Math.cos(a) * r, 6 + Math.sin(a) * r, rr(.12, .3)).toArray()); fl.setMatrixAt(i, M4); fl.setColorAt(i, C.set(['#f2d23a', '#f4f1e6', '#d98ab0', '#f4f1e6'][i % 4])); }
      add(fl, 'wild_flowers', 'foliage', { cast: false }); }
    if (Z === 'field') {
      // the hook: the truck has brought the tank; four GIs lift it off and set it down in the field
      cargoTruck('cargo_truck', [-7, 6, 0], -Math.PI / 2);
      const tk = sherman('inflatable_sherman', { at: [0, 4, 0], rot: -.35 }); const lift = EV.lift || [0, 52], set = EV.set || 103, dent = EV.dent || 110;
      ups.push(f => { const a = sm((f - lift[0]) / (lift[1] - lift[0])), b = sm((f - lift[1]) / (set - lift[1])); tk.position.copy(V(0, 4, 1.55 * (1 - b) + .03 * Math.sin(f * .21) * (1 - b))); tk.rotation.y = -.35;   /* animation audit: the tank stays above its four lifters (it used to slide 3.6 m over static men) and comes down with them; a small bob while held */
        const d = Math.max(0, 1 - Math.abs(f - dent) / 10), dr = sm((f - (EV.deflate || 1e9)) / 18); tk.userData.set(.9 * dr, .12 * d + .25 * dr); });
      /* V3.1 step 11 (interaction with consequence): on 'rubber' the brass valve cap pops off under the air pressure, flies on an arc,
         bounces once in the grass and stays there (aftermath); the steam fx and the valve whistle already land on the same word */
      { const cap = add(new THREE.Mesh(new THREE.CylinderGeometry(.075, .085, .05, 18), metal('brass', '#a8823a', { rough: .5 })), 'valve_cap', 'metal');   /* rougher, darker: facing the lens it must not flare into a glowing ball */ const v0 = new THREE.Vector3(), vel = new THREE.Vector3();
        const t0 = (EV.deflate || 1e9) - 1, G = .0035;   /* a cartoon-slow arc: readable in the macro insert */
        ups.push(f => { const vv = tk.userData.valve; if (!vv) return; vv.updateWorldMatrix(true, false);
          const top = () => { const bb = new THREE.Box3().setFromObject(vv), c = bb.getCenter(new THREE.Vector3()); c.y = bb.max.y + .02; return c; };   /* GLB parts carry the tank origin: use the valve's real geometry */
          if (f < t0) { cap.position.copy(top()); cap.rotation.set(0, 0, 0); return; }
          if (!cap.userData.go) { v0.copy(top()); vel.set(.018, .055, .012); cap.userData.go = true; }
          const k = f - t0; let x = v0.x + vel.x * k, y = v0.y + vel.y * k - .5 * G * k * k, z = v0.z + vel.z * k;
          if (y < .03) { const kl = (vel.y + Math.sqrt(vel.y * vel.y + 2 * G * (v0.y - .03))) / G, b = k - kl, xl = v0.x + vel.x * kl, zl = v0.z + vel.z * kl;   /* one small bounce, then it lies in the grass */
            x = xl + vel.x * .35 * Math.min(b, 14); z = zl + vel.z * .35 * Math.min(b, 14); y = .03 + Math.max(0, .03 * b - .5 * G * b * b); }
          cap.position.set(x, y, z); cap.rotation.x = Math.min(k, 40) * .45; cap.rotation.z = Math.min(k, 40) * .3; }); }
      anchors = { tank: [0, 4, 1.2], truck: [-7, 6, 1.5] };
    } else {
      // the camp: rows of tanks in every state of inflation, compressors, paint pots, the bulldozer drawing track marks
      const rows = decoyField('camp_tank', -13, 12, 4, 3, 8.2, 9, { nets: 2, gaps: .04, fixed: [[-4, 12, .06]] });   /* the 'up close' station is built on the decoy at (-4, 12) */   /* V3 step 2 (was a 3x4 grid of clones) */
      const dz = bulldozer('bulldozer', [12, 2, 0], Math.PI / 2); trackMarks('fake_track_marks', [12, -6], [12, 1]);
      // air compressors (v1 note: plain blocks): a wheeled cart, the tank on top, a motor, a gauge, a hose running to the nearest decoy
      const OD = metal('iron', '#4f5a36', { rough: .6, rust: .2 }), DK = std('#23241f', { rough: .9 }), ST = metal('steel', '#9a9f96', { rough: .35 });
      for (const [x, y] of [[-4, 3], [5, 6], [-9, 8]]) { box('compressor_cart', 'metal', 1.3, .8, .12, [x, y, .32], OD); for (const sx of [-.45, .45]) for (const sy of [-.38, .38]) { const w = cyl('compressor_wheel', 'metal', .22, .1, [x + sx, y + sy, .0], DK); w.rotation.x = Math.PI / 2; w.position.copy(V(x + sx, y + sy, .22)); }
        const tk = cyl('compressor_tank', 'metal', .26, 1.2, [x, y, .7], ST); tk.rotation.z = Math.PI / 2; tk.position.copy(V(x, y, .7));
        box('compressor_motor', 'metal', .45, .5, .4, [x - .35, y, .44], OD); cyl('compressor_flywheel', 'metal', .17, .05, [x - .62, y, .62], DK).rotation.z = Math.PI / 2;
        cyl('compressor_gauge', 'metal', .07, .03, [x + .3, y - .27, .95], metal('brass', '#c8a24a')); box('compressor_stencil', 'cloth', .5, .02, .14, [x, y - .41, .38], basic('#e8e2cc'));
        const hose = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V(x + .6, y, .7), V(x + 1.2, y + .6, .05), V(x + 2.4, y + 2.4, .05), V(x + 3.2, y + 4.6, .5)]), 30, .035, 6), DK); add(hose, 'air_hose', 'rubber'); }
      for (let i = 0; i < 8; i++) { const [px, py] = [rr(-3, 3), rr(-1, 2)], pc = ['#6a7a3a', '#3a3a2a', '#8a6a3a', '#efe6d2'][i % 4]; cyl('paint_pot', 'metal', .16, .3, [px, py, 0], metal('steel', '#a8aaa2', { rough: .4 })); cyl('paint_in_pot', 'cloth', .145, .01, [px, py, .3], std(pc, { rough: .3 })); const hb = new THREE.Mesh(new THREE.TorusGeometry(.16, .008, 4, 16, Math.PI), DK); hb.position.copy(V(px, py, .3)); add(hb, 'pot_handle', 'metal'); }
      // crates and jerrycans: planks, battens, stencils
      const crate = (at, w, d, h, r = 0) => { const g = new THREE.Group(); g.position.copy(V(...at)); g.rotation.y = r; scene.add(g); const W = relief('wood', '#8a7048', { seed: 75 + (at[0] * 3 | 0) }), B = relief('wood', '#6a5434', { seed: 76 });
        const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), W), 'crate', 'wood', { parent: g }); m.position.y = h / 2;
        for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const b = add(new THREE.Mesh(new THREE.BoxGeometry(.06, h + .02, .06), B), 'crate_batten', 'wood', { parent: g }); b.position.set(sx * (w / 2 - .02), h / 2, sz * (d / 2 - .02)); }
        const lb = add(new THREE.Mesh(new THREE.PlaneGeometry(w * .7, h * .35), new THREE.MeshBasicMaterial({ map: stencilTex[(at[0] * 7 | 0) & 3], transparent: true, alphaTest: .4 })), 'crate_stencil', 'cloth', { parent: g, cast: false }); lb.position.set(0, h * .55, d / 2 + .005); return g; };
      crate([2.6, -1.2, 0], .9, .6, .6, .3); crate([2.7, -1.15, .6], .6, .5, .4, .1); crate([-6.2, 5.0, 0], 1.2, .8, .7, -.4); crate([7.4, 4.0, 0], .8, .8, .6, .7);
      for (const [x, y] of [[3.4, -.8], [3.6, -.5], [-6.9, 4.6]]) { box('jerrycan', 'metal', .17, .34, .48, [x, y, 0], metal('iron', '#4a5634', { rough: .55 })); box('jerrycan_handle', 'metal', .04, .2, .06, [x, y, .48], DK); }
      { const TW = relief('wood', '#8a6a46', { seed: 72 }); box('paint_table', 'wood', 2.2, .9, .06, [1.5, -.5, .8], TW); for (const sx of [-1, 1]) for (const sy of [-1, 1]) box('table_leg', 'wood', .07, .07, .8, [1.5 + sx * 1.0, -.5 + sy * .38, 0], TW);
        box('table_stretcher', 'wood', 2.0, .05, .05, [1.5, -.5, .25], TW);
        for (const [x, y, r, c] of [[.9, -.6, .2, '#efe8d6'], [1.3, -.4, -.15, '#e8e0c8'], [2.1, -.55, .4, '#f2ecdc']]) { const sh = box('sketch_sheet', 'cloth', .42, .3, .005, [x, y, .86], std(c, { rough: .9 }), { rot: r }); }
        box('camo_stencil', 'cloth', .6, .45, .01, [1.8, -.35, .87], std('#3f4a2a', { rough: .9 }), { rot: .2 });
        for (let i = 0; i < 4; i++) { const b = cyl('paint_brush', 'wood', .012, .32, [2.3 + i * .05, -.3, .86], relief('wood', '#c8a878', { seed: 77 })); b.rotation.z = Math.PI / 2 - .2; b.position.copy(V(2.3 + i * .06, -.3 + i * .04, .88)); } }
      ups.push((f, t) => { dz.position.copy(V(12, 1 - Math.min(7, Math.max(0, (t - 22) * .6)), 0)); });   // drives toward the camera through the bulldozer line, never wraps
      anchors = { tank: [-4, 12, 1.5], dozer: [12, 2, 1.5] };
    }
  }
  if (Z === 'road') {
    // P3 moonlit country road: ONE half-track, and the sound of a hundred tanks
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'night-storm', seed: 31, coverage: .6, storm: { under: '#2c3a62', underAmt: .12 } })   /* V3 step 5: no orange town-glow under the clouds (read as pink clouds at night) */;
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: '#1e2a48', near: 30, far: 200 });
    ground('#3e5236'); scene.add(new THREE.HemisphereLight('#7a92cc', '#2c3626', 2.4)); { const mk = new THREE.DirectionalLight('#b0c4ff', 2.2); mk.position.copy(V(-30, 60, 40)); mk.target.position.copy(V(0, 10, 0)); mk.castShadow = true; scene.add(mk, mk.target); }
    const road = add(new THREE.Mesh(new THREE.PlaneGeometry(5, 300), relief('cobble', '#7a7466', { seed: 81, size: 2 })), 'road', 'ground', { cast: false, mat: 'cobble' }); road.rotation.x = -Math.PI / 2; road.position.copy(V(0, 60, .01));
    /* V3 step 5: poplars with a leafy, broken silhouette (trunk + a column of lumpy leaf clumps) instead of smooth cypress cones */
    { const PT = relief('wood', '#3a3428', { seed: 82 }), clG = new THREE.SphereGeometry(1, 14, 10), cp = clG.attributes.position;
      for (let i = 0; i < cp.count; i++) { const k = 1 + .18 * Math.sin(cp.getX(i) * 5.3 + cp.getY(i) * 3.1) * Math.cos(cp.getZ(i) * 4.7); cp.setXYZ(i, cp.getX(i) * k, cp.getY(i) * k, cp.getZ(i) * k); } clG.computeVertexNormals();
      const N = 36 * 20, im = new THREE.InstancedMesh(clG, new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .9, bumpMap: leafTex, bumpScale: 2.2 }), N), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), C = new THREE.Color(); let k = 0;
      for (let i = 0; i < 18; i++) for (const sd of [-1, 1]) { const x = sd * (4.2 + rr(-.3, .3)), y = -10 + i * 9 + rr(-1, 1), h = rr(12, 16);
        cyl('poplar_trunk', 'wood', .16, h * .45, [x, y, 0], PT, { r2: .1 });
        for (let j = 0; j < 20; j++) { const t = j / 19, z = h * (.22 + .74 * t), r = (.95 - .6 * t * t) * rr(.65, 1.0);
          Q.setFromEuler(new THREE.Euler(rr(0, 6), rr(0, 6), rr(0, 6))); M4.compose(V(x + rr(-.35, .35), y + rr(-.35, .35), z), Q, new THREE.Vector3(r, r * 1.5, r)); im.setMatrixAt(k, M4);
          im.setColorAt(k++, C.set(['#2c4a2a', '#34522e', '#26402a', '#3a5a32'][j % 4]).offsetHSL(0, 0, rr(-.03, .03))); } }
      im.castShadow = true; im.receiveShadow = true; add(im, 'poplar_crowns', 'foliage', { mat: 'foliage' }); }
    /* V3 step 5: a wet night - glossy cobbles, puddles that hold the sky and the lamps, rain streaks, ripples, grass verges, roadside lamps */
    { road.material.roughness = Math.min(road.material.roughness ?? .8, .38); if ('metalness' in road.material) road.material.metalness = .05; road.material.needsUpdate = true;
      const wet = ctx.pbr ? ctx.pbr.metal('wet', { color: '#2a3040', rough: .06 }) : std('#2a3040', { rough: .1 });
      const pud = []; for (let i = 0; i < 16; i++) { const g = new THREE.CircleGeometry(1, 28), q = g.attributes.position; const ax = rr(.5, 1.6), ay = rr(.35, 1.0);
        for (let k = 1; k < q.count; k++) { const a = Math.atan2(q.getY(k), q.getX(k)), r = 1 + .22 * Math.sin(a * 3 + i) + .12 * Math.sin(a * 7 + i * 2); q.setXY(k, Math.cos(a) * r * ax, Math.sin(a) * r * ay); }
        const m = add(new THREE.Mesh(g, wet), 'puddle', 'water', { cast: false }); m.rotation.x = -Math.PI / 2; m.rotation.z = rr(0, 3); m.position.copy(V(rr(-2, 2), rr(-6, 60), .02)); pud.push(m); }
      const rip = []; for (let i = 0; i < 14; i++) { const r = add(new THREE.Mesh(new THREE.RingGeometry(.9, 1, 32), new THREE.MeshBasicMaterial({ color: '#c8d4ff', transparent: true, opacity: 0, depthWrite: false })), 'rain_ripple', 'fx', { cast: false }); r.rotation.x = -Math.PI / 2; r.userData.noExport = true; r.userData.p = pud[i % pud.length]; r.userData.o = rnd(); rip.push(r); }
      const NR = 1600, rg = new THREE.BufferGeometry(), rp = new Float32Array(NR * 6), seedP = []; for (let i = 0; i < NR; i++) seedP.push([rr(-9, 9), rr(-8, 50), rr(0, 14), rr(.6, 1)]);
      rg.setAttribute('position', new THREE.BufferAttribute(rp, 3)); const rain = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: '#a9b8e6', transparent: true, opacity: .32, depthWrite: false })); rain.frustumCulled = false; rain.name = 'rain'; rain.userData.noExport = true; scene.add(rain);
      for (const yy of [-2, 16, 34]) { cyl('road_lamp_post', 'metal', .05, 4.2, [3.0, yy, 0], metal('iron', '#2a2a26', { rough: .6 })); box('road_lamp_arm', 'metal', .8, .06, .06, [2.65, yy, 4.15], metal('iron', '#2a2a26'));
        const pl = new THREE.PointLight('#ffc070', 10, 11, 1.6); pl.position.copy(V(2.3, yy, 3.95)); scene.add(pl); glow('#ffc890', .55, .85, V(2.3, yy, 3.98)); }
      for (const sd of [-1, 1]) dropInstances(meadow({ name: 'verge_grass', at: [sd * 9, 20], radius: 28, count: 3000, height: .45, tints: ['#c8d0d8', '#b8c4cc', '#d4dccc'] }), (x) => Math.abs(x) < 2.9);   /* verges only: the cobbles stay clear */
      ups.push((f, t) => { for (let i = 0; i < NR; i++) { const [x, y, z0, sp] = seedP[i]; const z = ((z0 - t * 11 * sp) % 14 + 14) % 14, j = i * 6; rp[j] = x; rp[j + 1] = z; rp[j + 2] = -y; rp[j + 3] = x - .06; rp[j + 4] = z + .55 * sp; rp[j + 5] = -y; } rg.attributes.position.needsUpdate = true;
        rip.forEach(r => { const q = (t * .9 + r.userData.o) % 1; r.position.copy(r.userData.p.position); r.position.y += .01; r.position.x += Math.sin(r.userData.o * 40) * .4; r.scale.setScalar(.05 + q * .35); r.material.opacity = .5 * (1 - q); }); }); }
    const ht = halftrack('sound_halftrack', [0, 6, 0], -Math.PI / 2); { const wl = new THREE.PointLight('#ffcf8a', 14, 9, 1.6); wl.position.copy(V(1.6, 6.2, 3.3)); scene.add(wl); glow('#ffcf8a', .5, .8, V(1.6, 6.2, 3.3)); cyl('ht_lamp_post', 'metal', .03, 1.2, [1.6, 6.2, 2.1], metal('iron', '#3a3a34')); }   /* the operator's hooded lamp: the vehicle reads at night */
    const moon = glow('#dfe8ff', 18, .9, V(-30, 120, 60)); const hl = new THREE.SpotLight('#ffe9b0', 30, 40, .5, .6); hl.position.copy(V(0, 8.6, 1.2)); hl.target.position.copy(V(0, 30, 0)); scene.add(hl, hl.target);
    // sound made visible: rings rolling out of the horn
    const bandTex = canvasTex(256, 16, (g, w, h) => { const gr = g.createLinearGradient(0, 0, w, 0); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(.55, 'rgba(255,255,255,.9)'); gr.addColorStop(.7, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
    const rings = []; for (let i = 0; i < 8; i++) { const rg = new THREE.RingGeometry(.7, 1.0, 72, 1), ru = rg.attributes.uv, rp = rg.attributes.position; for (let k = 0; k < ru.count; k++) ru.setXY(k, (Math.hypot(rp.getX(k), rp.getY(k)) - .7) / .3, .5); const r = new THREE.Mesh(rg, new THREE.MeshBasicMaterial({ map: bandTex, color: '#c4dcff', transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, fog: false })); r.userData.noExport = true; r.name = 'sound_ring'; scene.add(r); rings.push(r); }
    // ghost tanks that exist only as sound: faint silhouettes on the poplar line
    const ghosts = []; for (let i = 0; i < 5; i++) { const t = sherman('ghost_tank', { at: [rr(-14, -7), 18 + i * 10, 0], rot: Math.PI / 2, cast: false }); t.traverse(o => { if (o.isMesh) { o.material = o.material.clone(); o.material.transparent = true; o.material.opacity = 0; o.material.depthWrite = false; } }); ghosts.push(t); }
    const hz = EV.hundred || 0;
    let CAM = null; scene.onBeforeRender = (r_, s_, c_) => { CAM = c_; };
    ups.push((f, t) => { ht.userData.disc.rotation.y = t * 3.5; const on = sm((f - (hz - 10)) / 15);
      const hpos = ht.userData.horn.getWorldPosition(new THREE.Vector3()), ax = new THREE.Vector3(1, 0, 0).applyQuaternion(ht.quaternion).normalize();
      rings.forEach((r, i) => { const q = ((t * .45 + i / rings.length) % 1); r.position.copy(hpos).addScaledVector(ax, .9 + q * 8); r.lookAt(r.position.clone().add(ax)); r.scale.setScalar(1.05 + q * 4.2); const dc = (CAM && CAM.position) ? r.position.distanceTo(CAM.position) : 99; r.material.opacity = on * .75 * Math.pow(1 - q, 1.2) * Math.min(1, q * 10) * Math.min(1, Math.max(0, (dc - 3) / 5));   /* never a veil over the lens */ });
      ghosts.forEach((g, i) => g.traverse(o => { if (o.isMesh) o.material.opacity = on * (.12 + .08 * Math.sin(t * 2 + i)); })); });
    anchors = { halftrack: [0, 6, 2], speaker: [0, 7.2, 2.75] };
  }
  const room = (w, d, h, wallCol, floorKind, floorCol, o = {}) => { const fl = add(new THREE.Mesh(new THREE.PlaneGeometry(w, d), relief(floorKind, floorCol, { seed: 91, size: 2 })), 'floor', 'wood', { cast: false, mat: floorKind === 'wood' ? 'wood_grain' : 'stone' }); fl.rotation.x = -Math.PI / 2; fl.position.copy(V(0, d / 2 - 2, 0));
    const W = o.wallMat || relief(o.wallKind || 'plaster', wallCol, { seed: 92 }); if (o.win) { const [cx, z0, ww, wh] = o.win, x0 = cx - ww / 2, x1 = cx + ww / 2;   // back wall with a real hole for the window
      box('wall_back', 'plaster', x0 + w / 2, .2, h, [(-w / 2 + x0) / 2, d - 2, 0], W); box('wall_back', 'plaster', w / 2 - x1, .2, h, [(x1 + w / 2) / 2, d - 2, 0], W);
      box('wall_back', 'plaster', ww, .2, z0, [cx, d - 2, 0], W); box('wall_back', 'plaster', ww, .2, h - z0 - wh, [cx, d - 2, z0 + wh], W);
    } else box('wall_back', 'plaster', w, .2, h, [0, d - 2, 0], W); box('wall_left', 'plaster', .2, d, h, [-w / 2, d / 2 - 2, 0], W); box('wall_right', 'plaster', .2, d, h, [w / 2, d / 2 - 2, 0], W);
    if (!o.noCeil) box('ceiling', 'plaster', w, d, .2, [0, d / 2 - 2, h], o.ceilMat || W, { cast: false });
    if (o.skirting) for (const [sx, sy, sw, sd] of [[0, d - 2.11, w, .03], [-w / 2 + .11, d / 2 - 2, .03, d], [w / 2 - .11, d / 2 - 2, .03, d]]) box('skirting_board', 'wood', sw, sd, .14, [sx, sy, 0], o.skirting); };
  // v1 note 3: each room its own wall and ceiling surface (no shared plaster that read as a map)
  const surf = (draw, rep, o = {}) => { const t = canvasTex(512, 512, draw); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]); const b = o.bump ? canvasTex(512, 512, o.bump) : null; if (b) { b.wrapS = b.wrapT = THREE.RepeatWrapping; b.repeat.set(rep[0], rep[1]); b.colorSpace = THREE.NoColorSpace; }
    return new THREE.MeshStandardMaterial({ map: t, roughness: o.rough ?? .88, bumpMap: b, bumpScale: o.bs ?? 1 }); };
  const noiseFill = (g, w, h, n, a, c = '0,0,0') => { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(${c},${(rnd() * a).toFixed(3)})`; g.fillRect(rnd() * w, rnd() * h, rr(1, 4), rr(1, 4)); } };
  const tentCanvas = surf((g, w, h) => { g.fillStyle = '#7b7650'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 3) { g.fillStyle = `rgba(0,0,0,${y % 6 ? .05 : .09})`; g.fillRect(0, y, w, 1); } for (let x = 0; x < w; x += 3) { g.fillStyle = 'rgba(255,255,230,.04)'; g.fillRect(x, 0, 1, h); }
      for (const x of [0, 256]) { g.fillStyle = 'rgba(40,36,20,.45)'; g.fillRect(x, 0, 10, h); for (let y = 0; y < h; y += 12) { g.fillStyle = 'rgba(230,220,180,.35)'; g.fillRect(x + 3, y, 4, 5); } }
      for (let i = 0; i < 6; i++) { g.fillStyle = 'rgba(60,50,30,.10)'; g.beginPath(); g.ellipse(rr(0, w), rr(h * .5, h), rr(20, 60), rr(30, 80), 0, 0, 6.3); g.fill(); } noiseFill(g, w, h, 6000, .06); }, [2, 1],
    { bump: (g, w, h) => { g.fillStyle = '#808080'; g.fillRect(0, 0, w, h); for (let y = 0; y < h; y += 3) { g.fillStyle = y % 6 ? '#8a8a8a' : '#707070'; g.fillRect(0, y, w, 1); } for (const x of [0, 256]) { g.fillStyle = '#b0b0b0'; g.fillRect(x, 0, 10, h); } }, bs: .8 });
  const cafePaper = surf((g, w, h) => { g.fillStyle = '#e4d3a8'; g.fillRect(0, 0, w, h); for (let x = 0; x < w; x += 64) { g.fillStyle = 'rgba(160,120,60,.18)'; g.fillRect(x, 0, 22, h); g.fillStyle = 'rgba(120,80,40,.25)'; g.fillRect(x + 30, 0, 2, h); }
      for (let y = 32; y < h; y += 64) for (let x = 43; x < w; x += 64) { g.fillStyle = 'rgba(150,60,40,.35)'; g.beginPath(); for (let k = 0; k < 4; k++) { const a = k * Math.PI / 2; g.ellipse(x + Math.cos(a) * 5, y + Math.sin(a) * 5, 5, 3, a, 0, 6.3); } g.fill(); }
      const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, 'rgba(70,40,10,.22)'); gr.addColorStop(.3, 'rgba(70,40,10,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h); noiseFill(g, w, h, 4000, .05); }, [5, 1.6]);
  const cafeCeil = surf((g, w, h) => { g.fillStyle = '#e9dcbc'; g.fillRect(0, 0, w, h); g.fillStyle = 'rgba(80,50,20,.25)'; g.fillRect(0, 0, w, h); noiseFill(g, w, h, 5000, .08, '90,60,20'); }, [2, 2]);
  const blockPaint = relief('brick', '#7d8588', { seed: 95, size: 1.2 });
  const roomPaper = surf((g, w, h) => { g.fillStyle = '#d6cdb2'; g.fillRect(0, 0, w, h); for (let y = 24; y < h; y += 48) for (let x = (y / 48 % 2) * 24 + 12; x < w; x += 48) { g.fillStyle = 'rgba(90,110,160,.45)'; for (let k = 0; k < 5; k++) { const a = k * 1.2566; g.beginPath(); g.ellipse(x + Math.cos(a) * 5, y + Math.sin(a) * 5, 4, 2.4, a, 0, 6.3); g.fill(); } g.fillStyle = 'rgba(240,200,90,.8)'; g.beginPath(); g.arc(x, y, 2.2, 0, 6.3); g.fill(); }
      noiseFill(g, w, h, 3000, .04); }, [4, 1.4]);
  const lamp = (at, col = '#ffcf8a', I = 14, R = 9) => { const l = new THREE.PointLight(col, I, R, 1.5); l.position.copy(V(...at)); scene.add(l); glow(col, .9, .8, V(...at)); return l; };
  /* V3: place a Blender prop (GLB) at plan coordinates; materials are kept, metals get the place's env map through ctx.pbr when it exists */
  const prop = (key, name, role, at, rotY = 0, remap = {}) => { const g = GLB[key].clone(true); g.name = name; g.position.copy(V(...at)); g.rotation.y = rotY;
    g.traverse(o => { if (!o.isMesh) return; const m = remap[o.material.name]; if (m) o.material = m; o.userData.role = role; o.castShadow = true; o.receiveShadow = true; }); scene.add(g); return g; };
  /* V3 step 4 helpers: soft, irregular shapes for dressing (sandbags, duffels, cushions), built as real deformed meshes */
  const lumpGeo = (sx, sy, sz, k = .12, sd = 1) => { const g = new THREE.SphereGeometry(1, 18, 12).toNonIndexed(), q = g.attributes.position;
    for (let i = 0; i < q.count; i++) { const x = q.getX(i), y = q.getY(i), z = q.getZ(i), n = 1 + k * Math.sin(x * 4.1 + sd) * Math.cos(z * 3.3 + sd * 2) + k * .5 * Math.sin(y * 7 + sd);
      q.setXYZ(i, x * sx * n, Math.max(-sy * .55, y * sy * n), z * sz * n); } g.computeVertexNormals(); return g; };
  const lump = (name, role, geo, mat, at, rot = 0) => { const m = add(new THREE.Mesh(geo, mat), name, role); m.position.copy(V(...at)); m.rotation.y = rot; return m; };
  const crate = (at, w, d, h, stencil, sd) => { const W = relief('wood', '#7a6444', { seed: sd }); box('supply_crate', 'wood', w, d, h, at, W);
    for (const dz of [.12, h - .12]) box('crate_band', 'metal', w + .01, d + .01, .04, [at[0], at[1], at[2] + dz], metal('iron', '#3a3a32', { rough: .7 }));
    if (stencil) { const t = canvasTex(256, 96, (g, ww, hh) => { g.clearRect(0, 0, ww, hh); g.fillStyle = 'rgba(30,28,20,.85)'; g.font = 'bold 40px monospace'; g.textAlign = 'center'; g.fillText(stencil, ww / 2, 62); });
      const m = add(new THREE.Mesh(new THREE.PlaneGeometry(w * .8, h * .35), new THREE.MeshStandardMaterial({ map: t, transparent: true, alphaTest: .3, polygonOffset: true, polygonOffsetFactor: -4 })), 'crate_stencil', 'wood', { cast: false });
      m.position.copy(V(at[0], at[1] - d / 2 - .006, at[2] + h * .55)); } };
  if (Z === 'radio') {
    room(6, 6, 3.2, '#8a8460', 'wood', '#6a5a44', { wallMat: tentCanvas, ceilMat: tentCanvas });   // inside the radio tent: canvas walls with seams, tent poles
    for (const x of [-2.9, 2.9]) cyl('tent_pole', 'wood', .06, 3.2, [x, 1.0, 0], relief('wood', '#6a5434', { seed: 103 }));
    box('ridge_pole', 'wood', 6, .1, .1, [0, 1.0, 3.05], relief('wood', '#6a5434', { seed: 104 }));
    // the operator's desk dressing: headphones, logbook, field telephone, mug, folding chair, a lantern
    cyl('ashtray', 'metal', .07, .02, [1.05, 1.25, .8], metal('iron', '#5a5a52')); { const cig = cyl('cigarette', 'cloth', .006, .07, [1.05, 1.25, .82], std('#efe8dc')); cig.rotation.z = Math.PI / 2 - .2; const ember = glow('#ff8a3a', .03, .9, V(1.09, 1.25, .826));
      const wisps = []; for (let i = 0; i < 9; i++) { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#cfd2d6', transparent: true, opacity: 0, depthWrite: false })); sp.userData.noExport = true; scene.add(sp); wisps.push(sp); }
      ups.push((f, t) => { wisps.forEach((sp, i) => { const q = ((t * .22 + i / wisps.length) % 1); sp.position.copy(V(1.09 + .05 * Math.sin(t * 1.3 + i * 2.1) * q * 4, 1.25 + .02 * Math.cos(t + i), .84 + q * .9)); sp.scale.setScalar(.06 + q * .3); sp.material.opacity = .45 * (1 - q) * Math.min(1, q * 6); }); ember.material.opacity = .7 + .3 * Math.sin(t * 3.1); }); }
    box('logbook', 'cloth', .34, .26, .03, [.9, 1.35, .8], std('#3a4a2a')); box('logbook_page', 'cloth', .3, .22, .005, [.9, 1.35, .832], std('#efe6cf'));
    box('field_phone', 'metal', .3, .2, .18, [-1.0, 1.75, .8], relief('wood', '#4a3a2a', { seed: 105 })); cyl('mug', 'metal', .045, .1, [1.2, 1.6, .8], metal('steel', '#cfd2c8', { rough: .5 }));
    { const hp = new THREE.Mesh(new THREE.TorusGeometry(.1, .012, 6, 20, Math.PI), std('#2a2a24')); hp.position.copy(V(.6, 1.7, .9)); add(hp, 'headphones', 'metal'); for (const sx of [-.1, .1]) cyl('earcup', 'metal', .04, .03, [.6 + sx, 1.7, .8], std('#1e1e1a')); }
    box('chair_seat', 'wood', .45, .45, .04, [-1.5, .9, .45], relief('wood', '#7a5a3a', { seed: 106 })); for (const sx of [-.2, .2]) for (const sy of [-.2, .2]) box('chair_leg', 'metal', .03, .03, .45, [-1.5 + sx, .9 + sy, 0], metal('iron', '#3a3a34'));
    box('radio_table', 'wood', 2.4, 1.0, .8, [0, 1.6, 0], relief('wood', '#7a5a3a', { seed: 101 }));
    prop('field_radio', 'field_radio', 'metal', [.3, 1.7, .8], -Math.PI / 2, { case: metal('iron', '#4d5634', { rough: .55 }), chrome: metal('steel', '#c8c8c0', { rough: .25 }), brass: metal('brass', '#c8a24a') });   /* V3: Blender model (meters, tuning window, knobs, toggles, handles, vents) */
    const mk = prop('morse_key', 'morse_key', 'metal', [-.5, 1.4, .8], 0, { brass: metal('brass', '#c8a24a', { rough: .3 }) }), key = mk.getObjectByName('key_lever');   /* V3: Blender key, the lever pivots */
    const card = add(new THREE.Mesh(new THREE.PlaneGeometry(.8, .5), basic('#ffffff', { map: canvasTex(320, 200, (g, w, h) => { g.fillStyle = '#efe6d0'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a2420'; g.font = 'bold 20px serif'; g.fillText('FIST: OP. 4th ARMD', 14, 30); for (let r = 0; r < 4; r++) { let x = 14; for (let i = 0; i < 14; i++) { const dash = rnd() < .45; g.fillRect(x, 60 + r * 34, dash ? 22 : 8, 8); x += dash ? 30 : 16; } } }) })), 'fist_card', 'cloth', { cast: false }); card.position.copy(V(-.2, 3.85, 1.6));
    lamp([.8, 1.4, 2.4], '#ffd08a', 16, 8);
    box('map_board', 'wood', 1.6, .05, 1.0, [1.4, 3.86, 1.2], std('#ffffff', { extra: { map: canvasTex(320, 200, (g, w, h) => { g.fillStyle = '#d8ccA0'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(90,120,80,.6)'; for (let i = 0; i < 14; i++) { g.beginPath(); g.moveTo(0, rr(0, h)); g.bezierCurveTo(w * .3, rr(0, h), w * .6, rr(0, h), w, rr(0, h)); g.stroke(); }
      g.strokeStyle = '#4a6ab0'; g.lineWidth = 6; g.beginPath(); g.moveTo(w * .7, 0); g.bezierCurveTo(w * .55, h * .4, w * .8, h * .7, w * .6, h); g.stroke(); g.fillStyle = '#2a2a24'; g.font = 'bold 14px serif'; g.fillText('SECTOR 7 - GRID 41', 10, 18); for (let i = 0; i < 7; i++) { g.fillStyle = ['#c8322c', '#2a5ab0', '#2a2a24'][i % 3]; g.beginPath(); g.arc(rr(30, w - 30), rr(30, h - 30), 4, 0, 6.3); g.fill(); } }) } }));
    /* V3 step 4: a real signals tent - canvas roof in an A between the walls and the ridge pole, sagging between the poles; duckboard floor;
       sandbags along the walls; stacked supply crates with stencils; battery boxes cabled to the set; a second receiver; a cot with a blanket;
       a hanging hurricane lantern (practical light); a helmet and a musette bag; telephone wire reel; a clipboard. */
    for (const sgn of [-1, 1]) { const g = new THREE.PlaneGeometry(6.2, 3.3, 30, 16), q = g.attributes.position;
      for (let i = 0; i < q.count; i++) { const x = q.getX(i), y = q.getY(i); q.setZ(i, -.09 * Math.sin((y + 1.65) / 3.3 * Math.PI) * (1 - .4 * Math.abs(Math.sin(x * 1.05))) + .012 * Math.sin(x * 9 + y * 4)); }
      g.computeVertexNormals(); const r = add(new THREE.Mesh(g, tentCanvas), 'tent_roof', 'cloth', { cast: false }); r.position.copy(V(0, 1.0 + sgn * 1.55, 2.68)); r.rotation.x = -Math.PI / 2 + sgn * .43; r.rotation.order = 'YXZ'; if (sgn > 0) r.rotation.y = Math.PI; r.material.side = THREE.DoubleSide; }
    for (let i = 0; i < 9; i++) box('duckboard', 'wood', .5, 5.8, .04, [-2.6 + i * .62, 1.0, .005], relief('wood', '#6e5a40', { seed: 170 + i }), { cast: false });
    const bagM = relief('cloth', '#8a7a52', { seed: 180 }), bagG = [0, 1, 2].map(k => lumpGeo(.32, .14, .2, .1, k * 1.7));
    for (let i = 0; i < 9; i++) { lump('sandbag', 'cloth', bagG[i % 3], bagM, [-2.65 + i * .62, 3.75, .1], rr(-.15, .15)); if (i % 2 === 0) lump('sandbag', 'cloth', bagG[(i + 1) % 3], bagM, [-2.35 + i * .62, 3.72, .32], rr(-.2, .2)); }
    for (let i = 0; i < 5; i++) lump('sandbag', 'cloth', bagG[i % 3], bagM, [2.72, 3.4 - i * .62, .1], Math.PI / 2 + rr(-.15, .15));
    crate([2.25, 3.35, 0], .9, .6, .55, 'SIG. CORPS', 191); crate([2.25, 3.35, .56], .8, .55, .45, 'BC-610', 192); crate([1.35, 3.5, 0], .7, .5, .5, '603 ENGR', 193);
    for (let i = 0; i < 3; i++) { box('battery_box', 'metal', .3, .22, .26, [.9 + i * .34, 2.3, .8], std('#2a2c26', { rough: .6 })); cyl('battery_post', 'metal', .02, .04, [.86 + i * .34, 2.3, 1.07], metal('brass', '#c8a24a')); }
    { const cab = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V(.9, 2.3, 1.08), V(.8, 2.1, 1.15), V(.55, 1.95, 1.1), V(.4, 1.85, 1.05)]), 24, .012, 6), std('#1a1a18', { rough: .7 })); add(cab, 'battery_cable', 'metal'); }
    box('receiver_set', 'metal', .6, .38, .34, [-.25, 1.75, 1.4], metal('iron', '#4d5634', { rough: .55 })); for (let i = 0; i < 3; i++) cyl('receiver_knob', 'metal', .035, .03, [-.45 + i * .2, 1.55, 1.5], std('#151515', { rough: .4 }));
    box('cot_frame', 'wood', .8, 2.0, .08, [-2.35, 2.6, .42], relief('wood', '#6a5434', { seed: 194 })); for (const sx of [-.35, .35]) for (const sy of [1.7, 3.5]) box('cot_leg', 'wood', .04, .04, .42, [-2.35 + sx, sy, 0], relief('wood', '#6a5434', { seed: 195 }));
    lump('cot_blanket', 'cloth', lumpGeo(.42, .1, 1.0, .08, 3), relief('cloth', '#5a5a3e', { seed: 196 }), [-2.35, 2.6, .5]); lump('duffel_bag', 'cloth', lumpGeo(.45, .22, .25, .1, 5), relief('cloth', '#6a6444', { seed: 197 }), [-2.3, 3.6, .22], .3);
    cyl('helmet_on_crate', 'metal', .17, .13, [1.35, 3.45, .5], metal('iron', '#4d5634', { rough: .65, rust: .2 }), { r2: .1 });
    cyl('wire_reel', 'metal', .16, .22, [2.4, 2.0, .16], metal('iron', '#3a3a34'), { rx: Math.PI / 2 }); cyl('wire_coil', 'metal', .14, .18, [2.4, 2.0, .16], std('#2a2a22', { rough: .7 }), { rx: Math.PI / 2 });
    box('clipboard', 'wood', .24, .02, .32, [-2.85, 1.6, 1.5], relief('wood', '#8a6a44', { seed: 198 })); box('clip_sheet', 'cloth', .2, .005, .26, [-2.84, 1.59, 1.49], std('#efe6cf'));
    { const lan = new THREE.Group(); lan.position.copy(V(-.9, 1.0, 2.55)); scene.add(lan); lan.name = 'hurricane_lantern';
      const fr = add(new THREE.Mesh(new THREE.CylinderGeometry(.08, .1, .26, 12, 1, true), std('#e8d8a0', { rough: .2, extra: { emissive: new THREE.Color('#ffb860'), emissiveIntensity: 1.6, transparent: true, opacity: .85 } })), 'lantern_glass', 'glass', { parent: lan, cast: false });
      add(new THREE.Mesh(new THREE.CylinderGeometry(.05, .11, .06, 12), metal('iron', '#2a2a24')), 'lantern_cap', 'metal', { parent: lan }).position.y = .16;
      add(new THREE.Mesh(new THREE.TorusGeometry(.06, .008, 6, 14, Math.PI), metal('iron', '#2a2a24')), 'lantern_handle', 'metal', { parent: lan }).position.y = .22;
      const ll = new THREE.PointLight('#ffb460', 6, 6, 1.6); lan.add(ll); ups.push((f, t) => { lan.rotation.z = .04 * Math.sin(t * 1.1); ll.intensity = 6 + .5 * Math.sin(t * 13) * Math.sin(t * 3.1); }); }
    ups.push((f, t) => { key.rotation.z = (Math.sin(t * 22) > .4 ? -.08 : 0); });
    anchors = { key: [-.5, 1.4, .85], card: [-.2, 3.85, 1.85] };
  }
  if (Z === 'cafe') {
    room(10, 8, 3.6, '#d8c49a', 'tile', '#b8a88a', { wallMat: cafePaper, ceilMat: cafeCeil });
    { const WD = relief('wood', '#5a3a24', { seed: 112 });   // wood wainscot + chair rail, ceiling beams, mirror and shelves behind the bar, a chalkboard, a clock, the accordion on a chair
      box('wainscot', 'wood', 9.8, .06, 1.1, [0, 5.9, 0], WD); box('wainscot', 'wood', .06, 7.8, 1.1, [-4.88, 2, 0], WD); box('wainscot', 'wood', .06, 7.8, 1.1, [4.88, 2, 0], WD);
      box('chair_rail', 'wood', 9.8, .1, .06, [0, 5.87, 1.1], WD); for (let i = 0; i < 5; i++) box('ceiling_beam', 'wood', .22, 8, .26, [-4 + i * 2, 2, 3.34], WD);
      box('bar_mirror', 'glass', 3.0, .04, 1.0, [2.4, 5.92, 1.6], std('#8c989e', { rough: .12, metal: .85 })); for (const z of [1.45, 2.2]) box('bar_shelf', 'wood', 3.4, .25, .04, [2.4, 5.8, z], WD);
      for (let i = 0; i < 10; i++) cyl('shelf_bottle', 'glass', .045, rr(.26, .36), [1.0 + i * .3, 5.8, 2.24], std(['#2a5a3a', '#6a4a1a', '#3a3a6a', '#7a2a2a', '#c8b060'][i % 5], { rough: .12 }));
      box('chalkboard', 'wood', 1.0, .04, .7, [-3.0, 5.9, 1.6], std('#ffffff', { extra: { map: canvasTex(200, 140, (g, w, h) => { g.fillStyle = '#2c3a30'; g.fillRect(0, 0, w, h); g.strokeStyle = '#6a4a2a'; g.lineWidth = 10; g.strokeRect(0, 0, w, h); g.fillStyle = '#e8e8dc'; g.font = '18px serif'; g.fillText('PLAT DU JOUR', 30, 40); g.font = '15px serif'; g.fillText('Omelette ... 8 F', 26, 75); g.fillText('Café ...... 2 F', 26, 102); }) } }));
      cyl('clock_face', 'cloth', .22, .04, [0.0, 5.9, 2.6], std('#efe8d6')).rotation.x = Math.PI / 2;
      for (const [x, y] of [[-2.6, 2.0], [-1.0, 3.6]]) { cyl('coffee_cup', 'cloth', .045, .06, [x + .12, y - .05, .78], std('#f2efe6', { rough: .3 })); cyl('saucer', 'cloth', .07, .01, [x + .12, y - .05, .78], std('#f2efe6', { rough: .3 })); }
      box('newspaper', 'cloth', .4, .3, .01, [-2.5, 2.1, .785], std('#e2dccb'));
      box('spy_chair_seat', 'wood', .44, .42, .05, [-2.6, 1.42, .43], WD); for (const sx of [-.19, .19]) for (const sy of [-.18, .18]) box('spy_chair_leg', 'wood', .04, .04, .43, [-2.6 + sx, 1.42 + sy, 0], WD);   /* animation audit: the spy's seated move sat on air; a stool, no back (a back would sit between the lens and him) */
      const acc = new THREE.Group(); acc.position.copy(V(-4.1, 4.4, .5)); scene.add(acc); for (let i = 0; i < 6; i++) { const b = add(new THREE.Mesh(new THREE.BoxGeometry(.06, .34, .3), std(i % 2 ? '#7a1e1e' : '#e6dcc8')), 'accordion_bellows', 'cloth', { parent: acc }); b.position.set(-.15 + i * .06, .17, 0); }
      for (const sx of [-.24, .24]) { const e = add(new THREE.Mesh(new THREE.BoxGeometry(.12, .38, .32), std('#1e1e1e', { rough: .3 })), 'accordion_end', 'cloth', { parent: acc }); e.position.set(sx, .19, 0); }
      box('accordion_chair', 'wood', .45, .45, .04, [-4.1, 4.4, .46], WD); for (const sx of [-.2, .2]) for (const sy of [-.2, .2]) box('chair_leg', 'wood', .04, .04, .46, [-4.1 + sx, 4.4 + sy, 0], WD); }
    box('zinc_bar', 'metal', 4.2, .8, 1.1, [2.4, 4.4, 0], metal('steel', '#a8aaa4', { rough: .35, finish: 'brushed' })); box('bar_top', 'metal', 4.4, 1.0, .06, [2.4, 4.4, 1.1], metal('steel', '#c8cac4', { rough: .25 }));
    for (const [x, y] of [[-2.6, 2.0], [-1.0, 3.6], [-3.4, 4.6]]) { cyl('cafe_table', 'wood', .45, .04, [x, y, .74], relief('wood', '#6a4a30', { seed: 111 })); cyl('cafe_table_leg', 'metal', .04, .74, [x, y, 0], metal('iron', '#2a2a2a')); for (const a of [0, 2.2, 4.2]) { cyl('cafe_chair_seat', 'wood', .2, .05, [x + Math.cos(a) * .75, y + Math.sin(a) * .75, .45], relief('wood', '#7a5a3a', { seed: 112 })); } }
    for (let i = 0; i < 3; i++) { const post = add(new THREE.Mesh(new THREE.PlaneGeometry(.9, 1.3), basic('#ffffff', { map: canvasTex(180, 260, (g, w, h) => { g.fillStyle = ['#e8c45a', '#5a8ac8', '#d86a4a'][i]; g.fillRect(0, 0, w, h); g.fillStyle = '#1e1a1a'; g.font = 'bold 26px serif'; g.fillText(['CINZANO', 'BYRRH', 'PERNOD'][i], 14, 60); g.font = '18px serif'; g.fillText('apéritif', 40, 220); }) })), 'cafe_poster', 'cloth', { cast: false }); post.position.copy(V(-3.8 + i * 1.3, 5.88, 2.2)); }
    for (let i = 0; i < 6; i++) cyl('bottle', 'glass', .05, .32, [1.0 + i * .4, 5.7, 1.2], std(['#2a5a3a', '#6a2a2a', '#3a3a6a'][i % 3], { rough: .15 }));
    // the window to the street and the ONE red of the film: the café's awning, seen through the glass
    box('cafe_window', 'glass', 3.0, .1, 1.8, [-1.0, -1.95, .9], std('#b8d0e0', { rough: .1, extra: { transparent: true, opacity: .35 } }));
    box('red_awning', 'cloth', 3.4, .9, .2, [-1.0, -2.6, 2.9], std('#c8322c', { rough: .7 }));
    lamp([-2, 3, 3.2], '#ffc884', 20, 10); lamp([2.4, 4, 3.2], '#ffc884', 14, 8);
    anchors = { bar: [2.4, 4.4, 1.2], spy_table: [-2.6, 2.0, .8] };
  }
  /* SET DETAIL (2026-11-18, stage 9 three.js enrichment, CB choice "2"): more real things in the three test places, in each place's own palette.
     Off unless film.json "set_detail": true, so V3 renders as before. Own random stream (rr2), so nothing placed above moves. */
  if (film.set_detail) {
    let s2 = 90001 + Z.length * 7; const r2 = () => (s2 = (s2 * 48271) % 2147483647) / 2147483647, rr2 = (a, b) => a + r2() * (b - a);
    const tube = (name, role, pts, r, mat, o = {}) => add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p => V(...p))), o.seg ?? 24, r, 8, !!o.closed), mat), name, role, o);
    const inst = (name, role, geo, mat, list, o = {}) => { const im = new THREE.InstancedMesh(geo, mat, list.length), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), C = new THREE.Color();
      list.forEach((e, i) => { Q.setFromEuler(new THREE.Euler(e.rx || 0, e.ry || 0, e.rz || 0)); M4.compose(V(...e.at), Q, new THREE.Vector3(...(e.s || [1, 1, 1]))); im.setMatrixAt(i, M4); if (e.c) im.setColorAt(i, C.set(e.c)); });
      return add(im, name, role, o); };
    if (Z === 'cafe') {
      const BW = std('#2e1e14', { rough: .55 }), BRASS = metal('brass', '#c8a24a', { rough: .3 }), GL = std('#cfe0e4', { rough: .05, extra: { transparent: true, opacity: .35, depthWrite: false } }), PAPER = std('#efe6cc', { rough: .7 });
      // bistro chairs: the floating round seats get three bentwood legs, a ring brace and a looped back (not the spy's stool side: a back there would sit between the lens and him)
      for (const [x, y] of [[-2.6, 2.0], [-1.0, 3.6], [-3.4, 4.6]]) for (const a of [0, 2.2, 4.2]) { const cx = x + Math.cos(a) * .75, cy = y + Math.sin(a) * .75;
        for (let k = 0; k < 3; k++) { const b = a + k * 2.094 + .5; cyl('chair_leg_bentwood', 'wood', .014, .45, [cx + Math.cos(b) * .14, cy + Math.sin(b) * .14, 0], BW, { r2: .016 }); }
        tube('chair_ring', 'wood', Array.from({ length: 13 }, (_, i) => [cx + Math.cos(i / 12 * 6.283) * .13, cy + Math.sin(i / 12 * 6.283) * .13, .16]), .008, BW, { closed: true, cast: false });
        if (Math.hypot(cx + 2.6, cy - 1.1) < .9) continue;
        const ox = Math.cos(a), oy = Math.sin(a), px = -oy, py = ox, pts = []; for (let i = 0; i <= 16; i++) { const u = i / 16, ang = Math.PI * u; pts.push([cx + ox * .17 + px * Math.cos(ang) * .17, cy + oy * .17 + py * Math.cos(ang) * .17, .47 + Math.sin(ang) * .42]); }
        tube('chair_back_loop', 'wood', pts, .012, BW); }
      // pendant lamps: cord, green enamel shade, bulb (the glows already sit at the bulbs)
      for (const [x, y] of [[-2, 3], [2.4, 4]]) { cyl('lamp_cord', 'metal', .006, .34, [x, y, 3.26], std('#1a1a1a'), { cast: false });
        const sh = cyl('lamp_shade', 'metal', .26, .16, [x, y, 3.16], std('#2f4a36', { rough: .4, extra: { side: THREE.DoubleSide } }), { r2: .05, cast: false }); sh.geometry = new THREE.CylinderGeometry(.05, .26, .16, 28, 1, true);
        add(new THREE.Mesh(new THREE.SphereGeometry(.05, 12, 8), basic('#fff0c8')), 'lamp_bulb', 'lamp', { cast: false }).position.copy(V(x, y, 3.17)); }
      // the bar: a brass foot rail, beer pumps, a cash register, glasses, a soda siphon; crown moulding all round
      tube('bar_foot_rail', 'metal', [[0.3, 3.93, .2], [4.5, 3.93, .2]], .025, BRASS, { seg: 4 });
      for (const x of [.6, 4.2]) cyl('rail_bracket', 'metal', .015, .2, [x, 3.97, 0], BRASS);
      for (let i = 0; i < 3; i++) { cyl('beer_pump', 'metal', .03, .32, [1.7 + i * .16, 4.25, 1.16], BRASS); cyl('pump_handle', 'wood', .018, .2, [1.7 + i * .16, 4.22, 1.48], std('#e8e0cc', { rough: .4 })); }
      box('cash_register', 'metal', .38, .34, .26, [3.95, 4.5, 1.16], metal('brass', '#9a7a3a', { rough: .45 })); box('register_top', 'metal', .34, .14, .12, [3.95, 4.58, 1.42], metal('brass', '#9a7a3a', { rough: .45 }));
      for (let i = 0; i < 6; i++) cyl('bar_glass', 'glass', .035, .1, [2.6 + (i % 3) * .09, 4.12 + (i >> 1 & 1) * .09, 1.16], GL, { r2: .042, cast: false });
      cyl('siphon', 'glass', .05, .26, [3.2, 4.2, 1.16], std('#5a8a9a', { rough: .1, metal: .2 })); cyl('siphon_head', 'metal', .03, .08, [3.2, 4.2, 1.42], metal('steel', '#c8c8c0'));
      for (const [w, d, at] of [[9.8, .1, [0, 5.85, 3.48]], [.1, 7.8, [-4.85, 2, 3.48]], [.1, 7.8, [4.85, 2, 3.48]]]) box('crown_moulding', 'wood', w, d, .12, at, relief('wood', '#5a3a24', { seed: 113 }), { cast: false });
      // the bottles become bottles: neck, shoulder and a paper label on every shelf and back-bar cylinder
      const bt = []; scene.traverse(o => { if (o.isMesh && /^(shelf_)?bottle/.test(o.name)) bt.push(o); });
      for (const o of bt) { const h = o.geometry.parameters.height, r = o.geometry.parameters.radiusTop, p = o.position;
        const sh = add(new THREE.Mesh(new THREE.CylinderGeometry(r * .32, r, h * .18, 16), o.material), 'bottle_shoulder', 'glass', { cast: false }); sh.position.set(p.x, p.y + h / 2 + h * .09, p.z);
        const nk = add(new THREE.Mesh(new THREE.CylinderGeometry(r * .3, r * .32, h * .3, 12), o.material), 'bottle_neck', 'glass', { cast: false }); nk.position.set(p.x, p.y + h / 2 + h * .33, p.z);
        const lb = add(new THREE.Mesh(new THREE.CylinderGeometry(r * 1.02, r * 1.02, h * .34, 16, 1, true), std(['#efe6cc', '#e8c45a', '#d8d0b8'][Math.floor(rr2(0, 3))], { rough: .7 })), 'bottle_label', 'cloth', { cast: false }); lb.position.set(p.x, p.y - h * .05, p.z); }
      // tables: wine, glasses, an ashtray; a coat stand with a hat in the far corner; two framed pictures on the left wall
      cyl('wine_bottle', 'glass', .038, .24, [-.88, 3.66, .76], std('#2a3a22', { rough: .1 })); cyl('wine_neck', 'glass', .014, .1, [-.88, 3.66, 1.0], std('#2a3a22', { rough: .1 }));
      for (const [dx, dy] of [[-.25, .12], [.1, -.2]]) { cyl('wine_glass_stem', 'glass', .005, .09, [-1.0 + dx, 3.6 + dy, .76], GL, { cast: false }); cyl('wine_glass_bowl', 'glass', .03, .07, [-1.0 + dx, 3.6 + dy, .85], std('#7a1e2a', { rough: .1, extra: { transparent: true, opacity: .6 } }), { r2: .038, cast: false }); }
      cyl('ashtray', 'glass', .06, .025, [-3.3, 4.5, .76], std('#8a8a80', { rough: .3 }));
      cyl('coat_stand', 'wood', .025, 1.8, [-4.5, 5.5, 0], BW); cyl('coat_stand_foot', 'wood', .18, .04, [-4.5, 5.5, 0], BW);
      for (let k = 0; k < 4; k++) { const a = k * 1.57; cyl('coat_hook', 'metal', .008, .14, [-4.5 + Math.cos(a) * .06, 5.5 + Math.sin(a) * .06, 1.72], BRASS); }
      add(new THREE.Mesh(lumpGeo(.2, .5, .14, .1, 3), std('#3a3a44', { rough: .9 })), 'coat_hanging', 'cloth').position.copy(V(-4.42, 5.45, 1.25));
      cyl('hat_crown', 'cloth', .1, .11, [-4.5, 5.5, 1.8], std('#2a2420', { rough: .85 })); cyl('hat_brim', 'cloth', .17, .015, [-4.5, 5.5, 1.8], std('#2a2420', { rough: .85 }));
      for (const [y, w, h, c] of [[1.6, .5, .4, '#6a7a5a'], [3.4, .4, .55, '#8a6a4a']]) { box('picture_frame', 'wood', .04, w + .08, h + .08, [-4.86, y, 1.6], metal('brass', '#8a6a2a', { rough: .5 }));
        box('picture', 'cloth', .02, w, h, [-4.84, y, 1.64], std(c, { rough: .8 })); }
    }
    if (Z === 'field') {
      const GRAN = relief('stone', '#9a958a', { seed: 141, size: .8 }), OAK = relief('wood', '#7a6a4e', { seed: 142 }), MUD = relief('mud', '#4e4030', { seed: 143, size: 2 });
      // granite gateposts where the lane passes the hedge, and an old five-bar gate swung open against it
      for (const x of [-9.4, -4.6]) { box('gatepost', 'stone', .4, .4, 1.6, [x, 14, 0], GRAN); box('gatepost_cap', 'stone', .48, .48, .1, [x, 14, 1.6], GRAN); }
      { const g = new THREE.Group(); g.position.copy(V(-9.2, 13.6, 0)); g.rotation.y = 2.6; scene.add(g);
        for (let i = 0; i < 5; i++) { const b = add(new THREE.Mesh(new THREE.BoxGeometry(3.0, .09, .05), OAK), 'gate_bar', 'wood', { parent: g }); b.position.set(1.5, .25 + i * .26, 0); }
        for (const x of [.05, 1.5, 2.95]) { const s = add(new THREE.Mesh(new THREE.BoxGeometry(.1, 1.3, .06), OAK), 'gate_stile', 'wood', { parent: g }); s.position.set(x, .7, 0); }
        const br = add(new THREE.Mesh(new THREE.BoxGeometry(3.2, .08, .05), OAK), 'gate_brace', 'wood', { parent: g }); br.position.set(1.5, .75, .01); br.rotation.z = .36; }
      // wheel ruts down the lane, with rain left in them
      for (const x of [-7.75, -6.25]) { const r = add(new THREE.Mesh(new THREE.PlaneGeometry(.46, 130), MUD), 'lane_rut', 'ground', { cast: false, mat: 'mud' }); r.rotation.x = -Math.PI / 2; r.position.copy(V(x, 35, .015)); }
      /* (no rut puddles: in daylight they mirrored the blue sky and read as a blue plank on the lane) */
      // the grass crown between the ruts (a Normandy lane), clear of the riders' line only where the bikes cross it
      { const sv = seed; for (const y of [-14, 2, 18, 34]) dropInstances(meadow({ name: 'lane_crown', at: [-7, y], radius: 8.5, count: 2600, height: .22, tints: ['#8a9a50', '#7a8c48', '#9aa85a'] }), (x) => Math.abs(x + 7) > .3); seed = sv; }   /* meadow draws from the main stream: restored so nothing else moves */
      // leaf skin on the hedge clumps: sprig cards over each clump's outer surface, so the bocage silhouette breaks into leaves instead of smooth balls
      { const tex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
          for (let i = 0; i < 9; i++) { const a = i / 9 * 6.283 + rr2(-.2, .2), d = rr2(14, 40), x = 64 + Math.cos(a) * d, y = 64 + Math.sin(a) * d, v = rr2(170, 255) | 0;
            g.save(); g.translate(x, y); g.rotate(a); g.fillStyle = `rgb(${v},${v},${v})`; g.beginPath(); g.ellipse(0, 0, 20, 10, 0, 0, 6.283); g.fill(); g.strokeStyle = `rgba(0,0,0,.25)`; g.lineWidth = 1.5; g.beginPath(); g.moveTo(-18, 0); g.lineTo(18, 0); g.stroke(); g.restore(); }
          const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
        const cg = new THREE.PlaneGeometry(1, 1), cm = new THREE.MeshStandardMaterial({ map: tex, alphaTest: .5, side: THREE.DoubleSide, roughness: .85 });
        const src = []; scene.traverse(o => { if (o.isInstancedMesh && /^hedge_clumps/.test(o.name)) src.push(o); });
        const K = 34, M4 = new THREE.Matrix4(), M5 = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3(), C = new THREE.Color(), D = new THREE.Vector3(), up = new THREE.Vector3(0, 0, 1);
        let total = 0; for (const im of src) total += im.count * K; const leaf = new THREE.InstancedMesh(cg, cm, total); let k = 0;
        for (const im of src) for (let i = 0; i < im.count; i++) { im.getMatrixAt(i, M4); M4.decompose(P, Q, S); if (im.instanceColor) im.getColorAt(i, C); else C.set('#4d7a30'); const r = S.x;
          for (let j = 0; j < K; j++) { D.set(rr2(-1, 1), rr2(-.35, 1), rr2(-1, 1)).normalize(); const q = new THREE.Quaternion().setFromUnitVectors(up, D.clone().add(new THREE.Vector3(rr2(-.5, .5), rr2(-.5, .5), rr2(-.5, .5))).normalize());
            q.multiply(new THREE.Quaternion().setFromAxisAngle(up, rr2(0, 6.283))); const sz = r * rr2(.32, .5); M5.compose(P.clone().addScaledVector(D, r * rr2(.88, 1.04)), q, new THREE.Vector3(sz, sz, sz)); leaf.setMatrixAt(k, M5);
            leaf.setColorAt(k++, C.clone().offsetHSL(rr2(-.012, .012), rr2(-.05, .05), rr2(-.05, .05) + .06 * Math.max(0, D.y))); } }
        leaf.castShadow = true; leaf.receiveShadow = true; add(leaf, 'hedge_leaf_cards', 'foliage', { mat: 'foliage' }); }
      // a milk-churn stand by the lane, a log, hay bales by the farm, a dry-stone wall, molehills in the meadow
      box('churn_stand', 'wood', 1.2, .7, .08, [-10.0, 4.0, .7], OAK); for (const sx of [-.5, .5]) for (const sy of [-.28, .28]) box('churn_stand_leg', 'wood', .08, .08, .7, [-10.0 + sx, 4.0 + sy, 0], OAK);
      for (const dx of [-.3, .3]) { cyl('milk_churn', 'metal', .17, .5, [-10.0 + dx, 4.0, .78], metal('steel', '#b8bcb8', { rough: .45, finish: 'brushed' }), { r2: .13 }); cyl('churn_lid', 'metal', .1, .07, [-10.0 + dx, 4.0, 1.28], metal('steel', '#a8aca8', { rough: .4 })); }
      const lg = cyl('fallen_log', 'wood', .22, 3.2, [-12.5, 9.5, .2], relief('bark', '#5a4a36', { seed: 144 }), { r2: .19 }); lg.rotation.set(0, .5, Math.PI / 2); lg.position.copy(V(-12.5, 9.5, .22));
      for (const [x, y, s] of [[19, 30, 1], [20.4, 31, 1], [19.7, 30.6, 2.0]]) { const b = cyl('hay_bale', 'foliage', .7, 1.2, [x, y, s > 1 ? 1.4 : 0], relief('grass', '#c8a85e', { seed: 145 })); b.rotation.set(Math.PI / 2, 0, rr2(0, 3)); b.position.copy(V(x, y, s > 1 ? 2.1 : .7)); }
      { const L = []; for (let x = 15; x < 32; x += .45) for (let z = 0; z < 3; z++) L.push({ at: [x + rr2(-.1, .1), 28 + rr2(-.08, .08), .18 + z * .3], ry: rr2(0, 3), rz: rr2(-.3, .3), s: [rr2(.24, .34), rr2(.14, .2), rr2(.2, .3)], c: ['#8e897e', '#a29c90', '#7c776c'][Math.floor(rr2(0, 3))] });
        inst('drystone_wall', 'stone', new THREE.DodecahedronGeometry(1, 0), std('#ffffff', { rough: .95 }), L); }
      { const L = []; for (let i = 0; i < 16; i++) { let x, y; do { x = rr2(-4, 26); y = rr2(4, 30); } while (Math.abs(x + 7) < 3.5 || Math.hypot(x - 5, y + 3.6) < 6 || Math.hypot(x + 1.6, y - 2.1) < 2.5); L.push({ at: [x, y, 0], ry: rr2(0, 3), s: [rr2(.16, .26), rr2(.08, .12), rr2(.16, .26)], c: '#5a4632' }); }
        inst('molehill', 'ground', new THREE.SphereGeometry(1, 10, 6, 0, 6.29, 0, 1.6), relief('mud', '#ffffff', { seed: 146 }), L, { cast: false }); }
    }
    if (Z === 'road') {
      const KERB = relief('stone', '#6a6a66', { seed: 151, size: .7 }), WOOD = relief('wood', '#4a3e30', { seed: 152 }), LIME = relief('plaster', '#c8c4b8', { seed: 153 });
      // granite kerbs along both edges of the cobbles
      { const L = []; for (const sx of [-2.6, 2.6]) for (let y = -12; y < 150; y += .9) L.push({ at: [sx + rr2(-.02, .02), y, .06], ry: rr2(-.03, .03), s: [.22, .12, .86], c: ['#6e6e6a', '#626260', '#7a7872'][Math.floor(rr2(0, 3))] });
        inst('kerb_stone', 'stone', new THREE.BoxGeometry(1, 1, 1), KERB, L); }
      // a roadside calvary (stone cross on steps), a milestone, a rail fence on the left verge, a far farm with one lit window
      { const at = [-4.4, 13]; box('calvary_step', 'stone', 1.4, 1.4, .25, [at[0], at[1], 0], LIME); box('calvary_step', 'stone', 1.0, 1.0, .25, [at[0], at[1], .25], LIME); box('calvary_shaft', 'stone', .26, .26, 3.0, [at[0], at[1], .5], LIME); box('calvary_arm', 'stone', .9, .2, .2, [at[0], at[1], 2.9], LIME);
        add(new THREE.Mesh(new THREE.TorusGeometry(.32, .03, 6, 24), LIME), 'calvary_ring', 'stone').position.copy(V(at[0], at[1] - .02, 3.0)); }
      box('milestone', 'stone', .4, .22, .6, [2.95, 7.5, 0], LIME); cyl('milestone_cap', 'stone', .2, .22, [2.95, 7.5, .6], std('#8a3028', { rough: .7 }), { seg: 16 }).rotation.x = 0;
      for (let y = -8; y < 70; y += 2.4) { cyl('fence_post', 'wood', .06, 1.1, [6.4 + rr2(-.05, .05), y, 0], WOOD); }   /* right verge: on the left it ran down the lens line of the low road shot and read as rails */
      for (const z of [.5, .95]) for (let y = -8; y < 67; y += 2.4) { const r = box('fence_rail', 'wood', .05, 2.45, .06, [6.4, y + 1.2, z], WOOD); r.rotation.x = rr2(-.04, .04); }
      { const g = farmhouse([-26, 46, 0], .35); const w = add(new THREE.Mesh(new THREE.PlaneGeometry(.88, 1.08), basic('#ffb860', { fog: false })), 'lit_window', 'lamp', { cast: false, parent: g }); w.position.set(0, 2.4, 3.08);
        g.updateMatrixWorld(true); glow('#ffb860', 2.4, .55, w.getWorldPosition(new THREE.Vector3()).addScaledVector(new THREE.Vector3(0, 0, 1).applyQuaternion(g.quaternion), .3)); }
      // wet fallen leaves on the cobbles and in the gutters
      { const L = []; for (let i = 0; i < 700; i++) { const gut = r2() < .6, x = gut ? (r2() < .5 ? -1 : 1) * rr2(2.0, 2.45) : rr2(-2.3, 2.3); L.push({ at: [x, rr2(-8, 60), .02 + r2() * .006], rx: -Math.PI / 2, rz: rr2(0, 6.3), s: [rr2(.05, .09), rr2(.03, .06), 1], c: ['#5a3a1e', '#6a4a20', '#3e2a16', '#7a5a2a'][Math.floor(rr2(0, 4))] }); }
        inst('fallen_leaf', 'foliage', new THREE.CircleGeometry(1, 6), std('#ffffff', { rough: .35, extra: { side: THREE.DoubleSide } }), L, { cast: false }); }
    }
  }
  if (Z === 'photo') {
    room(7, 6, 3.0, '#5a5e60', 'stone', '#4a4c4e', { wallMat: blockPaint, ceilMat: std('#4e5254', { rough: .95 }) });
    { const GM = metal('iron', '#5a6058', { rough: .55 });   // filing cabinet, a pinboard of photos, a desk lamp, stacked prints, a hanging shade
      box('filing_cabinet', 'metal', .5, .6, 1.3, [-3.0, 3.4, 0], GM); for (let i = 0; i < 4; i++) box('drawer_front', 'metal', .44, .02, .26, [-3.0, 3.09, .12 + i * .31], GM);
      box('pinboard', 'wood', 1.4, .04, .9, [-1.8, 3.97, 1.5], relief('wood', '#a88a5a', { seed: 121 })); for (let i = 0; i < 8; i++) box('pinned_photo', 'cloth', .22, .01, .17, [-2.35 + (i % 4) * .36, 3.94, 1.25 + (i >> 2) * .4], std(i % 3 ? '#9a9a90' : '#7a7a72'));
      for (let i = 0; i < 5; i++) box('print_stack', 'cloth', .3, .24, .015, [.85 + i * .01, 1.25, .93 + i * .016], std('#c8c8c0'), { rot: rr(-.2, .2) });
      cyl('lamp_shade', 'metal', .3, .25, [0, 1.6, 2.4], GM, { r2: .08 }); cyl('lamp_cord', 'metal', .01, .4, [0, 1.6, 2.65], std('#1a1a1a')); }
    const lt = prop('light_table', 'light_table', 'lamp', [0, 1.6, 0], 0, { table_glass: basic('#c8d6e8'), metal_dark: metal('iron', '#3a3a36', { rough: .5 }), brass: metal('brass', '#c8a24a', { rough: .3 }), chrome: metal('steel', '#c8c8c0', { rough: .25 }) });   /* V3: Blender table (frame, legs, braces, lamp box, drawers, stereoscope, pencil tray); the frosted top glows */
    const photoTex = canvasTex(512, 384, (g, w, h) => { g.fillStyle = '#8a8a80'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${rnd() * 60 | 0},${rnd() * 60 | 0},${rnd() * 50 | 0},.08)`; g.fillRect(rnd() * w, rnd() * h, 3, 3); } g.fillStyle = '#3a3a34'; for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { const x = 40 + c * 75, y = 60 + r * 80; g.fillRect(x, y, 36, 22); g.fillRect(x + 30, y + 9, 20, 4); g.fillStyle = 'rgba(30,25,20,.5)'; g.fillRect(x + 4, y + 24, 4, 50); g.fillRect(x + 26, y + 24, 4, 50); g.fillStyle = '#3a3a34'; } });
    const ph = add(new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.0), basic('#d8d8d0', { map: photoTex })), 'aerial_photo', 'cloth', { cast: false }); ph.rotation.x = -Math.PI / 2; ph.position.copy(V(0, 1.6, .925));
    const loupe = cyl('loupe', 'glass', .09, .015, [.25, 1.5, .93], std('#9fb0bc', { rough: .05, metal: .1, extra: { transparent: true, opacity: .22, depthWrite: false } })); add(new THREE.Mesh(new THREE.TorusGeometry(.09, .012, 8, 32), metal('iron', '#2a2a26', { rough: .4 })), 'loupe_rim', 'metal').position.copy(V(.25, 1.5, .945)); scene.children[scene.children.length - 1].rotation.x = Math.PI / 2;   /* V3: a thin lens in a dark rim (a solid pale cylinder read as a white blob on the lit table) */
    const tl = new THREE.PointLight('#dfeaff', 5, 6, 1.4); tl.position.copy(V(0, 1.6, 1.3)); scene.add(tl); lamp([2.6, 3.4, 2.8], '#9fb0c8', 6, 8);
    box('river_map', 'cloth', 2.4, .04, 1.4, [0, 3.95, 1.4], basic('#ffffff', { map: canvasTex(480, 280, (g, w, h) => { g.fillStyle = '#d8d0b4'; g.fillRect(0, 0, w, h); g.strokeStyle = '#4a6ab0'; g.lineWidth = 16; g.beginPath(); g.moveTo(w * .55, 0); g.bezierCurveTo(w * .4, h * .3, w * .7, h * .6, w * .5, h); g.stroke(); g.fillStyle = '#b02a2a'; for (let i = 0; i < 12; i++) g.fillRect(w * .62 + (i % 4) * 14, h * .72 + Math.floor(i / 4) * 14, 9, 9); }) }));
    anchors = { photo: [0, 1.6, .93], loupe: [.25, 1.5, .95] };
  }
  if (Z === 'river') {
    // P7: the great river at night. SOUTH (x < 0): the decoy field under shell bursts. NORTH (x > 40): the real army crossing on pontoons in silence.
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'night-storm', seed: 71, coverage: .8, storm: { under: '#2c3a62', underAmt: .12 } })   /* V3 step 5: no orange town-glow under the clouds (read as pink clouds at night) */;
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: '#1c2744', near: 50, far: 520 });
    ground('#4a5c3a');
    farLandscape({ at: [0, 30], r0: 170, r1: 470, tints: ['#5a7040', '#6a7848', '#7a7a50', '#4e663a', '#80764e', '#62743e'], hedge: '#2a3a20', spire: 2.0 });   /* V3 step 3 */
    meadow({ name: 'meadow_river', at: [-24, 26], radius: 34, count: 4200, height: .5, patchy: true }); meadow({ name: 'meadow_river_near', at: [-8, 4], radius: 18, count: 2200, height: .4 });
    // v1 note 5: real water. Reflective (the place's own sky as env map), two layers of moving ripples (normal maps), deeper colour mid-stream, shallow and lighter at the banks
    const waveN = canvasTex(256, 256, (g, w, h) => { const im = g.createImageData(w, h), H = (x, y) => Math.sin(x * 6.283 * 3 / w + Math.sin(y * 6.283 * 2 / h) * 1.3) * .5 + Math.sin(y * 6.283 * 5 / h + x * 6.283 * 2 / w) * .3 + Math.sin((x + y) * 6.283 * 7 / w) * .2;
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const dx = H(x + 1, y) - H(x - 1, y), dy = H(x, y + 1) - H(x, y - 1), i = (y * w + x) * 4; im.data[i] = 128 + dx * 90; im.data[i + 1] = 128 + dy * 90; im.data[i + 2] = 255; im.data[i + 3] = 255; } g.putImageData(im, 0, 0); });
    waveN.colorSpace = THREE.NoColorSpace; waveN.wrapS = waveN.wrapT = THREE.RepeatWrapping; waveN.repeat.set(90, 16); const waveN2 = waveN.clone(); waveN2.needsUpdate = true; waveN2.repeat.set(23, 5);
    const WATER_ENV = 1.15; const WM = ctx.pbr ? ctx.pbr.metal('wet', { color: '#1a3346', rough: .16, env: 1.15 }) : std('#1d3b50', { rough: .3 });
    WM.normalMap = waveN; WM.normalScale = new THREE.Vector2(1.5, 1.5); if ('clearcoat' in WM) { WM.clearcoat = .35; WM.clearcoatRoughness = .2; WM.clearcoatNormalMap = waveN2; WM.clearcoatNormalScale = new THREE.Vector2(.4, .4); } WM.vertexColors = true; if ('specularIntensity' in WM) WM.specularIntensity = .22;   /* the moon glint bloomed into a white haze: keep the sky reflection, tame the light's hot spot */
    const rg = new THREE.PlaneGeometry(400, 70, 120, 24), rgp = rg.attributes.position, rcol = new Float32Array(rgp.count * 3);
    for (let i = 0; i < rgp.count; i++) { const e = 1 - Math.min(1, Math.abs(rgp.getY(i)) / 35), deep = Math.min(1, e * 2.2); rcol[i * 3] = 1.0 - .45 * deep; rcol[i * 3 + 1] = 1.0 - .38 * deep; rcol[i * 3 + 2] = 1.0 - .25 * deep; }
    rg.setAttribute('color', new THREE.BufferAttribute(rcol, 3));
    const riv = add(new THREE.Mesh(rg, WM), 'river', 'water', { cast: false, mat: 'water' }); riv.rotation.x = -Math.PI / 2; riv.position.copy(V(20, 70, .3));   /* above the ground plane, or the ground hides it */
    ups.push((f, t) => { waveN.offset.set(t * .012, t * .02); waveN2.offset.set(-t * .009, t * .013); WM.envMapIntensity = WATER_ENV; });
    // the banks: muddy slopes into the water, a foam line where they meet, reeds
    for (const [y0, dir] of [[35, 1], [105, -1]]) { const bg = new THREE.PlaneGeometry(400, 5, 100, 4), bp_ = bg.attributes.position; for (let i = 0; i < bp_.count; i++) { const v = (bp_.getY(i) + 2.5) / 5; bp_.setZ(i, .55 - .55 * v + .06 * Math.sin(bp_.getX(i) * .7)); } bg.computeVertexNormals();
      const bank = add(new THREE.Mesh(bg, relief('mud', '#4a3e2e', { seed: 170, size: 3 })), 'river_bank', 'ground', { cast: false, mat: 'mud' }); bank.rotation.x = -Math.PI / 2; bank.rotation.z = dir > 0 ? 0 : Math.PI; bank.position.copy(V(20, y0 + dir * 1.0, 0));
      const foam = add(new THREE.Mesh(new THREE.PlaneGeometry(400, .5), new THREE.MeshBasicMaterial({ map: canvasTex(512, 16, (g, w, h) => { for (let x = 0; x < w; x += 2) { g.fillStyle = `rgba(230,240,255,${(.15 + .35 * Math.random()).toFixed(2)})`; g.fillRect(x, Math.random() * 6, 2, h - 8); } }), transparent: true, depthWrite: false, opacity: .55 })), 'shore_foam', 'water', { cast: false });
      foam.rotation.x = -Math.PI / 2; foam.position.copy(V(20, y0 + dir * 1.9, .33));
      const reeds = new THREE.InstancedMesh(new THREE.CylinderGeometry(.012, .02, 1, 4), std('#5a6a3a', { rough: .9 }), 700), M4 = new THREE.Matrix4(), Q = new THREE.Quaternion();
      for (let i = 0; i < 700; i++) { const x = rr(-60, 100), h = rr(.6, 1.4); Q.setFromEuler(new THREE.Euler(rr(-.2, .2), 0, rr(-.2, .2))); M4.compose(V(x, y0 + dir * rr(-.6, 1.4), h / 2), Q, new THREE.Vector3(1, h, 1)); reeds.setMatrixAt(i, M4); } add(reeds, 'reeds', 'foliage', { cast: false }); }
    const rb = riv.geometry.attributes.position.array.slice();
    // the decoy field: rows of inflatable tanks (south)
    const decoys = decoyField('decoy_tank', -46, 18, 7, 4, 7, 8, { nets: 0, gaps: .1 });   /* V3 step 2 (was a 4x7 grid of clones) */
    /* ---- V3 steps 9-10 (2026-11-18): a LAYERED stylised burst, purely visual fiction (no weapon parameters): an incoming glowing trail,
       a brief flash (no white disc), a billowing fire envelope that cools from yellow to dark red, a smoke column that rises and spreads into a
       mushroom cap and drifts away, sparks and clods on ballistic arcs, the light on the set that flares and decays, and a scorch that stays. */
    const puffTex = canvasTex(128, 128, (g, w) => { for (let i = 0; i < 9; i++) { const x = w / 2 + rr(-18, 18), y = w / 2 + rr(-18, 18), r = rr(22, 40), gr = g.createRadialGradient(x, y, 0, x, y, r);
        gr.addColorStop(0, 'rgba(255,255,255,.55)'); gr.addColorStop(.6, 'rgba(255,255,255,.25)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
      const im = g.getImageData(0, 0, w, w); for (let i = 0; i < im.data.length; i += 4) im.data[i + 3] *= .75 + .25 * Math.random(); g.putImageData(im, 0, 0); });
    const FIRE = ['#fff4c0', '#ffd060', '#ff9a30', '#e05a1a', '#8a2a10'].map(c => new THREE.Color(c)), SMOKE0 = new THREE.Color('#5a3a26'), SMOKE1 = new THREE.Color('#4a4a4e');
    const scorchTex = canvasTex(128, 128, (g, w) => { const gr = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2); gr.addColorStop(0, 'rgba(14,10,8,.9)'); gr.addColorStop(.6, 'rgba(24,18,12,.6)'); gr.addColorStop(1, 'rgba(30,24,16,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, w); });
    function layeredBurst(P) {
      const sprite = (col, blend) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: puffTex, color: col, transparent: true, opacity: 0, depthWrite: false, blending: blend || THREE.NormalBlending, rotation: rr(0, 6.3) })); s.userData.noExport = true; s.scale.setScalar(1e-4); scene.add(s); return s; };
      const fire = Array.from({ length: 16 }, () => ({ s: sprite('#ffd060', THREE.AdditiveBlending), d: new THREE.Vector3(rr(-1, 1), rr(.2, 1.2), rr(-1, 1)).normalize(), sp: rr(.6, 1.2), sz: rr(2.2, 3.8) }));   /* V3.1: bigger envelope, it reads at phone size */
      const smoke = Array.from({ length: 22 }, (_, i) => ({ s: sprite('#5a4a3a'), h: i / 22, a: rr(0, 6.3), r: rr(.2, 1), sz: rr(3.0, 4.8), dl: rr(0, 6) }));
      const flash = sprite('#fff6d8', THREE.AdditiveBlending);
      const NS = 40, sg = new THREE.BufferGeometry(), sv = new Float32Array(NS * 3), vel = Array.from({ length: NS }, () => new THREE.Vector3(rr(-7, 7), rr(6, 15), rr(-7, 7)));
      sg.setAttribute('position', new THREE.BufferAttribute(sv, 3)); const sparks = new THREE.Points(sg, new THREE.PointsMaterial({ color: '#ffc070', size: .22, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
      sparks.frustumCulled = false; sparks.userData.noExport = true; scene.add(sparks);
      const scorch = add(new THREE.Mesh(new THREE.CircleGeometry(3.2, 24), new THREE.MeshBasicMaterial({ map: scorchTex, transparent: true, opacity: 0, depthWrite: false })), 'scorch_mark', 'fx', { cast: false });
      scorch.rotation.x = -Math.PI / 2; scorch.position.set(P.x, .03, P.z); scorch.userData.noExport = true;
      const tg = new THREE.BufferGeometry(), tv = new Float32Array(8 * 3); tg.setAttribute('position', new THREE.BufferAttribute(tv, 3));
      const trail = new THREE.Line(tg, new THREE.LineBasicMaterial({ color: '#ffd9a0', transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending })); trail.frustumCulled = false; trail.userData.noExport = true; scene.add(trail);
      const from = new THREE.Vector3(P.x + 40, 34, P.z - 70), arc = (u) => new THREE.Vector3().lerpVectors(from, P, u).add(new THREE.Vector3(0, 10 * Math.sin(Math.PI * u), 0));
      return { fire, smoke, flash, sparks, scorch, trail, update(a, light) {   /* a = frames since impact */
        // incoming trail: the 10 frames before impact, a short glowing streak running down its arc
        const u = (a + 10) / 10; trail.material.opacity = u > 0 && u < 1 ? .9 : 0; if (u > 0 && u < 1) { for (let k = 0; k < 8; k++) { const q = arc(Math.max(0, u - k * .025)); tv[k * 3] = q.x; tv[k * 3 + 1] = q.y; tv[k * 3 + 2] = q.z; } tg.attributes.position.needsUpdate = true; }
        // flash: 3 frames, small and warm
        const fl = a >= 0 && a < 4 ? 1 - a / 4 : 0; flash.position.set(P.x, P.y + 1, P.z); flash.scale.setScalar(fl ? 4 + 2.5 * (1 - fl) : 1e-4); flash.material.opacity = .85 * fl;
        // fire envelope: puffs billow out and up, cooling yellow -> orange -> dark red, gone by 1.3 s
        for (const F of fire) { const t = a / 40; if (a < 0 || t > 1) { F.s.scale.setScalar(1e-4); F.s.material.opacity = 0; continue; }
          const e = 1 - Math.pow(1 - Math.min(1, t * 2.2), 3); F.s.position.set(P.x + F.d.x * 4.2 * e * F.sp, P.y + .6 + F.d.y * 4.6 * e * F.sp + 3.2 * t, P.z + F.d.z * 4.2 * e * F.sp);
          F.s.scale.setScalar(F.sz * (.6 + 1.8 * e)); const ci = Math.min(FIRE.length - 1.001, t * (FIRE.length - 1)); F.s.material.color.copy(FIRE[Math.floor(ci)]).lerp(FIRE[Math.ceil(ci)], ci % 1); F.s.material.opacity = .8 * (1 - t) * Math.min(1, a / 2); }
        // smoke: a column that rises and spreads into a cap, lit warm from below at first, then grey; it drifts with the wind and thins out over 4 s
        for (const S of smoke) { const t = (a - 4 - S.dl) / 120; if (t <= 0 || t > 1) { S.s.scale.setScalar(1e-4); S.s.material.opacity = 0; continue; }
          const rise = 13 * (1 - Math.pow(1 - Math.min(1, t * 1.6), 2)) * (.35 + .65 * S.h), cap = S.h > .6 ? 3.8 * Math.min(1, t * 2) : .6 * t, drift = 3.5 * t;   /* V3.1: a taller column and a wider cap: the mushroom reads */
          S.s.position.set(P.x + Math.cos(S.a) * (S.r + cap) + drift, P.y + 1 + rise, P.z + Math.sin(S.a) * (S.r + cap) * .7);
          S.s.scale.setScalar(S.sz * (.7 + 1.6 * Math.min(1, t * 2)) * (S.h > .6 ? 1.45 : 1)); S.s.material.color.copy(SMOKE0).lerp(SMOKE1, Math.min(1, t * 3)); S.s.material.opacity = .62 * Math.min(1, t * 8) * (1 - t); }
        // sparks: ballistic, fading
        const ts = a / 30; sparks.material.opacity = a >= 0 && ts < 1.2 ? .95 * (1 - ts / 1.2) : 0;
        if (a >= 0 && ts < 1.2) { for (let k = 0; k < NS; k++) { sv[k * 3] = P.x + vel[k].x * ts; sv[k * 3 + 1] = Math.max(.05, P.y + .5 + vel[k].y * ts - 9.8 * ts * ts); sv[k * 3 + 2] = P.z + vel[k].z * ts; } sg.attributes.position.needsUpdate = true; }
        // the scorch stays (aftermath)
        scorch.material.opacity = a > 2 ? Math.min(.85, (a - 2) / 6) : 0;
        // light on the set: flare, flicker, decay over a second
        if (light) light.intensity = a >= 0 && a < 34 ? 70 * Math.exp(-a / 9) * (.85 + .15 * Math.sin(a * 2.3)) : 0; } };
    }
    // shell bursts on the decoys from EV.shell on: flashes + tanks thrown and deflating
    const bursts = []; for (let i = 0; i < 10; i++) { const b = glow('#ffb060', 6, 0, V(-42 + (i * 23) % 40, 20 + (i * 7) % 22, 1)); const l = new THREE.PointLight('#ffa040', 0, 40, 1.6); l.position.copy(b.position); scene.add(l); const fb = add(new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), basic('#fff2c0', { transparent: true, depthWrite: false })), 'shell_fireball', 'fx', { cast: false }); fb.position.copy(b.position); fb.userData.noExport = true; const ob = add(new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), basic('#ff7a2a', { transparent: true, depthWrite: false })), 'shell_fire_outer', 'fx', { cast: false }); ob.position.copy(b.position); const sk = []; for (let j = 0; j < 5; j++) { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#6a6660', transparent: true, opacity: .75, depthWrite: false })); sp.userData.noExport = true; sp.userData.off = [rr(-1.5, 1.5), rr(0, 2), rr(-1.5, 1.5)]; scene.add(sp); sk.push(sp); }   /* soft smoke puffs */ const clods = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.32, 0), std('#3a2e22', { rough: 1 }), 14); clods.userData.noExport = true; add(clods, 'shell_debris', 'fx', { cast: false }); const cv = Array.from({ length: 14 }, () => [rr(-5, 5), rr(7, 13), rr(-5, 5)]); bursts.push({ clods, cv, b, l, fb, ob, sk, f0: (EV.shell || 0) + i * 8, d: decoys[(i * 5) % decoys.length], L: layeredBurst(b.position.clone()) }); }   // the barrage keeps falling while the crane rises (V3: + the layered burst)
    // the real crossing (north): pontoon bridge and real (metal) tanks rolling across
    box('assault_boat', 'wood', 1.6, 3.2, .45, [57.0, 44.0, .15], relief('wood', '#4a4a36', { seed: 160 }));
    { const rip = []; for (let i = 0; i < 10; i++) { const r_ = add(new THREE.Mesh(new THREE.RingGeometry(.92, 1.0, 48), new THREE.MeshBasicMaterial({ color: '#dfe8f4', transparent: true, opacity: 0, depthWrite: false })), 'water_ripple', 'water', { cast: false }); r_.rotation.x = -Math.PI / 2; r_.userData.c = i < 4 ? [57.0, 44.0] : [60 + (i % 2 ? 1.5 : -1.5), 37 + (i - 4) * 6]; r_.userData.ph = i * .37; rip.push(r_); }
      ups.push((f, t) => { rip.forEach(r_ => { const q = (t * .35 + r_.userData.ph) % 1; r_.position.copy(V(r_.userData.c[0], r_.userData.c[1], .33)); r_.scale.setScalar(1.6 + q * 3.5); r_.material.opacity = .1 * (1 - q) * Math.min(1, q * 5); }); }); }   /* ripples round the boat and pontoons */   // the sergeant's boat beside the bridge
    for (let i = 0; i < 14; i++) { const fr_ = add(new THREE.Mesh(new THREE.RingGeometry(1.5, 1.9, 4, 1), new THREE.MeshBasicMaterial({ color: '#dfe8f4', transparent: true, opacity: .28, depthWrite: false })), 'pontoon_foam', 'water', { cast: false }); fr_.rotation.x = -Math.PI / 2; fr_.rotation.z = Math.PI / 4; fr_.scale.set(1, 1.15, 1); fr_.position.copy(V(60, 37 + i * 3.1, .32)); }
    for (let i = 0; i < 14; i++) box('pontoon', 'metal', 2.6, 3.0, .5, [60, 37 + i * 3.1, .05], metal('iron', '#3a4030', { rough: .7 }));
    box('bridge_deck', 'wood', 3.2, 44, .12, [60, 58, .55], relief('wood', '#5a4a36', { seed: 121 }));
    const real = []; for (let i = 0; i < 3; i++) { const t = sherman('real_tank', { at: [60, 30 - i * 9, 0], rot: -Math.PI / 2, col: '#4a5030' }); t.traverse(o => { if (o.isMesh && o.material.name === 'rubber_canvas') { o.material = metal('iron', '#4a5030', { rough: .65, rust: .2 }); } }); real.push(t); }
    const moon = glow('#e6eeff', 24, .9, V(120, 200, 80)); const path = add(new THREE.Mesh(new THREE.PlaneGeometry(6, 60), basic('#c8d8ff', { transparent: true, opacity: .1, depthWrite: false })), 'moon_path', 'water', { cast: false }); path.rotation.x = -Math.PI / 2; path.position.copy(V(70, 70, .38)); path.visible = false;   /* the moon's real reflection (env map) replaces the painted strip */ const ml = new THREE.DirectionalLight('#b4c6ff', 3.2); scene.add(new THREE.HemisphereLight('#7c90c8', '#33402c', 3.2));   /* night never under mean 0.31 (11c) */    // moonlight pools on the silent crossing (north)
    for (const [x, y] of [[-40, 14], [-37, 9], [-12, 14], [-33, 36], [-19, 38]])   /* V3.1: the lamp at (-26, 16) stood across the closer strike framing */ { const wl = new THREE.PointLight('#ffcf8a', 30, 26, 1.6); wl.position.copy(V(x, y, 4)); scene.add(wl); glow('#ffcf8a', 1.4, .9, V(x, y, 4)); cyl('work_lamp_pole', 'metal', .06, 4, [x, y, 0], metal('iron', '#3a3a34')); } ml.position.copy(V(-40, -60, 70));   /* key from the camera side: the moon glint off the water bloomed into a haze */ scene.add(ml);
    decoys.forEach((t, i) => { t.userData.i0 = (EV.inflate || 0) + i * 2; });
    ups.push((f, t) => {
      decoys.forEach(t => { if (t.position.y > .01) return; const u = sm((f - t.userData.i0) / 12), s0 = t.userData.s0 || 1; t.visible = u > .02; t.scale.set(s0, s0 * Math.max(.05, u) * (1 - .45 * (t.userData.sagV || 0)), s0); });
      const p = riv.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const x = rb[i * 3], y = rb[i * 3 + 1]; p.setZ(i, .05 * Math.sin(.2 * x + 1.4 * t) + .03 * Math.sin(.31 * y - 1.1 * t)); } p.needsUpdate = true; riv.geometry.computeVertexNormals();
      for (const B of bursts) { const k = (f - B.f0) / 22, on = k > 0 && k < 1 ? (k < .15 ? .85 * k / .15 : .85 * Math.pow((1 - k) / .85, 1.5)) : 0;   // 3-frame build, then a slow fall; softer peak (no white-out)
        B.b.material.opacity = .4 * on; B.b.scale.setScalar(5 + 6 * Math.max(0, Math.min(1, k))); B.l.intensity = 60 * on; const kk = Math.max(0, Math.min(1, k)); B.fb.scale.setScalar(on > .02 ? (1.2 + 2.2 * kk) * Math.sqrt(on) : 1e-4); B.ob.scale.setScalar(on > .02 ? (2.4 + 4.6 * kk) : 1e-4); B.fb.material.opacity = Math.min(1, on * 1.3); B.ob.material.opacity = .8 * on;   /* a hot core inside a fading orange shell, not a solid ball */ B.ob.position.y = B.b.position.y + 1.2 * kk;
        const sm_ = (f - B.f0) / 60; B.sk.forEach(sp => { const o = sp.userData.off; sp.position.set(B.b.position.x + o[0] * (1 + sm_), B.b.position.y + 1.5 + o[1] + 5 * Math.max(0, sm_), B.b.position.z + o[2] * (1 + sm_)); sp.scale.setScalar(sm_ > .1 && sm_ < 1.8 ? 4 + 6 * Math.min(1, sm_) : 1e-4); sp.material.opacity = .7 * Math.max(0, 1 - sm_ / 1.8); });   // smoke rises after the flash
        B.fb.material.color.set(on > .5 ? '#fff0b0' : '#ff9a40');
        /* V3 step 9: the old sphere fireball, orange shell, wide glow disc and round smoke puffs are retired; the layered burst draws the event */
        B.fb.visible = B.ob.visible = false; B.b.material.opacity = 0; B.sk.forEach(sp => { sp.visible = false; }); B.L.update(f - B.f0, B.l);
        { const ts = (f - B.f0) / 30, M4 = new THREE.Matrix4(); for (let j = 0; j < 14; j++) { const v_ = B.cv[j], live = ts > 0 && ts < 2.2; const x = B.b.position.x + v_[0] * ts, y = Math.max(.1, B.b.position.y - 1 + v_[1] * ts - 4.9 * ts * ts), z = B.b.position.z + v_[2] * ts;
          M4.makeScale(live ? 1 : 1e-4, live ? 1 : 1e-4, live ? 1 : 1e-4).setPosition(x, y, z); B.clods.setMatrixAt(j, M4); } B.clods.instanceMatrix.needsUpdate = true; }   /* debris: earth thrown up and falling back */
        if (k > 0) { const q = Math.min(1, k * 1.5); B.d.userData.set(.8 * q, .6 * q); B.d.position.y = Math.max(0, Math.sin(Math.min(1, k) * Math.PI) * 4); B.d.rotation.z = q * .6; } }
      const go = sm((f - (EV.cross || 0)) / 140); real.forEach((t, i) => { t.position.copy(V(60, 30 - i * 9 + go * 60, .67)); });
    });
    anchors = { decoys: [-25, 30, 1], bridge: [60, 58, 0] };
  }
  if (Z === 'bedroom') {
    room(5, 5, 2.8, '#7a8ab4', 'wood', '#6a5a46', { win: [1.2, 1.1, 1.2, 1.2], wallMat: roomPaper, ceilMat: std('#c4c8dc', { rough: .95 }), skirting: relief('wood', '#ece4d4', { seed: 135 }) });
    const BW = relief('wood', '#6a4a2e', { seed: 131 });   // v1 note 6: a real bed - frame, posts, headboard, mattress, sheet, a quilted blanket draped in folds, pillow, nightstand, rug, a wooden toy tank
    box('bed_frame', 'wood', 1.2, 2.1, .3, [-.8, 2.2, .1], BW); for (const sx of [-.57, .57]) for (const sy of [1.2, 3.2]) box('bed_post', 'wood', .08, .08, sy > 2 ? 1.1 : .7, [-.8 + sx, sy, 0], BW);
    box('headboard', 'wood', 1.2, .06, .6, [-.8, 3.2, .4], BW); box('mattress', 'cloth', 1.1, 1.95, .16, [-.8, 2.2, .4], std('#e8e4d8', { rough: .95 })); box('sheet_fold', 'cloth', 1.14, .3, .03, [-.8, 2.95, .56], std('#f4f2ea', { rough: .9 }));
    const quiltTex0 = canvasTex(256, 256, (g, w, h) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = ['#7a5a48', '#e6dcc0', '#9aa47a', '#c8a868', '#a85a4a', '#e6dcc0'][(x + y * 3) % 6]; g.fillRect(x * 32, y * 32, 32, 32); g.strokeStyle = 'rgba(40,40,60,.35)'; g.strokeRect(x * 32 + 2, y * 32 + 2, 28, 28); } });
    const quiltTex = quiltTex0; quiltTex.wrapS = quiltTex.wrapT = THREE.RepeatWrapping; quiltTex.repeat.set(1.6, 2.2);
    const qg = new THREE.PlaneGeometry(1.3, 1.75, 26, 34), qp = qg.attributes.position; for (let i = 0; i < qp.count; i++) { const x = qp.getX(i), y = qp.getY(i), edge = Math.max(0, Math.abs(x) - .55) / .1; qp.setZ(i, .05 * Math.sin(y * 9 + x * 3) * Math.cos(x * 7) - .32 * Math.min(1, edge) * Math.min(1, edge)); } qg.computeVertexNormals();
    const blanket = add(new THREE.Mesh(qg, new THREE.MeshStandardMaterial({ map: quiltTex, roughness: .95, side: THREE.DoubleSide })), 'blanket', 'cloth'); blanket.rotation.x = -Math.PI / 2; blanket.position.copy(V(-.8, 1.95, .6));
    box('pillow', 'cloth', .6, .35, .14, [-.8, 3.0, .56], std('#f4f2ea', { rough: .95 }));
    box('nightstand', 'wood', .45, .4, .55, [.0, 3.0, 0], BW); cyl('bedside_lamp', 'cloth', .12, .2, [.0, 3.0, .75], std('#e8d8a8', { rough: .8 }), { r2: .07 }); cyl('lamp_stem', 'metal', .015, .2, [.0, 3.0, .55], metal('brass', '#c8a24a')); box('book', 'cloth', .16, .22, .04, [.12, 2.9, .55], std('#7a2a2a'));
    box('rug', 'cloth', 1.4, .9, .01, [.2, 1.2, 0], std('#ffffff', { extra: { map: canvasTex(200, 130, (g, w, h) => { g.fillStyle = '#8a3a2a'; g.fillRect(0, 0, w, h); g.strokeStyle = '#e8c890'; g.lineWidth = 6; g.strokeRect(10, 10, w - 20, h - 20); g.strokeStyle = '#2a3a5a'; g.lineWidth = 3; g.strokeRect(24, 24, w - 48, h - 48); }) } }));
    { const toy = sherman('toy_tank', { at: [.5, 1.5, .01], rot: .6, scale: .07, col: '#6a7a3a' }); }
    box('wardrobe', 'wood', 1.0, .55, 1.9, [-2.1, .4, 0], BW); box('wardrobe_door_line', 'wood', .02, .01, 1.7, [-2.1, .12, .1], std('#2a1a10'));
    for (const sx of [-.75, .75]) { const cu = add(new THREE.Mesh(new THREE.PlaneGeometry(.35, 1.5, 6, 1), new THREE.MeshStandardMaterial({ color: '#e8d8b0', roughness: .9, side: THREE.DoubleSide })), 'curtain', 'cloth'); cu.position.copy(V(1.2 + sx, 2.86, 1.65)); ups.push((f, t) => { cu.rotation.y = .12 * Math.sin(t * 1.1 + sx); }); }
    const plump = add(new THREE.Mesh(new THREE.SphereGeometry(.5, 20, 12), new THREE.MeshStandardMaterial({ map: quiltTex, roughness: .95 })), 'pillow_lump', 'cloth'); plump.scale.set(.62, .34, 1.15); plump.position.copy(V(-.8, 2.0, .66));
    { const WF = relief('wood', '#ece4d4', { seed: 132 });   // an open window: four bars round the hole, no pane
      box('window_frame', 'wood', 1.4, .14, .1, [1.2, 2.9, 1.0], WF); box('window_frame', 'wood', 1.4, .14, .1, [1.2, 2.9, 2.3], WF);
      box('window_frame', 'wood', .1, .14, 1.4, [.55, 2.9, 1.0], WF); box('window_frame', 'wood', .1, .14, 1.4, [1.85, 2.9, 1.0], WF); } box('window_sill', 'wood', 1.4, .3, .08, [1.2, 3.0, 1.06], relief('wood', '#ece4d4', { seed: 133 }));
    box('night_garden', 'plaster', 9, .1, 6, [1.2, 7.5, 0], basic('#22305e'), { cast: false });   // the night outside, seen through the window
    box('garden_crate', 'wood', .7, .6, .6, [1.3, 3.8, 0], relief('wood', '#5a4630', { seed: 134 }));   // the boy stands on it, outside
    glow('#f4f0d8', .35, .9, V(2.6, 7.3, 3.6));
    const hemi = new THREE.HemisphereLight('#9fb4ff', '#3a3040', 1.6); scene.add(hemi);
    const out = new THREE.PointLight('#b8ccff', 10, 6, 1.5); out.position.copy(V(1.0, 5.2, 2.4)); scene.add(out);
    const sheets = add(new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, 2.4, 8), std('#ece8de')), 'rope_of_sheets', 'cloth'); sheets.position.copy(V(1.4, 2.9, .2)); sheets.rotation.x = .25;
    const ml = new THREE.SpotLight('#a8c0ff', 30, 12, .6, .7); ml.position.copy(V(1.4, 5, 2.6)); ml.target.position.copy(V(-.8, 2.0, .5)); scene.add(ml, ml.target);
    /* V3 step 4: the boy's room lived in - a chair with clothes, a shelf with books and a toy plane, framed pictures, a clock, slippers, a chest at the bed foot */
    box('wall_shelf', 'wood', 1.0, .22, .03, [-2.0, 2.0 + .9, 1.55], BW); for (let i = 0; i < 7; i++) box('shelf_book', 'cloth', .05 + rnd() * .03, .17, .2 + rnd() * .06, [-2.4 + i * .085, 2.9, 1.57], std(['#7a2a24', '#2a4a6a', '#5a6a3a', '#c8a868', '#4a3a5a'][i % 5], { rough: .8 }));
    { const pl = new THREE.Group(); pl.position.copy(V(-1.75, 2.9, 1.66)); scene.add(pl); pl.name = 'toy_plane'; const PM = std('#9aa0a6', { rough: .5 });
      add(new THREE.Mesh(lumpGeo(.12, .025, .025, .02, 2), PM), 'toy_plane_body', 'wood', { parent: pl }); const wg = add(new THREE.Mesh(new THREE.BoxGeometry(.03, .004, .26), PM), 'toy_plane_wing', 'wood', { parent: pl }); wg.position.x = .02; }
    for (const [x, z, w, h, c] of [[-1.6, 1.75, .3, .38, '#5a6a8a'], [-1.15, 1.85, .24, .3, '#8a6a4a']]) { box('picture_frame', 'wood', w, .025, h, [x, 3.18, z], BW); box('picture', 'cloth', w - .06, .005, h - .06, [x, 3.165, z], std(c, { rough: .7 })); }
    cyl('wall_clock', 'wood', .14, .04, [.6, 3.18, 2.05], BW, { rx: Math.PI / 2 }); cyl('clock_face', 'cloth', .12, .005, [.6, 3.155, 2.05], std('#f0ead8'), { rx: Math.PI / 2 });
    box('chair_seat', 'wood', .4, .4, .04, [.55, 2.3, .42], BW); for (const sx of [-.17, .17]) for (const sy of [-.17, .17]) box('chair_leg', 'wood', .03, .03, .42, [.55 + sx, 2.3 + sy, 0], BW); box('chair_back', 'wood', .4, .03, .45, [.55, 2.49, .45], BW);
    lump('folded_clothes', 'cloth', lumpGeo(.18, .06, .14, .1, 7), std('#3a4a6a', { rough: .95 }), [.55, 2.3, .5]); lump('hung_jumper', 'cloth', lumpGeo(.2, .2, .04, .12, 8), std('#8a3a2a', { rough: .95 }), [.55, 2.52, .7]);
    box('bed_chest', 'wood', 1.0, .4, .4, [-.8, 1.0, 0], relief('wood', '#5a3a26', { seed: 136 })); for (const sx of [-.35, .35]) lump('slipper', 'cloth', lumpGeo(.06, .03, .12, .05, sx * 9), std('#6a4a3a', { rough: .95 }), [.05 + sx * .3, 1.55, .02]);
    ups.push((f, t) => { plump.scale.y = .34 + .025 * Math.sin(t * 1.5); });
    anchors = { bed: [-.8, 2.0, .8], window: [1.2, 2.96, 1.2] };
  }
  if (Z === 'attic') {
    room(7, 7, 3.4, '#8a7058', 'wood', '#7a5a3e', { wallKind: 'wood', noCeil: true });
    { const AW = relief('wood', '#6a5038', { seed: 160 });   // v1 note 6: roof boards between the rafters, collar ties, cardboard boxes, an old chair, framed photos, a helmet on the trunk, a dormer window
      for (const s of [-1, 1]) { const rb = box('roof_boards', 'wood', 7, 7, .04, [0, 1.5, 3.3], AW); rb.rotation.z = 0; }
      for (let i = 0; i < 6; i++) box('collar_tie', 'wood', .12, .12, .12, [-3 + i * 1.2, 1.5, 2.5], AW);
      for (const [x, y, w, h] of [[-2.4, 3.8, .6, .45], [-1.8, 4.0, .5, .4], [-2.2, 3.9, .45, .35], [2.2, 4.1, .7, .5]]) { box('cardboard_box', 'cloth', w, w * .8, h, [x, y, 0], std('#b08a5a', { rough: .95 })); box('box_tape', 'cloth', w + .01, .06, h + .01, [x, y, 0], std('#c8b080')); }
      box('old_chair_seat', 'wood', .45, .45, .04, [2.3, 2.6, .45], AW); for (const sx of [-.2, .2]) for (const sy of [-.2, .2]) box('chair_leg', 'wood', .04, .04, .45, [2.3 + sx, 2.6 + sy, 0], AW); box('chair_back', 'wood', .45, .04, .5, [2.3, 2.8, .5], AW);
      for (let i = 0; i < 3; i++) box('framed_photo', 'wood', .3, .03, .24, [-1.4 + i * .5, 5.4, 1.3 + (i % 2) * .3], std(['#3a3026', '#4a3a2a', '#2a2420'][i]));
      cyl('old_helmet', 'metal', .17, .12, [.35, 2.1, .78], metal('iron', '#4d5634', { rough: .7, rust: .3 }), { r2: .1 }); }
    for (let i = 0; i < 6; i++) box('roof_rafter', 'wood', .2, 7, .25, [-3 + i * 1.2, 1.5, 3.0], relief('wood', '#5a4030', { seed: 141 + i }));
    box('ridge_beam', 'wood', 7, .3, .3, [0, 1.5, 3.25], relief('wood', '#4a3424', { seed: 149 })); for (const x of [-2.6, 2.6]) box('attic_post', 'wood', .22, .22, 3.0, [x, 3.6, 0], relief('wood', '#4a3424', { seed: 150 }));
    const trunk = box('trunk', 'wood', 1.3, .7, .65, [0, 2.0, 0], relief('wood', '#6a4630', { seed: 151 })); const lid = box('trunk_lid', 'wood', 1.3, .7, .1, [0, 2.0, .65], relief('wood', '#5a3a26', { seed: 152 }));
    box('medal_box', 'cloth', .3, .2, .08, [.9, 1.6, 0], std('#1a2a5a')); box('old_sketchbook', 'cloth', .4, .3, .05, [-.9, 1.7, 0], std('#7a5a3a'));
    { const shaft = add(new THREE.Mesh(new THREE.CylinderGeometry(.22, .8, 4.6, 24, 1, true), new THREE.MeshBasicMaterial({ color: '#ffd9a0', transparent: true, opacity: .035, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending })), 'light_shaft', 'fx', { cast: false });
      shaft.position.copy(V(-1.6, .6, 2.0)); shaft.rotation.z = .55; shaft.rotation.x = -.25; shaft.userData.noExport = true; ups.push((f, t) => { shaft.material.opacity = .032 + .006 * Math.sin(t * .7); });   /* V3: was .065 over a 1.3 m cone: a milky veil over the shot */ }   /* the window light the dust motes float in (story bible P9) */
    const skin = sherman('deflated_skin', { at: [0, 1.9, .55], scale: .22 }); skin.userData.set(.9, .85);
    scene.add(new THREE.HemisphereLight('#ffe2b8', '#4a3424', 1.6)); const sun = new THREE.SpotLight('#ffd9a0', 40, 16, .55, .6); sun.position.copy(V(-3, -1, 4)); sun.target.position.copy(V(0, 2, 0)); scene.add(sun, sun.target);
    const motes = []; for (let i = 0; i < 40; i++) motes.push(glow('#ffe6b0', rr(.03, .07), .6, V(rr(-2, 1), rr(0, 3), rr(.5, 3))));
    ups.push((f, t) => { motes.forEach((m, i) => { m.position.y += Math.sin(t * .5 + i) * .0008; m.position.x += Math.cos(t * .3 + i) * .0006; });
      const up = sm((f - (EV.lift_skin || 1e9)) / 40); skin.position.copy(V(.72 * up, 1.9 - .25 * up, .55 + up * .75));   /* animation audit: it rose beside her; now it lifts into her raised hands */ skin.userData.set(.9 * (1 - up), .85 * (1 - up)); skin.scale.setScalar(.22 + up * .05); });
    anchors = { trunk: [0, 2.0, .8] };
  }

  const update = (f, t) => { for (const u of ups) u(f, t); };
  return { update, anchors };
}
