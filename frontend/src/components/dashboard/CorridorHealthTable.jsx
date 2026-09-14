import React from 'react';
import { useRouteContext } from '../../context/RouteContext';

export function CorridorHealthTable() {
  const { roads } = useRouteContext();

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-md)',
      overflow: 'hidden',
      marginTop: '20px',
    }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--sand-50)' }}>
        <h3 style={{ fontSize: '15px', color: 'var(--forest-900)' }}>
          Highway Arteries & Quality Monitoring (NER Corridor Mesh)
        </h3>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <th style={{ padding: '12px 20px' }}>ROAD ID</th>
              <th style={{ padding: '12px 20px' }}>SEGMENT</th>
              <th style={{ padding: '12px 20px' }}>CLASSIFICATION</th>
              <th style={{ padding: '12px 20px' }}>DISTANCE</th>
              <th style={{ padding: '12px 20px' }}>TERRAIN</th>
              <th style={{ padding: '12px 20px' }}>BASE HEALTH</th>
              <th style={{ padding: '12px 20px' }}>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {roads.map((road) => {
              const isClosed = road.status === 'CLOSED';
              return (
                <tr
                  key={road.road_id}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    backgroundColor: isClosed ? 'var(--crimson-light)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '12px 20px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {road.road_id}
                  </td>
                  <td style={{ padding: '12px 20px', fontWeight: 600, color: 'var(--forest-900)' }}>
                    {road.a} ↔ {road.b}
                  </td>
                  <td style={{ padding: '12px 20px' }}>
                    <span className="badge-pill badge-forest" style={{ fontSize: '10px' }}>
                      {road.road_type} ({road.surface})
                    </span>
                  </td>
                  <td style={{ padding: '12px 20px', fontFamily: 'var(--font-mono)' }}>
                    {road.distance_km} km
                  </td>
                  <td style={{ padding: '12px 20px', textTransform: 'capitalize' }}>
                    {road.terrain}
                  </td>
                  <td style={{ padding: '12px 20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        flex: 1,
                        height: '6px',
                        backgroundColor: 'var(--sand-200)',
                        borderRadius: '3px',
                        overflow: 'hidden',
                        maxWidth: '80px',
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${road.base_condition}%`,
                          backgroundColor: road.base_condition > 75 ? 'var(--emerald)' : (road.base_condition > 60 ? 'var(--amber)' : 'var(--crimson)'),
                        }}></div>
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                        {road.base_condition}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 20px' }}>
                    <span className={`badge-pill ${isClosed ? 'badge-crimson' : 'badge-emerald'}`}>
                      {road.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
