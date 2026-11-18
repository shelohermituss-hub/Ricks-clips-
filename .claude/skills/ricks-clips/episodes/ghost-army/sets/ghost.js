// THE GHOST ARMY — one set module for every place of the film (set-builder + props-hero, rough board v1, 2026-11-17).
// film.json places.<name> = { "set": "ghost", "zone": "field" | "camp" | "road" | "radio" | "cafe" | "photo" | "river" | "bedroom" | "attic", "light": ... }.
// Each place is its own three.js scene; every zone is built round the origin. Plan coordinates: metres, Z up, Y away from the first camera.
// Hero objects are built here in code (the Asset Hub refuses military models on purpose): the INFLATABLE SHERMAN (rubberised canvas, valve,
// patch, track-print skirt), the SOUND HALF-TRACK (giant speaker horn, disc turntable), the cargo truck, the bulldozer with its track-mark beam.
// Story events come from places.<name>.events (frames). Real models (CC-BY, Sketchfab via Asset Hub) come in through places.<name>.assets.
export function build(THREE, scene, film, ctx) {
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
  function sherman(name, opts = {}) {
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
    p('ht_bed', new THREE.BoxGeometry(3.2, 1.0, 2.1), OD, -1.0, 1.25, 0); p('ht_hood', new THREE.BoxGeometry(1.7, .8, 1.6), OD, 1.6, 1.2, 0);
    p('ht_cab', new THREE.BoxGeometry(1.1, .6, 2.0), OD, .5, 1.55, 0); p('ht_windshield', new THREE.BoxGeometry(.06, .5, 1.8), std('#7f93a3', { rough: .2 }), 1.0, 2.05, 0);
    p('ht_bumper', new THREE.BoxGeometry(.2, .25, 2.2), DARK, 2.5, .8, 0);
    for (const s of [-1, 1]) { p('ht_front_wheel', new THREE.CylinderGeometry(.48, .48, .3, 22), TYRE, 1.7, .48, s * .95, { rx: Math.PI / 2 }); p('ht_track', new THREE.BoxGeometry(2.6, .8, .4), TYRE, -1.0, .45, s * .9); for (let i = 0; i < 4; i++) p('ht_bogie', new THREE.CylinderGeometry(.28, .28, .1, 16), DARK, -2.0 + i * .66, .42, s * 1.12, { rx: Math.PI / 2 }); }
    // the giant speaker: a horn on a frame over the bed + the disc turntable and cables
    const prof = []; for (let i = 0; i <= 24; i++) { const y = i / 24 * 1.7; prof.push(new THREE.Vector2(.2 + .82 * Math.pow(y / 1.7, 2.6), y - .85)); }
    const HM = metal('steel', '#a3a99c', { rough: .42, finish: 'brushed' }); HM.side = THREE.DoubleSide;
    const horn = p('ht_speaker_horn', new THREE.LatheGeometry(prof, 48), HM, -1.15, 2.8, 0, { rz: -Math.PI / 2 });
    for (const [k, r] of [[.25, .27], [.5, .36], [.75, .56]]) p('ht_horn_rib', new THREE.TorusGeometry(r + .02, .025, 8, 40), OD, -1.15 - .85 + k * 1.7, 2.8, 0).rotation.y = Math.PI / 2;
    p('ht_horn_rim', new THREE.TorusGeometry(1.03, .05, 10, 48), OD, -1.15 + .85, 2.8, 0).rotation.y = Math.PI / 2;
    const throat = p('ht_horn_throat', new THREE.CircleGeometry(.95, 40), std('#121410', { rough: 1 }), -1.15 + .5, 2.8, 0); throat.rotation.y = Math.PI / 2;   // dark inside of the bell
    p('ht_speaker_driver', new THREE.CylinderGeometry(.3, .34, .55, 20), OD, -2.25, 2.8, 0, { rz: -Math.PI / 2 }); p('ht_driver_cap', new THREE.SphereGeometry(.3, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), OD, -2.52, 2.8, 0, { rz: Math.PI / 2 });
    for (const z of [-.45, .45]) p('ht_speaker_frame', new THREE.BoxGeometry(.1, 1.1, .1), OD, -1.7, 2.15, z); p('ht_speaker_cradle', new THREE.BoxGeometry(1.4, .1, 1.0), OD, -1.6, 2.4, 0);
    const cab = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(-2.5, 2.8, .2), new THREE.Vector3(-2.6, 2.0, .6), new THREE.Vector3(-1.4, 1.8, .7), new THREE.Vector3(-.4, 1.85, -.4)]), 24, .03, 6), DARK); add(cab, 'ht_speaker_cable', 'rubber', { parent: g });
    // armoured body detail: bed sides, fenders, headlights, winch roller, a "SONIC" crate
    for (const s of [-1, 1]) { p('ht_bed_side', new THREE.BoxGeometry(3.2, .5, .06), OD, -1.0, 2.0, s * 1.08); p('ht_fender', new THREE.BoxGeometry(1.1, .06, .5), OD, 1.7, 1.02, s * .95); p('ht_headlight', new THREE.CylinderGeometry(.11, .12, .16, 14), metal('steel', '#c8c8c0', { rough: .3 }), 2.25, 1.35, s * .6, { rz: Math.PI / 2 }); }
    p('ht_winch', new THREE.CylinderGeometry(.16, .16, 1.4, 16), DARK, 2.6, .95, 0, { rx: Math.PI / 2 });
    const sc = p('ht_sonic_crate', new THREE.BoxGeometry(.8, .5, .6), relief('wood', '#7a6444', { seed: 13 }), -2.0, 2.0, .55);
    const disc = p('ht_disc', new THREE.CylinderGeometry(.42, .42, .02, 32), std('#111111', { rough: .3 }), -.2, 1.78, -.6); p('ht_turntable', new THREE.BoxGeometry(1.0, .12, 1.0), std('#5a4636'), -.2, 1.7, -.6);
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
  function bulldozer(name, at, rot = 0) {
    const g = new THREE.Group(); g.name = name; g.position.copy(V(...at)); g.rotation.y = rot; scene.add(g);
    const Y = metal('iron', '#8a7a3a', { rough: .6 }), D = std('#2a2a26', { rough: .9 });
    const p = (nm, geo, mat, x, y, z) => { const m = add(new THREE.Mesh(geo, mat), nm, 'metal', { parent: g }); m.position.set(x, y, z); return m; };
    p('dozer_body', new THREE.BoxGeometry(2.4, 1.3, 1.8), Y, 0, 1.2, 0); p('dozer_cab', new THREE.BoxGeometry(1.0, 1.0, 1.4), Y, -.5, 2.3, 0); p('dozer_blade', new THREE.BoxGeometry(.15, 1.0, 2.6), D, 1.6, .6, 0);
    for (const s of [-1, 1]) p('dozer_track', new THREE.BoxGeometry(2.8, .7, .5), D, 0, .35, s * 1.0);
    // the toothed beam it drags: it draws two lines of track marks behind it
    p('dozer_beam', new THREE.BoxGeometry(.25, .2, 2.4), D, -1.8, .15, 0);
    for (let i = 0; i < 8; i++) p('dozer_beam_tooth', new THREE.BoxGeometry(.08, .22, .14), D, -1.8, .02, -1.05 + i * .3);   // the teeth that draw the tread marks
    p('dozer_exhaust', new THREE.CylinderGeometry(.07, .07, 1.0, 10), D, .7, 2.3, .5); p('dozer_grille', new THREE.BoxGeometry(.05, .9, 1.4), D, 1.22, 1.25, 0);
    for (let i = 0; i < 6; i++) p('dozer_grille_bar', new THREE.BoxGeometry(.06, .05, 1.3), Y, 1.25, .85 + i * .15, 0);
    for (const s of [-1, 1]) { p('dozer_arm', new THREE.BoxGeometry(1.4, .14, .14), D, 1.0, .7, s * 1.15); for (let i = 0; i < 5; i++) p('dozer_roller', new THREE.CylinderGeometry(.2, .2, .1, 12), Y, -1.0 + i * .5, .3, s * 1.27).rotation.x = Math.PI / 2;
      for (let i = 0; i < 14; i++) p('dozer_track_shoe', new THREE.BoxGeometry(.08, .06, .52), D, -1.3 + i * .2, .72, s * 1.0); }
    p('dozer_seat', new THREE.BoxGeometry(.4, .1, .45), std('#3a2a1e'), -.6, 1.9, 0); p('dozer_roof', new THREE.BoxGeometry(1.2, .06, 1.6), Y, -.5, 2.85, 0);
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

  // VFX audit: wind per place and light (dawn calm, open camp breezy, night road gusty in the poplars, river wind over the water)
  if (ctx.atmosphere && ctx.atmosphere.setWind) { const WN = { field: [.32, .12], camp: [.5, .2], road: [.62, .3], river: [.7, .3] }[Z]; if (WN) ctx.atmosphere.setWind({ direction: [1, .3], strength: WN[0], gust: WN[1], speed: 1 }); }
  let anchors = {};
  // ============================================================ ZONES ============================================================
  if (Z === 'field' || Z === 'camp') {
    // P1 Normandy bocage at dawn (hook) and P2 the same meadow as the ghost camp (overcast day)
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'clear-day', seed: Z === 'field' ? 11 : 12, coverage: Z === 'field' ? .7 : 1.4 });
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: Z === 'field' ? '#e8d2b0' : '#c9ccc8', near: 45, far: 260 });
    ground('#6f8a46'); const road = add(new THREE.Mesh(new THREE.PlaneGeometry(4.2, 200), relief('mud', '#8a7656', { seed: 61, size: 3 })), 'dirt_road', 'ground', { cast: false, mat: 'mud' }); road.rotation.x = -Math.PI / 2; road.position.copy(V(-7, 40, .01));
    hedge('hedge', [-60, 14], [-9.5, 14]); hedge('hedge', [-4.5, 14], [60, 14]); hedge('hedge', [-9.5, -30], [-9.5, 14]); hedge('hedge', [-4.5, 14], [-4.5, 90]); hedge('hedge', [14, 14], [14, 90]);
    for (const [x, y, h, s] of [[-14, 18, 9, 3], [8, 20, 11, 4], [22, 30, 10, 5], [-26, 34, 12, 6], [4, 46, 9, 7], [-40, 10, 10, 8], [30, 8, 9, 9]]) tree([x, y, 0], h, 'oak', s);
    for (const [x, y] of [[16, 10], [19, 6], [24, 11]]) tree([x, y, 0], 4.5, 'olive', Math.round(x));   // apple orchard stand-ins
    farmhouse([24, 34, 0], -.4); for (let i = 0; i < 6; i++) pole([-4.2, -10 + i * 22, 0]);
    const offRoad = (x, y) => Math.abs(x + 7) < 2.8 || Math.hypot(x - 5, y + 3.6) < 4.5 || Math.hypot(x + 3.4, y + 6.6) < 3;   // the dirt road and the lens of the low hook camera stay clear
    const clearBand = (im) => { if (!im || !im.isInstancedMesh) return; const M4 = new THREE.Matrix4(), Z0 = new THREE.Matrix4().makeScale(0, 0, 0), q = new THREE.Vector3();
      for (let i = 0; i < im.count; i++) { im.getMatrixAt(i, M4); q.setFromMatrixPosition(M4); const x = im.position.x + q.x, y = -(im.position.z + q.z); if (offRoad(x, y)) im.setMatrixAt(i, Z0); } im.instanceMatrix.needsUpdate = true; };
    if (ctx.detail) { clearBand(ctx.detail.grass({ at: [2, 4, 0], count: 1400, radius: 18, height: .34, seed: 71 })); clearBand(ctx.detail.grass({ at: [0, 30, 0], count: 1200, radius: 40, height: .5, seed: 73 })); clearBand(ctx.detail.rocks({ at: [-6, 8, 0], count: 40, radius: 18, size: .14, seed: 74 })); }
    { const fl = new THREE.InstancedMesh(new THREE.SphereGeometry(.035, 6, 4), new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: .8 }), 500), M4 = new THREE.Matrix4(), C = new THREE.Color();   // wild flowers: buttercups, daisies, clover
      for (let i = 0; i < 500; i++) { let a = rr(0, 6.3), r = rr(2, 30); while (offRoad(Math.cos(a) * r, 6 + Math.sin(a) * r)) { a = rr(0, 6.3); r = rr(2, 30); } M4.makeTranslation(...V(Math.cos(a) * r, 6 + Math.sin(a) * r, rr(.12, .3)).toArray()); fl.setMatrixAt(i, M4); fl.setColorAt(i, C.set(['#f2d23a', '#f4f1e6', '#d98ab0', '#f4f1e6'][i % 4])); }
      add(fl, 'wild_flowers', 'foliage', { cast: false }); }
    if (Z === 'field') {
      // the hook: the truck has brought the tank; four GIs lift it off and set it down in the field
      cargoTruck('cargo_truck', [-7, 6, 0], -Math.PI / 2);
      const tk = sherman('inflatable_sherman', { at: [0, 4, 0], rot: -.35 }); const lift = EV.lift || [0, 52], set = EV.set || 103, dent = EV.dent || 110;
      ups.push(f => { const a = sm((f - lift[0]) / (lift[1] - lift[0])), b = sm((f - lift[1]) / (set - lift[1])); tk.position.copy(V(0, 4, 1.55 * (1 - b) + .03 * Math.sin(f * .21) * (1 - b))); tk.rotation.y = -.35;   /* animation audit: the tank stays above its four lifters (it used to slide 3.6 m over static men) and comes down with them; a small bob while held */
        const d = Math.max(0, 1 - Math.abs(f - dent) / 10), dr = sm((f - (EV.deflate || 1e9)) / 18); tk.userData.set(.9 * dr, .12 * d + .25 * dr); });
      anchors = { tank: [0, 4, 1.2], truck: [-7, 6, 1.5] };
    } else {
      // the camp: rows of tanks in every state of inflation, compressors, paint pots, the bulldozer drawing track marks
      const rows = []; for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) { const t = sherman('camp_tank', { at: [-12 + c * 8, 12 + r * 9, 0], rot: rr(-.2, .2) + Math.PI * .02 }); t.userData.set(0, [0, .35, .7, 0][(r * 4 + c) % 4]); rows.push(t); }
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
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'night-storm', seed: 31, coverage: .6 });
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: '#1e2a48', near: 30, far: 200 });
    ground('#3e5236'); scene.add(new THREE.HemisphereLight('#7a92cc', '#2c3626', 2.4)); { const mk = new THREE.DirectionalLight('#b0c4ff', 2.2); mk.position.copy(V(-30, 60, 40)); mk.target.position.copy(V(0, 10, 0)); mk.castShadow = true; scene.add(mk, mk.target); }
    const road = add(new THREE.Mesh(new THREE.PlaneGeometry(5, 300), relief('cobble', '#7a7466', { seed: 81, size: 2 })), 'road', 'ground', { cast: false, mat: 'cobble' }); road.rotation.x = -Math.PI / 2; road.position.copy(V(0, 60, .01));
    for (let i = 0; i < 18; i++) for (const s of [-1, 1]) tree([s * 4.2, -10 + i * 9, 0], 14, 'cypress', i * 2 + (s > 0 ? 1 : 0));   // poplars
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
    box('field_radio', 'metal', .9, .5, .6, [.3, 1.7, .8], metal('iron', '#4d5634', { rough: .6 })); for (let i = 0; i < 4; i++) cyl('radio_dial', 'metal', .06, .04, [.0 + i * .2, 1.44, 1.2], metal('steel', '#c8c8c0'));
    const key = box('morse_key', 'metal', .26, .12, .05, [-.5, 1.4, .8], metal('brass', '#c8a24a')); box('morse_base', 'wood', .3, .16, .03, [-.5, 1.4, .79], relief('wood', '#3a2a1e', { seed: 102 }));
    const card = add(new THREE.Mesh(new THREE.PlaneGeometry(.8, .5), basic('#ffffff', { map: canvasTex(320, 200, (g, w, h) => { g.fillStyle = '#efe6d0'; g.fillRect(0, 0, w, h); g.fillStyle = '#2a2420'; g.font = 'bold 20px serif'; g.fillText('FIST: OP. 4th ARMD', 14, 30); for (let r = 0; r < 4; r++) { let x = 14; for (let i = 0; i < 14; i++) { const dash = rnd() < .45; g.fillRect(x, 60 + r * 34, dash ? 22 : 8, 8); x += dash ? 30 : 16; } } }) })), 'fist_card', 'cloth', { cast: false }); card.position.copy(V(-.2, 3.85, 1.6));
    lamp([.8, 1.4, 2.4], '#ffd08a', 16, 8);
    box('map_board', 'wood', 1.6, .05, 1.0, [1.4, 3.86, 1.2], std('#ffffff', { extra: { map: canvasTex(320, 200, (g, w, h) => { g.fillStyle = '#d8ccA0'; g.fillRect(0, 0, w, h); g.strokeStyle = 'rgba(90,120,80,.6)'; for (let i = 0; i < 14; i++) { g.beginPath(); g.moveTo(0, rr(0, h)); g.bezierCurveTo(w * .3, rr(0, h), w * .6, rr(0, h), w, rr(0, h)); g.stroke(); }
      g.strokeStyle = '#4a6ab0'; g.lineWidth = 6; g.beginPath(); g.moveTo(w * .7, 0); g.bezierCurveTo(w * .55, h * .4, w * .8, h * .7, w * .6, h); g.stroke(); g.fillStyle = '#2a2a24'; g.font = 'bold 14px serif'; g.fillText('SECTOR 7 - GRID 41', 10, 18); for (let i = 0; i < 7; i++) { g.fillStyle = ['#c8322c', '#2a5ab0', '#2a2a24'][i % 3]; g.beginPath(); g.arc(rr(30, w - 30), rr(30, h - 30), 4, 0, 6.3); g.fill(); } }) } }));
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
  if (Z === 'photo') {
    room(7, 6, 3.0, '#5a5e60', 'stone', '#4a4c4e', { wallMat: blockPaint, ceilMat: std('#4e5254', { rough: .95 }) });
    { const GM = metal('iron', '#5a6058', { rough: .55 });   // filing cabinet, a pinboard of photos, a desk lamp, stacked prints, a hanging shade
      box('filing_cabinet', 'metal', .5, .6, 1.3, [-3.0, 3.4, 0], GM); for (let i = 0; i < 4; i++) box('drawer_front', 'metal', .44, .02, .26, [-3.0, 3.09, .12 + i * .31], GM);
      box('pinboard', 'wood', 1.4, .04, .9, [-1.8, 3.97, 1.5], relief('wood', '#a88a5a', { seed: 121 })); for (let i = 0; i < 8; i++) box('pinned_photo', 'cloth', .22, .01, .17, [-2.35 + (i % 4) * .36, 3.94, 1.25 + (i >> 2) * .4], std(i % 3 ? '#9a9a90' : '#7a7a72'));
      for (let i = 0; i < 5; i++) box('print_stack', 'cloth', .3, .24, .015, [.85 + i * .01, 1.25, .93 + i * .016], std('#c8c8c0'), { rot: rr(-.2, .2) });
      cyl('lamp_shade', 'metal', .3, .25, [0, 1.6, 2.4], GM, { r2: .08 }); cyl('lamp_cord', 'metal', .01, .4, [0, 1.6, 2.65], std('#1a1a1a')); }
    const lt = box('light_table', 'lamp', 2.2, 1.3, .9, [0, 1.6, 0], std('#2a2c2e')); const top = box('light_table_glass', 'lamp', 2.0, 1.1, .03, [0, 1.6, .9], basic('#9fb2c8'));
    const photoTex = canvasTex(512, 384, (g, w, h) => { g.fillStyle = '#8a8a80'; g.fillRect(0, 0, w, h); for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(${rnd() * 60 | 0},${rnd() * 60 | 0},${rnd() * 50 | 0},.08)`; g.fillRect(rnd() * w, rnd() * h, 3, 3); } g.fillStyle = '#3a3a34'; for (let r = 0; r < 4; r++) for (let c = 0; c < 6; c++) { const x = 40 + c * 75, y = 60 + r * 80; g.fillRect(x, y, 36, 22); g.fillRect(x + 30, y + 9, 20, 4); g.fillStyle = 'rgba(30,25,20,.5)'; g.fillRect(x + 4, y + 24, 4, 50); g.fillRect(x + 26, y + 24, 4, 50); g.fillStyle = '#3a3a34'; } });
    const ph = add(new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.0), basic('#d8d8d0', { map: photoTex })), 'aerial_photo', 'cloth', { cast: false }); ph.rotation.x = -Math.PI / 2; ph.position.copy(V(0, 1.6, .925));
    const loupe = cyl('loupe', 'glass', .09, .08, [.25, 1.5, .93], std('#cfe6ff', { rough: .05, extra: { transparent: true, opacity: .5 } }));
    const tl = new THREE.PointLight('#dfeaff', 5, 6, 1.4); tl.position.copy(V(0, 1.6, 1.3)); scene.add(tl); lamp([2.6, 3.4, 2.8], '#9fb0c8', 6, 8);
    box('river_map', 'cloth', 2.4, .04, 1.4, [0, 3.95, 1.4], basic('#ffffff', { map: canvasTex(480, 280, (g, w, h) => { g.fillStyle = '#d8d0b4'; g.fillRect(0, 0, w, h); g.strokeStyle = '#4a6ab0'; g.lineWidth = 16; g.beginPath(); g.moveTo(w * .55, 0); g.bezierCurveTo(w * .4, h * .3, w * .7, h * .6, w * .5, h); g.stroke(); g.fillStyle = '#b02a2a'; for (let i = 0; i < 12; i++) g.fillRect(w * .62 + (i % 4) * 14, h * .72 + Math.floor(i / 4) * 14, 9, 9); }) }));
    anchors = { photo: [0, 1.6, .93], loupe: [.25, 1.5, .95] };
  }
  if (Z === 'river') {
    // P7: the great river at night. SOUTH (x < 0): the decoy field under shell bursts. NORTH (x > 40): the real army crossing on pontoons in silence.
    if (ctx.sky && ctx.sky.on) ctx.sky.clouds({ kind: 'night-storm', seed: 71, coverage: .8 });
    if (ctx.atmosphere) ctx.atmosphere.setFog({ color: '#1a2440', near: 40, far: 320 });
    ground('#4a5c3a');
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
    const decoys = []; for (let r = 0; r < 4; r++) for (let c = 0; c < 7; c++) { const t = sherman('decoy_tank', { at: [-46 + c * 7 + rr(-1, 1), 18 + r * 8 + rr(-1, 1), 0], rot: rr(-.3, .3) }); decoys.push(t); }
    // shell bursts on the decoys from EV.shell on: flashes + tanks thrown and deflating
    const bursts = []; for (let i = 0; i < 10; i++) { const b = glow('#ffb060', 6, 0, V(-42 + (i * 23) % 40, 20 + (i * 7) % 22, 1)); const l = new THREE.PointLight('#ffa040', 0, 40, 1.6); l.position.copy(b.position); scene.add(l); const fb = add(new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), basic('#fff2c0', { transparent: true, depthWrite: false })), 'shell_fireball', 'fx', { cast: false }); fb.position.copy(b.position); fb.userData.noExport = true; const ob = add(new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), basic('#ff7a2a', { transparent: true, depthWrite: false })), 'shell_fire_outer', 'fx', { cast: false }); ob.position.copy(b.position); const sk = []; for (let j = 0; j < 5; j++) { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: '#6a6660', transparent: true, opacity: .75, depthWrite: false })); sp.userData.noExport = true; sp.userData.off = [rr(-1.5, 1.5), rr(0, 2), rr(-1.5, 1.5)]; scene.add(sp); sk.push(sp); }   /* soft smoke puffs */ const clods = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.32, 0), std('#3a2e22', { rough: 1 }), 14); clods.userData.noExport = true; add(clods, 'shell_debris', 'fx', { cast: false }); const cv = Array.from({ length: 14 }, () => [rr(-5, 5), rr(7, 13), rr(-5, 5)]); bursts.push({ clods, cv, b, l, fb, ob, sk, f0: (EV.shell || 0) + i * 8, d: decoys[(i * 5) % decoys.length] }); }   // the barrage keeps falling while the crane rises
    // the real crossing (north): pontoon bridge and real (metal) tanks rolling across
    box('assault_boat', 'wood', 1.6, 3.2, .45, [57.0, 44.0, .15], relief('wood', '#4a4a36', { seed: 160 }));
    { const rip = []; for (let i = 0; i < 10; i++) { const r_ = add(new THREE.Mesh(new THREE.RingGeometry(.92, 1.0, 48), new THREE.MeshBasicMaterial({ color: '#dfe8f4', transparent: true, opacity: 0, depthWrite: false })), 'water_ripple', 'water', { cast: false }); r_.rotation.x = -Math.PI / 2; r_.userData.c = i < 4 ? [57.0, 44.0] : [60 + (i % 2 ? 1.5 : -1.5), 37 + (i - 4) * 6]; r_.userData.ph = i * .37; rip.push(r_); }
      ups.push((f, t) => { rip.forEach(r_ => { const q = (t * .35 + r_.userData.ph) % 1; r_.position.copy(V(r_.userData.c[0], r_.userData.c[1], .33)); r_.scale.setScalar(1.6 + q * 3.5); r_.material.opacity = .1 * (1 - q) * Math.min(1, q * 5); }); }); }   /* ripples round the boat and pontoons */   // the sergeant's boat beside the bridge
    for (let i = 0; i < 14; i++) { const fr_ = add(new THREE.Mesh(new THREE.RingGeometry(1.5, 1.9, 4, 1), new THREE.MeshBasicMaterial({ color: '#dfe8f4', transparent: true, opacity: .28, depthWrite: false })), 'pontoon_foam', 'water', { cast: false }); fr_.rotation.x = -Math.PI / 2; fr_.rotation.z = Math.PI / 4; fr_.scale.set(1, 1.15, 1); fr_.position.copy(V(60, 37 + i * 3.1, .32)); }
    for (let i = 0; i < 14; i++) box('pontoon', 'metal', 2.6, 3.0, .5, [60, 37 + i * 3.1, .05], metal('iron', '#3a4030', { rough: .7 }));
    box('bridge_deck', 'wood', 3.2, 44, .12, [60, 58, .55], relief('wood', '#5a4a36', { seed: 121 }));
    const real = []; for (let i = 0; i < 3; i++) { const t = sherman('real_tank', { at: [60, 30 - i * 9, 0], rot: -Math.PI / 2, col: '#4a5030' }); t.traverse(o => { if (o.isMesh && o.material.name === 'rubber_canvas') { o.material = metal('iron', '#4a5030', { rough: .65, rust: .2 }); } }); real.push(t); }
    const moon = glow('#e6eeff', 24, .9, V(120, 200, 80)); const path = add(new THREE.Mesh(new THREE.PlaneGeometry(6, 60), basic('#c8d8ff', { transparent: true, opacity: .1, depthWrite: false })), 'moon_path', 'water', { cast: false }); path.rotation.x = -Math.PI / 2; path.position.copy(V(70, 70, .38)); path.visible = false;   /* the moon's real reflection (env map) replaces the painted strip */ const ml = new THREE.DirectionalLight('#b4c6ff', 3.2); scene.add(new THREE.HemisphereLight('#7c90c8', '#33402c', 3.2));   /* night never under mean 0.31 (11c) */    // moonlight pools on the silent crossing (north)
    for (const [x, y] of [[-40, 14], [-26, 16], [-12, 14], [-33, 36], [-19, 38]]) { const wl = new THREE.PointLight('#ffcf8a', 30, 26, 1.6); wl.position.copy(V(x, y, 4)); scene.add(wl); glow('#ffcf8a', 1.4, .9, V(x, y, 4)); cyl('work_lamp_pole', 'metal', .06, 4, [x, y, 0], metal('iron', '#3a3a34')); } ml.position.copy(V(-40, -60, 70));   /* key from the camera side: the moon glint off the water bloomed into a haze */ scene.add(ml);
    decoys.forEach((t, i) => { t.userData.i0 = (EV.inflate || 0) + i * 2; });
    ups.push((f, t) => {
      decoys.forEach(t => { if (t.position.y > .01) return; const u = sm((f - t.userData.i0) / 12); t.visible = u > .02; t.scale.set(1, Math.max(.05, u), 1); });
      const p = riv.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const x = rb[i * 3], y = rb[i * 3 + 1]; p.setZ(i, .05 * Math.sin(.2 * x + 1.4 * t) + .03 * Math.sin(.31 * y - 1.1 * t)); } p.needsUpdate = true; riv.geometry.computeVertexNormals();
      for (const B of bursts) { const k = (f - B.f0) / 22, on = k > 0 && k < 1 ? (k < .15 ? .85 * k / .15 : .85 * Math.pow((1 - k) / .85, 1.5)) : 0;   // 3-frame build, then a slow fall; softer peak (no white-out)
        B.b.material.opacity = .4 * on; B.b.scale.setScalar(5 + 6 * Math.max(0, Math.min(1, k))); B.l.intensity = 60 * on; const kk = Math.max(0, Math.min(1, k)); B.fb.scale.setScalar(on > .02 ? (1.2 + 2.2 * kk) * Math.sqrt(on) : 1e-4); B.ob.scale.setScalar(on > .02 ? (2.4 + 4.6 * kk) : 1e-4); B.fb.material.opacity = Math.min(1, on * 1.3); B.ob.material.opacity = .8 * on;   /* a hot core inside a fading orange shell, not a solid ball */ B.ob.position.y = B.b.position.y + 1.2 * kk;
        const sm_ = (f - B.f0) / 60; B.sk.forEach(sp => { const o = sp.userData.off; sp.position.set(B.b.position.x + o[0] * (1 + sm_), B.b.position.y + 1.5 + o[1] + 5 * Math.max(0, sm_), B.b.position.z + o[2] * (1 + sm_)); sp.scale.setScalar(sm_ > .1 && sm_ < 1.8 ? 4 + 6 * Math.min(1, sm_) : 1e-4); sp.material.opacity = .7 * Math.max(0, 1 - sm_ / 1.8); });   // smoke rises after the flash
        B.fb.material.color.set(on > .5 ? '#fff0b0' : '#ff9a40');
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
    const lump = add(new THREE.Mesh(new THREE.SphereGeometry(.5, 20, 12), new THREE.MeshStandardMaterial({ map: quiltTex, roughness: .95 })), 'pillow_lump', 'cloth'); lump.scale.set(.62, .34, 1.15); lump.position.copy(V(-.8, 2.0, .66));
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
    ups.push((f, t) => { lump.scale.y = .34 + .025 * Math.sin(t * 1.5); });
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
    { const shaft = add(new THREE.Mesh(new THREE.CylinderGeometry(.35, 1.3, 4.6, 24, 1, true), new THREE.MeshBasicMaterial({ color: '#ffd9a0', transparent: true, opacity: .07, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending })), 'light_shaft', 'fx', { cast: false });
      shaft.position.copy(V(-1.6, .6, 2.0)); shaft.rotation.z = .55; shaft.rotation.x = -.25; shaft.userData.noExport = true; ups.push((f, t) => { shaft.material.opacity = .065 + .01 * Math.sin(t * .7); }); }   /* the window light the dust motes float in (story bible P9) */
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
