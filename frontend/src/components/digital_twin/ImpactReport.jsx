import React from 'react';
import { AlertTriangle, TrendingDown, ArrowRight, ShieldCheck } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export function ImpactReport({ impact }) {
  const { t } = useLanguage();
  if (!impact) return null;

  const roadClosed = impact.road_closed || {};
  const affected = impact.affected_shipments || [];

  return (
    <div style={{
      marginTop: '20px',
      padding: '20px',
      borderRadius: 'var(--radius-md)',
      backgroundColor: 'var(--sand-50)',
      border: '1px solid var(--border-color)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="var(--crimson)" />
          <h4 style={{ fontSize: '15px', color: 'var(--crimson)' }}>
            Disruption Active: {roadClosed.road_id} ({roadClosed.a} ↔ {roadClosed.b})
          </h4>
        </div>
        <span className="badge-pill badge-crimson">
          - {impact.accessibility_loss_pts} pts Access Drop
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
        marginBottom: '16px',
      }}>
        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-light)' }}>CLOSED CORRIDOR</div>
          <div style={{ fontWeight: 700, color: 'var(--forest-900)' }}>
            {roadClosed.road_id} ({roadClosed.road_type})
          </div>
        </div>

        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-light)' }}>AFFECTED SHIPMENTS</div>
          <div style={{ fontWeight: 700, color: 'var(--crimson)' }}>
            {affected.length} In-Transit
          </div>
        </div>

        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-light)' }}>DISRUPTION CAUSE</div>
          <div style={{ fontWeight: 700, color: 'var(--amber)' }}>
            {impact.reason || 'LANDSLIDE'}
          </div>
        </div>
      </div>

      {/* Reroute evaluation for shipments */}
      {affected.length > 0 ? (
        <div style={{ marginTop: '12px' }}>
          <h5 style={{ fontSize: '13px', marginBottom: '8px', color: 'var(--forest-900)' }}>
            Computed Dynamic Reroutes:
          </h5>
          {affected.map((item, idx) => (
            <div
              key={idx}
              style={{
                padding: '12px 14px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: '#FFFFFF',
                border: '1px solid var(--emerald-light)',
                marginBottom: '8px',
                fontSize: '12.5px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontWeight: 700, color: 'var(--forest-900)' }}>
                  Shipment {item.shipment?.shipment_id || `SHIP-${idx + 1}`}: {item.shipment?.cargo} ({item.shipment?.origin} → {item.shipment?.destination})
                </span>
                <span className="badge-pill badge-emerald">
                  <ShieldCheck size={12} /> Auto-Rerouted
                </span>
              </div>
              <div style={{ color: 'var(--text-muted)' }}>
                New Path: <b>{item.reroute?.path?.join(' → ')}</b> ({item.reroute?.total_distance_km} km, +{item.extra_distance_km || 0} km detour)
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ fontSize: '12.5px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
          No active shipments were currently using this specific road segment. General traffic has been dynamically redirected to secondary corridors.
        </div>
      )}
    </div>
  );
}
