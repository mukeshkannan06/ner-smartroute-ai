import React from 'react';

export function MapLegend() {
  return (
    <div style={{
      position: 'absolute',
      bottom: '16px',
      right: '16px',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(8px)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-md)',
      padding: '12px 16px',
      zIndex: 1000,
      fontSize: '11.5px',
      boxShadow: 'var(--shadow-md)',
      maxWidth: '220px',
    }}>
      <div style={{ fontWeight: 700, marginBottom: '8px', color: 'var(--forest-900)' }}>
        Map Layers & Legend
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '18px', height: '4px', backgroundColor: '#2E8B57', borderRadius: '2px' }}></span>
          <span>Optimal / Low Risk Route</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '18px', height: '4px', backgroundColor: '#D99B26', borderRadius: '2px' }}></span>
          <span>Alternative / Moderate Risk</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '18px', height: '4px', backgroundColor: '#C93B3B', borderRadius: '2px', borderStyle: 'dashed' }}></span>
          <span>Disrupted / Closed Road</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
          <span style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#C93B3B',
            display: 'inline-block',
          }}></span>
          <span>Active Hazard / Landslide</span>
        </div>
      </div>
    </div>
  );
}
