import { smartFetch } from './config';

/**
 * Plan a real, road-following route between ANY two locations in India.
 * Backed by /api/routing/plan, which combines OSRM real road geometry
 * with the multi-hazard disaster-risk engine (flood, landslide, cyclone,
 * rainfall, road closures) to score and rank candidate routes.
 */
export async function calculateBestRoutes({
  origin,
  destination,
  vehicleType = 'truck',
  weight = 2.0,
  cargo = 'General Goods',
  monsoon = false,
  peakHour = false,
  mode = 'balanced',
}) {
  const res = await smartFetch('/routing/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      origin,
      destination,
      vehicle_type: vehicleType,
      weight_tonnes: Number(weight),
      cargo,
      season_monsoon: Boolean(monsoon),
      peak_hour: Boolean(peakHour),
      mode,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Routing calculation failed');
  }
  return res.json();
}

export async function simulateDisruption({
  roadId,
  reason = 'LANDSLIDE',
  vehicleType = 'truck',
  weight = 2.0,
}) {
  const res = await smartFetch('/digital-twin/simulate-disruption', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      road_id: roadId,
      reason,
      vehicle_type: vehicleType,
      weight_tonnes: Number(weight),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Simulation failed');
  }
  return res.json();
}

export async function reopenRoad(roadId) {
  const res = await smartFetch(`/digital-twin/reopen/${roadId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reopen road');
  return res.json();
}

export async function reopenAllRoads() {
  const res = await smartFetch('/digital-twin/reopen-all', {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to reopen all roads');
  return res.json();
}
