import React from 'react';
import { SmartRouteMap } from '../components/map/SmartRouteMap';
import { RoutePlanner } from '../components/routing/RoutePlanner';

export function SmartRoutesPage() {
  return (
    <div className="grid-2col" style={{ alignItems: 'start' }}>
      <RoutePlanner />
      <div style={{ position: 'sticky', top: '24px' }}>
        <SmartRouteMap height="600px" />
      </div>
    </div>
  );
}
