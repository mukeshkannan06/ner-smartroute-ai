import en from './en.json';
import hi from './hi.json';
import ta from './ta.json';
import as from './as.json';
import mni from './mni.json';
import brx from './brx.json';
import kha from './kha.json';
import lus from './lus.json';

export const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', flag: '🇬🇧', speechCode: 'en-IN' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳', speechCode: 'hi-IN' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳', speechCode: 'ta-IN' },
  { code: 'as', name: 'Assamese', native: 'অসমীয়া', flag: '🌄', speechCode: 'as-IN' },
  { code: 'mni', name: 'Manipuri', native: 'ꯃꯤꯇꯩꯂꯣꯟ', flag: '🌄', speechCode: 'mni-IN' },
  { code: 'brx', name: 'Bodo', native: 'Bodo', flag: '🌄', speechCode: 'brx-IN' },
  { code: 'kha', name: 'Khasi', native: 'Khasi', flag: '🌄', speechCode: 'en-IN' },
  { code: 'lus', name: 'Mizo', native: 'Mizo ṭawng', flag: '🌄', speechCode: 'en-IN' },
];

export const TRANSLATIONS = {
  en,
  hi,
  ta,
  as,
  mni,
  brx,
  kha,
  lus,
};

export function getTranslation(lang, path) {
  const keys = path.split('.');
  let current = TRANSLATIONS[lang] || TRANSLATIONS.en;
  for (const k of keys) {
    if (current && current[k] !== undefined) {
      current = current[k];
    } else {
      // fallback to English
      let fallback = TRANSLATIONS.en;
      for (const fk of keys) {
        if (fallback && fallback[fk] !== undefined) {
          fallback = fallback[fk];
        } else {
          return path;
        }
      }
      return fallback;
    }
  }
  return current;
}
