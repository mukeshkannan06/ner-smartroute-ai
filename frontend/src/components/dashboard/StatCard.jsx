import React from 'react';

export function StatCard({ title, value, unit, subtitle, icon: Icon, color = 'emerald', badge }) {
  const colorMap = {
    emerald: {
      bg: 'var(--emerald-light)',
      text: 'var(--emerald)',
      border: 'rgba(46, 139, 87, 0.25)',
    },
    amber: {
      bg: 'var(--amber-light)',
      text: 'var(--amber)',
      border: 'rgba(217, 155, 38, 0.25)',
    },
    crimson: {
      bg: 'var(--crimson-light)',
      text: 'var(--crimson)',
      border: 'rgba(201, 59, 59, 0.25)',
    },
    forest: {
      bg: 'var(--sand-200)',
      text: 'var(--forest-800)',
      border: 'var(--border-color)',
    },
  };

  const scheme = colorMap[color] || colorMap.emerald;

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-md)',
      padding: '20px 22px',
      boxShadow: 'var(--shadow-sm)',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            backgroundColor: scheme.bg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: scheme.text,
          }}>
            <Icon size={16} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
        <span style={{
          fontSize: '28px',
          fontWeight: 700,
          fontFamily: 'var(--font-mono)',
          color: 'var(--forest-900)',
          lineHeight: 1,
        }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: 500 }}>
            {unit}
          </span>
        )}
      </div>

      {subtitle && (
        <div style={{
          fontSize: '11.5px',
          color: 'var(--text-light)',
          marginTop: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <span>{subtitle}</span>
          {badge && <span className={`badge-pill badge-${color}`}>{badge}</span>}
        </div>
      )}
    </div>
  );
}
