import React from 'react';
import { RefreshCw } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';
import { useRouteContext } from '../../context/RouteContext';
import { LanguageSelector } from '../chat/LanguageSelector';

export function Header() {
  const { t } = useLanguage();
  const { backendStatus, refreshNetwork, loading } = useRouteContext();

  const getStatusBadge = () => {
    switch (backendStatus) {
      case 'online':
        return {
          dotClass: 'status-dot',
          badgeClass: 'header-status-badge',
          text: 'AI ENGINE ONLINE',
          title: 'Backend connected',
        };
      case 'waking_up':
      case 'connecting':
        return {
          dotClass: 'status-dot waking',
          badgeClass: 'header-status-badge waking',
          text: loading ? 'CONNECTING / SPINNING UP...' : 'WAKING UP (RENDER)...',
          title: 'Render free tier backend is waking up (takes ~60s). Click to retry.',
        };
      case 'offline':
      default:
        return {
          dotClass: 'status-dot offline',
          badgeClass: 'header-status-badge offline',
          text: 'BACKEND OFFLINE (RETRY)',
          title: 'Click to retry connection to backend',
        };
    }
  };

  const status = getStatusBadge();

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
        {/* Dynamic Engine Status Badge */}
        <div
          className={status.badgeClass}
          onClick={backendStatus !== 'online' ? refreshNetwork : undefined}
          style={{ cursor: backendStatus !== 'online' ? 'pointer' : 'default' }}
          title={status.title}
        >
          <span className={status.dotClass}></span>
          <span className="status-text">{status.text}</span>
          {backendStatus !== 'online' && (
            <RefreshCw
              size={12}
              className={loading ? 'spin-icon' : ''}
              style={{ marginLeft: '4px', opacity: 0.7 }}
            />
          )}
        </div>

        {/* Language Selector Dropdown */}
        <LanguageSelector />
      </div>
    </header>
  );
}
