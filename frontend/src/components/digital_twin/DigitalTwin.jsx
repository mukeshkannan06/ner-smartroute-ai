import React, { useState } from 'react';
import { Cpu, AlertTriangle, RefreshCw, CheckCircle2, Play } from 'lucide-react';
import { useRouteContext } from '../../context/RouteContext';
import { useLanguage } from '../../context/LanguageContext';
import { simulateDisruption, reopenAllRoads } from '../../services/routingService';
import { ImpactReport } from './ImpactReport';

export function DigitalTwin() {
  const { roads, refreshNetwork, twinImpact, setTwinImpact } = useRouteContext();
  const { t } = useLanguage();

  const [selectedRoad, setSelectedRoad] = useState(roads[0]?.road_id || 'NH-001');
  const [disruptionType, setDisruptionType] = useState('LANDSLIDE');
  const [simulating, setSimulating] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleSimulate = async (e) => {
    e?.preventDefault();
    try {
      setSimulating(true);
      setSuccessMsg(null);
      const res = await simulateDisruption({
        roadId: selectedRoad,
        reason: disruptionType,
      });
      setTwinImpact(res);
      await refreshNetwork();
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  const handleReopenAll = async () => {
    try {
      setSimulating(true);
      await reopenAllRoads();
      setTwinImpact(null);
      setSuccessMsg('All road corridors reopened successfully.');
      await refreshNetwork();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <div className="glass-panel">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontSize: '18px', color: 'var(--forest-900)' }}>
            {t('twin.title')}
          </h2>
          <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
            {t('twin.subtitle')}
          </p>
        </div>
        <div style={{
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          backgroundColor: 'var(--forest-700)',
          color: 'var(--sand-100)',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
        }}>
          PHYSICAL-GIS MIRROR
        </div>
      </div>

      {successMsg && (
        <div style={{
          padding: '10px 14px',
          marginBottom: '16px',
          backgroundColor: 'var(--emerald-light)',
          color: 'var(--forest-900)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '12.5px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <CheckCircle2 size={16} color="var(--emerald)" />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSimulate}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
          <div className="form-group">
            <label className="form-label">{t('twin.select_road')}</label>
            <select
              className="form-select"
              value={selectedRoad}
              onChange={(e) => setSelectedRoad(e.target.value)}
            >
              {roads.map((r) => (
                <option key={r.road_id} value={r.road_id}>
                  {r.road_id}: {r.a} ↔ {r.b} ({r.road_type}, {r.terrain}, {r.status})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('twin.disruption_type')}</label>
            <select
              className="form-select"
              value={disruptionType}
              onChange={(e) => setDisruptionType(e.target.value)}
            >
              <option value="LANDSLIDE">⛰️ Landslide / Rockfall</option>
              <option value="FLOOD">🌊 Flash Flood / Waterlogging</option>
              <option value="ROAD_CLOSURE">🚧 Highway Construction / Maintenance</option>
              <option value="BRIDGE_CLOSURE">🌉 Structural Bridge Closure</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', marginTop: '6px' }}>
          <button
            type="submit"
            disabled={simulating}
            className="btn-secondary"
            style={{ flex: 1 }}
          >
            <Play size={16} />
            <span>{simulating ? 'Simulating...' : t('twin.simulate_btn')}</span>
          </button>

          <button
            type="button"
            onClick={handleReopenAll}
            disabled={simulating}
            className="btn-outline"
          >
            <RefreshCw size={16} />
            <span>{t('twin.reopen_all')}</span>
          </button>
        </div>
      </form>

      <ImpactReport impact={twinImpact} />
    </div>
  );
}
