import React from 'react';
import { Activity, ShieldAlert, AlertTriangle, Truck, MapPin, Gauge } from 'lucide-react';
import { StatCard } from './StatCard';
import { CorridorHealthTable } from './CorridorHealthTable';
import { useRouteContext } from '../../context/RouteContext';
import { useLanguage } from '../../context/LanguageContext';

export function GovernmentDashboard() {
  const { govData, roads, incidents } = useRouteContext();
  const { t } = useLanguage();

  const closedRoads = roads.filter((r) => r.status === 'CLOSED').length;
  const accessScore = govData?.network_accessibility_score || 82.4;
  const criticalCount = (govData?.critical_corridors || []).length;
  const highRiskCount = (govData?.high_risk_roads || []).length;
  const vehiclesTracked = govData?.vehicles_tracked || 0;

  return (
    <div className="glass-panel">
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '18px', color: 'var(--forest-900)' }}>
          {t('gov.title')}
        </h2>
        <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
          Network-wide live telemetry, accessibility index, and corridor resilience surveillance.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: '16px',
      }}>
        <StatCard
          title={t('gov.accessibility_index')}
          value={Math.round(accessScore * 10) / 10}
          unit="/100"
          subtitle="Regional connectivity"
          icon={Gauge}
          color={accessScore > 75 ? 'emerald' : 'amber'}
          badge={accessScore > 75 ? 'Optimal' : 'Compromised'}
        />

        <StatCard
          title={t('gov.critical_corridors')}
          value={criticalCount}
          subtitle="Sole lifeline links"
          icon={Activity}
          color="amber"
        />

        <StatCard
          title={t('gov.high_risk_roads')}
          value={highRiskCount}
          subtitle="Terrain/Rain hazard"
          icon={ShieldAlert}
          color={highRiskCount > 0 ? 'crimson' : 'emerald'}
        />

        <StatCard
          title={t('gov.active_disruptions')}
          value={closedRoads}
          subtitle="Emergency closures"
          icon={AlertTriangle}
          color={closedRoads > 0 ? 'crimson' : 'emerald'}
        />

        <StatCard
          title="Active Freight Shipments"
          value={vehiclesTracked}
          subtitle="Digital Twin Monitored"
          icon={Truck}
          color="forest"
        />
      </div>

      <CorridorHealthTable />
    </div>
  );
}
