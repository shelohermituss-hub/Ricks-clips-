// SHEET 16 — crashed_car production (2026-11-19): the barrel inventor (aviator cap + goggles from sheet 08, moustache, blue work overalls)
import { CAST as C8 } from './sheet08.mjs';
import { withFace } from '../face_gear.mjs';
export const TITLE = 'Cast sheet 16: crashed car';
const av = C8.find(c => c.name === 'aviator');
export const CAST = [
  withFace({ ...av, name: 'barrel_inventor', label: 'Barrel inventor', form: 'standard', size: 'thin', coat: '#2f5fbf', props: undefined, details: undefined,
             outfit: ['mechanic', { a: '#2f5fbf', b: '#b8262e', c: '#c9ccd2' }] }, { stache: 'chevron', col: '#4a3a30' }),
];
