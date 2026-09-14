import React from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export function LanguageSelector() {
  const { language, setLanguage, languages } = useLanguage();

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      padding: '4px 10px',
      borderRadius: 'var(--radius-sm)',
      backgroundColor: 'var(--sand-100)',
      border: '1px solid var(--border-color)',
    }}>
      <Globe size={15} color="var(--forest-800)" />
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        style={{
          border: 'none',
          backgroundColor: 'transparent',
          color: 'var(--forest-900)',
          fontSize: '12.5px',
          fontWeight: 600,
          outline: 'none',
          cursor: 'pointer',
        }}
      >
        {languages.map((l) => (
          <option key={l.code} value={l.code}>
            {l.flag} {l.native} ({l.name})
          </option>
        ))}
      </select>
    </div>
  );
}
