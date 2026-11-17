#!/usr/bin/env node
// Render-level regression test for the optional secondary-motion layer.
// It compares the actual SVG output from the character renderer, not just config parsing.
import * as char2d from '../templates/vector2d_characters/code/char2d.mjs';
import * as memes from '../templates/vector2d_characters/code/memes.mjs';
import * as memes2 from '../templates/vector2d_characters/code/memes2.mjs';
import * as memes3 from '../templates/vector2d_characters/code/memes3.mjs';
import * as bodies from '../templates/vector2d_characters/code/bodies.mjs';
import * as cast from '../templates/vector2d_characters/code/cast.mjs';
import * as walk from '../templates/motion_styles/moves/walk.mjs';
import { LIB } from '../templates/motion_styles/library.mjs';
import { initPuppets, svgFor } from '../templates/threejs_film/puppets.mjs';

const who = 'qa-walker';
const polishOn = { enabled: true, head_follow: .14, hand_follow: .08, breath: .55, breath_rate: 2.15, auto_blink: true };
function render(polish, t) {
  initPuppets({ char2d, memes, memes2, memes3, bodies, cast, motion: { LIB, mods: { walk }, polish, cloth: null } });
  return svgFor({ puppet: 'form:standard', id: who }, { pose: 'm:walk/A', mt: t, view: 'side', dir: 1 });
}

const untreated = render({ enabled: false }, .23);
const polished = render(polishOn, .23);
if (!untreated || !polished || untreated === polished) {
  throw new Error('Secondary motion did not change the rendered SVG.');
}

// Select a deterministic moment inside the blink window for this character identity.
const seed = [...who].reduce((sum, c) => sum + c.charCodeAt(0), 0);
const period = 2.9 + (seed % 5) * .31;
const offset = seed * .017;
const blinkTime = (period - (offset % period) + .02) % period;
const withBlink = render(polishOn, blinkTime);
const withoutBlink = render({ ...polishOn, auto_blink: false }, blinkTime);
if (!withBlink || !withoutBlink || withBlink === withoutBlink) {
  throw new Error(`Automatic blink did not change the SVG at t=${blinkTime.toFixed(3)}.`);
}

console.log('MOTION POLISH PASS: secondary motion and deterministic auto-blink both alter rendered SVG output.');
