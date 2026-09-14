import React from 'react';
import { Info } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export function DataModeBanner() {
  const { t } = useLanguage();

  return (
    <div style={{
      backgroundColor: 'var(--sand-200)',
      borderBottom: '1px solid var(--border-color)',
      padding: '8px 32px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      fontSize: '12px',
      color: 'var(--forest-800)',
    }}>
      <Info size={15} color="var(--clay-600)" />
      <span>{t('app.data_mode_notice')}</span>
    </div>
  );
}
