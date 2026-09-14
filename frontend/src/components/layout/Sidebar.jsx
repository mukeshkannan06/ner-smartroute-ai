import React from 'react';
import {
  Compass,
  Navigation,
  Activity,
  ShieldAlert,
  BarChart3,
  Cpu,
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export function Sidebar({ activeTab, setActiveTab }) {
  const { t } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('nav.dashboard'), icon: Activity },
    { id: 'planner', label: t('nav.smart_routes'), icon: Navigation },
    { id: 'twin', label: t('nav.digital_twin'), icon: Cpu },
    { id: 'gov', label: t('nav.government'), icon: BarChart3 },
    { id: 'incidents', label: t('nav.incidents'), icon: ShieldAlert },
  ];

  return (
    <aside className="app-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Compass size={22} />
        </div>
        <div className="sidebar-title-group">
          <h2 className="sidebar-title">
            NER SmartRoute
          </h2>
          <span className="sidebar-subtitle">
            Digital Twin AI
          </span>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-nav-btn ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} color={isActive ? 'var(--clay-400)' : 'var(--moss)'} />
              <span className="sidebar-nav-label">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Corridor Quick Status */}
      <div className="sidebar-status-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--moss-light)', fontFamily: 'var(--font-mono)' }}>
            NETWORK NODES
          </span>
          <span className="badge-pill badge-emerald" style={{ fontSize: '9px', padding: '2px 6px' }}>
            11 Cities
          </span>
        </div>
        <p style={{ fontSize: '11.5px', color: 'var(--sand-400)', lineHeight: '1.4' }}>
          Multi-layer GIS graph connected via NH/SH primary arteries.
        </p>
      </div>
    </aside>
  );
}
