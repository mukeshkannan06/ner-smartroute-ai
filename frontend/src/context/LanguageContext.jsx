import React, { createContext, useContext, useState, useEffect } from 'react';
import { LANGUAGES, getTranslation } from '../i18n';

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('ner_smartroute_lang') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('ner_smartroute_lang', language);
  }, [language]);

  const t = (path) => getTranslation(language, path);

  const currentLanguageObj = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, languages: LANGUAGES, currentLanguageObj }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
