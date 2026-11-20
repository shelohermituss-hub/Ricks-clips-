// SHEET 18 — exploding-whale production (2026-11-20, "The Exploding Whale", Oregon 1970). Original characters, no real person's likeness.
//   engineer : the highway engineer who runs the blast: WHITE hard hat, site-engineer shirt and tie, proud face (plan: cast:engineer)
//   veteran  : the quiet man in the crowd who knows explosives: olive army cap, khaki WW2 jacket (plan: cast:veteran)
//   worker   : highway crew: yellow hard hat, hi-vis road-worker vest (plan: cast:worker)
//   reporter : TV reporter: brown 1970 suit, side part (plan: cast:reporter)   cameraman: denim shirt, cap worn backwards
//   clerk    : office clerk of the highway division: office shirt, slick hair, glasses come from the face set
import { INK, P, fillPts, hl } from '../castkit.mjs';
import { wear } from '../head_wear.mjs';
export const TITLE = 'Cast sheet 18: exploding whale';
// hard hat (same construction as sheet06 "construction", any colour): brim + dome + centre ridge + highlight
const hardHat = (Y, R) => ({ cx, hy }) => [P(`M${cx - 128},${hy - 46} Q${cx},${hy - 76} ${cx + 128},${hy - 46} Q${cx + 132},${hy - 26} ${cx + 110},${hy - 28} Q${cx},${hy - 48} ${cx - 110},${hy - 28} Q${cx - 132},${hy - 26} ${cx - 128},${hy - 46} Z`, Y, INK, 6),
  fillPts([[cx - 104, hy - 50], [cx - 98, hy - 104], [cx - 50, hy - 140], [cx, hy - 148], [cx + 50, hy - 140], [cx + 98, hy - 104], [cx + 104, hy - 50], [cx, hy - 64]], Y, 7),
  P(`M${cx - 20},${hy - 146} Q${cx},${hy - 154} ${cx + 20},${hy - 146} L${cx + 16},${hy - 62} L${cx - 16},${hy - 62} Z`, R, INK, 4.5), hl(`M${cx - 80},${hy - 100} Q${cx - 60},${hy - 130} ${cx - 34},${hy - 136}`, 9, .6)];
const engineer = { name: 'engineer', label: 'Highway engineer', form: 'standard', size: 'thin', coat: '#e9e4d6', face: 'proud', hairCol: '#4a3526',
                   outfit: ['engineer', { a: '#e9e4d6', b: '#b23a2e', c: '#3a4a66' }], hat: hardHat('#f4f4ef', '#ffffff') };
const worker = { name: 'worker', label: 'Highway crew', form: 'standard', size: 'thin', coat: '#f3812a', face: 'strain', hairCol: '#2e2a26',
                 outfit: ['roadWorker', { a: '#f3812a', b: '#f5c518', c: '#c9ccd0' }], hat: hardHat('#f5c518', '#f8d84a') };
const veteran = wear({ name: 'veteran', label: 'Veteran in the crowd', form: 'standard', size: 'thin', coat: '#7a7446', face: 'standard', hairCol: '#8a8a86',
                       outfit: ['ww2Soldier', { a: '#6f6a3e', b: '#8a8456', c: '#5a4630' }] }, 'buzz', { hat: 'kepi', hatCol: '#5f6a38' });
const reporter = wear({ name: 'reporter', label: 'TV reporter', form: 'standard', size: 'thin', coat: '#8a6a44', face: 'standard', hairCol: '#3a2a20',
                        outfit: ['suit', { a: '#8a6a44', b: '#f1ead8', c: '#b8432e' }] }, 'sidePart', {});
const cameraman = wear({ name: 'cameraman', label: 'TV cameraman', form: 'standard', size: 'thin', coat: '#4f6f9a', face: 'standard', hairCol: '#6b4423',
                         outfit: ['denimShirt', { a: '#4f6f9a', b: '#3a5376', c: '#f1ead8' }] }, 'mullet', { hat: 'capBack', hatCol: '#b8432e' });
const clerk = wear({ name: 'clerk', label: 'Office clerk', form: 'standard', size: 'thin', coat: '#cfd9e6', face: 'standard', hairCol: '#2e2a26',
                     outfit: ['officeShirt', { a: '#cfd9e6', b: '#3a4a66', c: '#f4f4f2' }] }, 'slickBack', {});
export const CAST = [engineer, worker, veteran, reporter, cameraman, clerk];
