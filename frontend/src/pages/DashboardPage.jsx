import React from 'react';
import { SmartRouteMap } from '../components/map/SmartRouteMap';
import { RoutePlanner } from '../components/routing/RoutePlanner';
import { GovernmentDashboard } from '../components/dashboard/GovernmentDashboard';
import { DigitalTwin } from '../components/digital_twin/DigitalTwin';

export function DashboardPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Map View */}
      <div style={{ width: '100%' }}>
        <SmartRouteMap height="440px" />
      </div>

      {/* Grid: Route Planner + Digital Twin */}
      <div className="grid-2col">
        <RoutePlanner />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <DigitalTwin />
          <GovernmentDashboard />
        </div>
      </div>
    </div>
  );
}
