// SHEET 17 — crash_instinct production (2026-11-19, CB's own video "The Instinct That Makes You Crash")
//   planter : the man who plants the tree (shot 1) = the tow truck guy (shots 9-10, 15) = the mechanic (shot 16): ONE character,
//             teal short-sleeve work shirt, red trucker cap, brown hair under it (references/crash_instinct/ANALYSE_FR.md §4)
import { wear } from '../head_wear.mjs';
const TEAL_SHIRT = ['workShirt', { a: '#27a596', b: '#1b6e66', c: '#f4f4f2' }];
const planter = wear({ name: 'planter', label: 'Tree planter / tow truck guy', form: 'standard', size: 'thin', coat: '#27a596', face: 'standard',
                       hairCol: '#6b4423', outfit: TEAL_SHIRT }, 'sidePart', { hat: 'baseball', hatCol: '#d8262f' });
export const TITLE = 'Cast sheet 17: crash instinct';
export const CAST = [planter];
