import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { LanguageSelector } from '../chat/LanguageSelector';

export function Header() {
  const { t } = useLanguage();

  return (
    <header className="app-header">
      <div className="header-titles">
        <h1 className="header-title">
          {t('app.title')}
        </h1>
        <p className="header-subtitle">
          {t('app.subtitle')}
        </p>
      </div>

      <div className="header-actions">
        {/* Live Engine Status */}
        <div className="header-status-badge">
          <span className="status-dot"></span>
          <span className="status-text">
            AI ENGINE ONLINE
          </span>
        </div>

        {/* Language Selector Dropdown */}
        <LanguageSelector />
      </div>
    </header>
  );
}
