import React from 'react';
import { SmartRouteMap } from '../components/map/SmartRouteMap';
import { DigitalTwin } from '../components/digital_twin/DigitalTwin';

export function DigitalTwinPage() {
  return (
    <div className="grid-2col" style={{ alignItems: 'start' }}>
      <DigitalTwin />
      <div style={{ position: 'sticky', top: '24px' }}>
        <SmartRouteMap height="560px" />
      </div>
    </div>
  );
}
