// SHEET 16 — crashed_car production (2026-11-19)
//   barrel_inventor : the hero (aviator cap + goggles from sheet 08, moustache, blue work overalls)
//   hero_racer      : the same hero in his old blue race suit (shot 2B/2C)
//   young_driver    : the hero young, in the race suit with the white racing helmet on (shot 2A)
import { CAST as C8 } from './sheet08.mjs';
import { withFace } from '../face_gear.mjs';
import { withGear } from '../head_gear.mjs';
export const TITLE = 'Cast sheet 16: crashed car';
const av = C8.find(c => c.name === 'aviator');
const RACE_SUIT = ['mechanic', { a: '#2f5fbf', b: '#d8262f', c: '#f4f4f2' }];
const hero = withFace({ ...av, name: 'barrel_inventor', label: 'Barrel inventor', form: 'standard', size: 'thin', coat: '#2f5fbf', props: undefined, details: undefined,
                        outfit: ['mechanic', { a: '#2f5fbf', b: '#b8262e', c: '#c9ccd2' }] }, { stache: 'chevron', col: '#4a3a30' });
export const CAST = [
  hero,
  { ...hero, name: 'hero_racer', label: 'Hero in his race suit', outfit: RACE_SUIT },
  withGear({ name: 'young_driver', label: 'Young race driver', form: 'standard', size: 'thin', coat: '#2f5fbf', face: 'proud', outfit: RACE_SUIT }, 'buzz', { helmet: 'racing' }),
];
