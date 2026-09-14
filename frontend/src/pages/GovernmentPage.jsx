import React from 'react';
import { SmartRouteMap } from '../components/map/SmartRouteMap';
import { GovernmentDashboard } from '../components/dashboard/GovernmentDashboard';

export function GovernmentPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <SmartRouteMap height="400px" />
      <GovernmentDashboard />
    </div>
  );
}
