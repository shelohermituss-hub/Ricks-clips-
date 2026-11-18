// LIFT (Ghost Army, 2026-11-17): holding a big light thing overhead, setting it down, patting it like luggage.
// Built on the cheer "stadium" arm rig (the only arm set that clears the head on this cast) with weight added:
// knees give under the load, a slow breath sway, a foot shuffle to rebalance; then a two-beat set-down (dip, push, straighten).
import { track, reachDrop } from '../rig.mjs';
const sin = Math.sin, pos = v => Math.max(0, v), F = v => v === 'front';
const feet = (f, l0 = 0, l1 = 0, k = .4) => f ? [{ x: -42, lift: l0, kneeK: k }, { x: 40, lift: l1, kneeK: k }] : [{ x: -24, lift: l0 }, { x: 24, lift: l1 }];
// A BORED HOLD: arms up in a V under the load, knees soft and giving, a slow sway, one foot shuffles to rebalance (~every 2.2 s)
const hold = v => (t, ch) => { const f = F(v), give = .5 + .5 * sin(t * 1.7), sh = pos(sin(t * 2.85 - 1.2)) ** 6;
  const P = { view: v, dir: 1, x: 3 * sin(t * .9), rot: f ? 2.5 * sin(t * .9) : -4 + 1.5 * sin(t * .9), feet: feet(f, 22 * sh, 0, .55),
    hands: f ? [{ f: .8, d: -.6 + .02 * give, bow: .25 }, { f: .8, d: -.6 - .02 * give, bow: .25 }] : [{ f: -.78, d: -.52 + .02 * give, bow: .25 }, { f: .86, d: -.46 - .02 * give, bow: .25 }],
    head: f ? 2 * sin(t * .9) : -5 };
  P.y = reachDrop(ch, P) + 14 + 10 * give; return { ...P, cam: 0 }; };
// B SET DOWN: from the hold, a dip (anticipation), arms come down and forward as the load lowers, straighten, hands drop, a small shake-out
const setDown = v => (t, ch) => { const f = F(v), a = track([[0, 0], [.35, 1, 'io'], [1.3, 2, 'io'], [1.7, 3, 'out'], [2.3, 4, 'io']], t);
  const up = Math.max(0, Math.min(1, 2 - a)), dip = pos(1 - Math.abs(a - 1)) + .6 * pos(1 - Math.abs(a - 2)), shake = a > 3 ? .04 * sin(t * 26) * (4 - Math.min(4, a)) : 0;
  const dU = -.56, dD = f ? .55 : .5, d = dU + (dD - dU) * (1 - up);
  const P = { view: v, dir: 1, x: 0, rot: f ? 0 : -4 + 8 * dip, feet: feet(f, 0, 0, .4 + .3 * dip),
    hands: f ? [{ f: .8 - .3 * (1 - up), d: d + shake, bow: .3 }, { f: .8 - .3 * (1 - up), d: d - shake, bow: .3 }] : [{ f: -.78 + .9 * (1 - up), d: d + shake, bow: .3 }, { f: .86 - .2 * (1 - up), d: d - shake, bow: .3 }],
    head: f ? 0 : -5 + 6 * dip };
  P.y = reachDrop(ch, P) + 40 * dip; return { ...P, cam: 0 }; };
// C PAT LIKE LUGGAGE: one hand on the hip, the other gives the thing two light pats at chest height, then rests on it; weight on the back foot
const pat = v => (t, ch) => { const f = F(v), p = t < 1.6 ? pos(sin(t * 7.5)) * (t < .9 ? 1 : .5) : 0, lean = .5 + .5 * sin(t * 1.3);
  const P = { view: v, dir: 1, x: 0, rot: f ? 1.5 * lean : 3 + 2 * lean, feet: feet(f, 0, 0, .35),
    hands: f ? [{ f: .25, d: .45, bow: .9 }, { f: .62, d: .12 - .14 * p, bow: .5 }] : [{ f: -.3, d: .5, bow: .9 }, { f: .7, d: .08 - .14 * p, bow: .5 }],
    head: f ? 2 * lean : -3 - 3 * p };
  P.y = reachDrop(ch, P); return { ...P, cam: 0 }; };
const mk = (v, label) => ({ title: `LIFT  ·  ${label}`, dur: 4, styles: [
  { key: 'A', name: 'Bored hold', blurb: 'arms up under the load, knees give, slow sway, foot shuffle', pose: hold(v) },
  { key: 'B', name: 'Set down', blurb: 'dip, lower the load, straighten, shake out', pose: setDown(v) },
  { key: 'C', name: 'Pat like luggage', blurb: 'hand on hip, two pats, rests a hand on it', pose: pat(v) },
] });
export default mk('side', 'side view');
export const front = mk('front', 'front view');
