import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';
import { SmartRouteMap } from '../components/map/SmartRouteMap';
import { useRouteContext } from '../context/RouteContext';

export function IncidentsPage() {
  const { incidents } = useRouteContext();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <SmartRouteMap height="400px" />

      <div className="glass-panel">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <ShieldAlert size={22} color="var(--crimson)" />
          <div>
            <h2 style={{ fontSize: '18px', color: 'var(--forest-900)' }}>
              Active NER Network Hazards & Warning Sensors
            </h2>
            <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
              Real-time telemetry and hazard alert mesh for critical North-East arterial highways.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
          {incidents.map((inc) => {
            const isHigh = inc.severity === 'High';
            return (
              <div
                key={inc.incident_id}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: '#FFFFFF',
                  border: isHigh ? '1px solid var(--crimson-light)' : '1px solid var(--border-color)',
                  boxShadow: 'var(--shadow-sm)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--forest-900)', fontSize: '13.5px' }}>
                    {inc.road_name}
                  </span>
                  <span className={`badge-pill ${isHigh ? 'badge-crimson' : 'badge-amber'}`}>
                    {inc.severity} Severity
                  </span>
                </div>

                <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-light)', marginBottom: '8px' }}>
                  TYPE: {inc.type.replace('_', ' ')} • ID: {inc.incident_id}
                </div>

                <p style={{ fontSize: '12.5px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  {inc.message}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
