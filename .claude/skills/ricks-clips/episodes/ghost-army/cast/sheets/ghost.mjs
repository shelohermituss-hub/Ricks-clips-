// CAST of "The Ghost Army" (Normandy 1944, the Rhine 1945, an attic today). character-artist, 2026-11-17.
// Puppets: "cast:lou" "cast:carrier_tall" "cast:carrier_stocky" "cast:carrier_short" "cast:farmer" "cast:boy" "cast:sergeant" "cast:sound_op"
//          "cast:radio_op" "cast:spy" "cast:waitress" "cast:interpreter" "cast:grandchild" "cast:old_lou".
// film.json: "puppet_pkg": ["cast", "<skill>/templates/vector2d_characters/code"]. Built ONLY from the locked kit (outfit_lib, head_wear, head_gear, hair_lib).
// PERIOD CHECK 1944 (head / neck / face hair):
//  GIs           M1 steel helmet (head_gear 'soldier', olive) / open olive shirt collar / clean-shaven (US Army regulation)
//  sergeant      leather tanker cap with goggles pushed up (head_gear 'pilot' = closest kit shape to the M1938 tanker helmet) / clean-shaven
//  farmer        felt hat (Normandy farmers wore berets or felt hats; the kit has no beret: slouch felt) / blue work jacket / grey moustache-free
//  boy           bare head, 1940s school shorts look (newsboy) / -
//  spy           fedora + trench coat (1940s civilian) / -
//  waitress      no hat, hair up (1940s) / white collar, apron / -
//  interpreter   grey peaked cap (police shape, grey) / grey tunic (ww1 shape recoloured field grey) / -
//  grandchild    today: hoodie        old Lou   today: cardigan, grey hair
// COLOUR (STORY_BIBLE look): olive and khaki for the unit; the ONE red of the film is the café awning (set), never a costume.
import { wear } from '../head_wear.mjs';
import { withGear } from '../head_gear.mjs';

const OLIVE = '#5f6a3c', OLIVED = '#4a5230', KHAKI = '#b9a77a', BROWN = '#6b4a2e', FIELDGREY = '#6f7470', NAVY = '#2c3a5a', WORKBLUE = '#3f5f8f';
const base = spec => ({ form: 'standard', face: 'standard', views: true, sideFarArm: true, ...spec });
const gi = (name, label, size, hair, hairCol, pal) => withGear(base({ name, label, size, outfit: 'ww2Soldier', outfitPal: pal || { a: OLIVE, b: KHAKI, c: BROWN } }), hair, { col: hairCol, helmet: 'soldier' });

export const TITLE = 'The Ghost Army: the cast (Normandy 1944, the Rhine 1945, today)';
export const CAST = [
  // CHAR_GA_001 LOU, the hero: young artist-soldier, thin, curly brown hair under the steel helmet. Signature (polish stage): a paint smear on the helmet + pencil behind the ear.
  gi('lou', 'Lou, artist-soldier (hero)', 'thin', 'curlyCrop', '#5a3320'),
  // the three carriers: three body sizes, three hair colours, same uniform
  gi('carrier_tall', 'Tall carrier', 'thin', 'buzz', '#2a2420'),
  gi('carrier_stocky', 'Stocky carrier', 'fat', 'sidePart', '#c89a52'),
  gi('carrier_short', 'Short carrier', 'standard', 'cowlick', '#8a3a22'),
  // the two French cyclists
  wear(base({ name: 'farmer', label: 'Old Normandy farmer', size: 'thin', head: 'potato', outfit: 'factory', outfitPal: { a: WORKBLUE, b: '#2f4a72', c: BROWN } }), 'elderGrey', { col: '#d0ccd4', hat: 'slouch', hatCol: '#3a3430' }),
  wear(base({ name: 'boy', label: 'French boy, about 10', form: 'kid', outfit: 'newsboy', outfitPal: { a: '#8a7a5a', b: '#efe6d2', c: '#3f5f8f' } }), 'bowlCut', { col: '#6a4422' }),
  // THE MOCKER: the real armored-division sergeant (fat), leather tanker cap with goggles
  withGear(base({ name: 'sergeant', label: 'The sergeant (mocker)', size: 'fat', outfit: 'ww2Soldier', outfitPal: { a: OLIVED, b: KHAKI, c: '#3a2a1e' } }), 'buzz', { col: '#2a2420', helmet: 'pilot' }),
  // the sonic and radio specialists (no helmets: they work inside)
  wear(base({ name: 'sound_op', label: 'Sound operator', size: 'standard', outfit: 'ww2Soldier' }), 'slickBack', { col: '#2a2420' }),
  wear(base({ name: 'radio_op', label: 'Radio operator', size: 'thin', outfit: 'ww2Soldier', outfitPal: { a: OLIVE, b: KHAKI, c: '#2a2420' } }), 'pompadour', { col: '#c8a060' }),
  // the café
  wear(base({ name: 'spy', label: 'The café spy', size: 'thin', outfit: 'trench' }), 'slickBack', { col: '#1e1a1a', hat: 'fedora', hatCol: '#3a3532' }),
  wear(base({ name: 'waitress', label: 'Café waitress', form: 'lady', outfit: 'waitress', outfitPal: { a: '#e8dcc4', b: '#ffffff', c: NAVY } }), 'lowBun', { col: '#4a2e22' }),
  // the enemy photo interpreter
  wear(base({ name: 'interpreter', label: 'Enemy photo interpreter', size: 'standard', outfit: 'ww1', outfitPal: { a: FIELDGREY, b: '#4a4e4a', c: '#9a9c9a' } }), 'slickBack', { col: '#c8b48a', hat: 'police', hatCol: FIELDGREY }),
  // today: the attic
  wear(base({ name: 'grandchild', label: 'Grandchild (today)', form: 'kid', outfit: 'hoodie', outfitPal: { a: '#3f8fb0', b: '#ffffff', c: '#f2a23a' } }), 'pigtails', { col: '#5a3320' }),
  wear(base({ name: 'old_lou', label: 'Lou at 75 (today)', size: 'thin', head: 'potato', outfit: 'grandpa' }), 'elderGrey', { col: '#e4e2e8' }),
];
