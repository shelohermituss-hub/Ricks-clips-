// SHEET 19 — cart_army reproduction (2026-11-20, "How One Cart Stopped an Entire Army"). Original characters built to match the reference's roles.
//   fort_engineer : the man who drills the 82 holes: red quilted tunic, brown belt, white headband in spiky brown hair, half-lidded smug face
import { wear } from '../head_wear.mjs';
import { PIECES } from '../hair_lib.mjs';
const whiteBand = Pp => PIECES.headband(Pp).map(s => typeof s === 'string' ? s.replaceAll('#3a8fc4', '#f1ece0') : s);   // the reference's white cloth headband
export const TITLE = 'Cast sheet 19: cart army';
const fort_engineer = wear({ name: 'fort_engineer', label: 'Fort engineer', form: 'standard', size: 'thin', coat: '#b3243d', face: 'smug', hairCol: '#5a3a24',
                             outfit: ['judoka', { a: '#b3243d', b: '#7a4a2a', c: '#5a3a22' }] }, 'spiky', { col: '#5a3a24', pieces: [whiteBand] });
//   enemy_general : the general carried on a palanquin under a parasol: the sheet-02 samurai (horned helmet, armour) in black lacquer
//   enemy_soldier : the marching army: yellow tunic, grey kettle helmet (the helmet piece was drawn for this very film)
import { CAST as ASIA } from './sheet02.mjs';
const enemy_general = { ...ASIA.find(c => c.name === 'samurai'), name: 'enemy_general', label: 'Enemy general', coat: '#2b2733' };
const enemy_soldier = wear({ name: 'enemy_soldier', label: 'Enemy soldier', form: 'standard', size: 'thin', coat: '#e0aa1c', face: 'annoyed', hairCol: '#2e2a26',
                             outfit: ['mongol', { a: '#e0aa1c', b: '#3a3a40', c: '#7a5a20' }] }, 'buzz', { col: '#2e2a26', hat: 'dome', hatCol: '#aeb4c2' });
export const CAST = [fort_engineer, enemy_general, enemy_soldier];
