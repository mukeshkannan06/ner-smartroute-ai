import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { useRouteContext } from '../../context/RouteContext';
import { MapLegend } from './MapLegend';
import { fetchPanIndiaHazards } from '../../services/api';

const HAZARD_ICON = {
  FLOOD: '🌊',
  LANDSLIDE: '⛰️',
  CYCLONE: '🌪️',
  HEAVY_RAIN: '🌧️',
  ROAD_CLOSURE: '🚧',
};

const HAZARD_COLOR = {
  CRITICAL: '#C93B3B',
  HIGH: '#D97350',
  MODERATE: '#D99B26',
};

export function SmartRouteMap({ height = '460px' }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef({
    roads: L.layerGroup(),
    nodes: L.layerGroup(),
    routes: L.layerGroup(),
    incidents: L.layerGroup(),
    panHazards: L.layerGroup(),
  });
  const [panHazards, setPanHazards] = useState([]);
  const [showPanHazards, setShowPanHazards] = useState(true);

  const {
    nodes,
    roads,
    incidents,
    routeResults,
    selectedCandidateIndex,
    mapFocus,
    mapZoom,
    setOrigin,
    setDestination,
  } = useRouteContext();

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: mapFocus || [25.5, 93.0],
      zoom: mapZoom || 7,
      zoomControl: true,
    });

    // Standard OpenStreetMap Tile Layer (No API key required)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    layersRef.current.roads.addTo(map);
    layersRef.current.routes.addTo(map);
    layersRef.current.nodes.addTo(map);
    layersRef.current.incidents.addTo(map);
    layersRef.current.panHazards.addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Load pan-India hazard incidents (flood/landslide/cyclone/road closure) once.
  useEffect(() => {
    let cancelled = false;
    fetchPanIndiaHazards()
      .then((res) => {
        if (!cancelled) setPanHazards(res.hazards || []);
      })
      .catch(() => {
        if (!cancelled) setPanHazards([]);
      });
    return () => { cancelled = true; };
  }, []);

  // Render pan-India hazard markers (toggleable layer)
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    layersRef.current.panHazards.clearLayers();
    if (!showPanHazards) return;

    panHazards.forEach((hz) => {
      const color = HAZARD_COLOR[hz.severity] || '#2B75A0';
      const icon = L.divIcon({
        className: 'pan-hazard-marker-icon',
        html: `
          <div style="
            width: 26px; height: 26px; border-radius: 50%;
            background: ${color}; border: 2px solid #FFFFFF;
            box-shadow: 0 2px 6px rgba(0,0,0,0.35);
            display: flex; align-items: center; justify-content: center;
            font-size: 13px;
          ">${HAZARD_ICON[hz.type] || '⚠️'}</div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      });

      const marker = L.marker([hz.lat, hz.lon], { icon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px; max-width: 220px;">
          <div style="font-weight: 700; color: ${color};">
            ${HAZARD_ICON[hz.type] || '⚠️'} ${hz.type.replace('_', ' ')} (${hz.severity})
          </div>
          <div style="font-size: 11.5px; color: #5E6963; margin: 2px 0 6px;">${hz.location}</div>
          <p style="margin: 0; line-height: 1.35;">${hz.message}</p>
          ${hz.blocked ? '<div style="margin-top:6px; font-weight:700; color:#C93B3B;">🚫 Road Blocked</div>' : ''}
        </div>
      `);
      layersRef.current.panHazards.addLayer(marker);
    });
  }, [panHazards, showPanHazards]);

  // Update Base Road Network
  useEffect(() => {
    if (!mapInstanceRef.current || !roads.length || !Object.keys(nodes).length) return;

    layersRef.current.roads.clearLayers();

    roads.forEach((road) => {
      const nodeA = nodes[road.a];
      const nodeB = nodes[road.b];
      if (!nodeA || !nodeB) return;

      const isClosed = road.status === 'CLOSED';
      const color = isClosed ? '#C93B3B' : (road.road_type === 'NH' ? '#423E34' : '#8C8472');
      const weight = road.road_type === 'NH' ? 3.5 : 2.5;
      const dashArray = isClosed ? '6, 6' : undefined;

      const poly = L.polyline([[nodeA.lat, nodeA.lon], [nodeB.lat, nodeB.lon]], {
        color,
        weight,
        opacity: isClosed ? 0.9 : 0.45,
        dashArray,
      });

      poly.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <div style="font-weight: 700; color: #142E24;">${road.road_id} (${road.a} ↔ ${road.b})</div>
          <div>Type: <b>${road.road_type}</b> (${road.terrain})</div>
          <div>Base Condition: <b>${road.base_condition}/100</b></div>
          <div>Status: <b style="color: ${isClosed ? '#C93B3B' : '#2E8B57'}">${road.status}</b></div>
        </div>
      `);

      layersRef.current.roads.addLayer(poly);
    });
  }, [roads, nodes]);

  // Update Node City Markers
  useEffect(() => {
    if (!mapInstanceRef.current || !Object.keys(nodes).length) return;

    layersRef.current.nodes.clearLayers();

    Object.entries(nodes).forEach(([name, data]) => {
      const icon = L.divIcon({
        className: 'custom-node-marker',
        html: `
          <div style="
            background: #142E24;
            color: #FFFFFF;
            border: 2px solid #F5EFEB;
            border-radius: 50%;
            width: 14px;
            height: 14px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
          "></div>
          <div style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 11px;
            font-weight: 700;
            color: #142E24;
            background: rgba(255,255,255,0.92);
            padding: 2px 6px;
            border-radius: 4px;
            white-space: nowrap;
            margin-top: 2px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15);
            display: inline-block;
          ">${name}</div>
        `,
        iconSize: [20, 20],
        iconAnchor: [7, 7],
      });

      const marker = L.marker([data.lat, data.lon], { icon });
      marker.bindPopup(`
        <div style="font-family: sans-serif;">
          <h4 style="margin: 0 0 4px; color: #142E24;">${name}</h4>
          <div>Population: <b>${data.population ? data.population.toLocaleString() : 'N/A'}</b></div>
          <div>Key Hospitals: <b>${data.hospitals || 'N/A'}</b></div>
          <div style="margin-top: 8px; display: flex; gap: 6px;">
            <button onclick="window.__setOrigin('${name}')" style="padding: 3px 8px; background: #142E24; color: #fff; border-radius: 4px; font-size: 11px; border:none; cursor:pointer;">Set Origin</button>
            <button onclick="window.__setDest('${name}')" style="padding: 3px 8px; background: #B5502D; color: #fff; border-radius: 4px; font-size: 11px; border:none; cursor:pointer;">Set Destination</button>
          </div>
        </div>
      `);

      layersRef.current.nodes.addLayer(marker);
    });

    window.__setOrigin = (name) => setOrigin(name);
    window.__setDest = (name) => setDestination(name);
  }, [nodes]);

  // Update Incident Hazard Markers
  useEffect(() => {
    if (!mapInstanceRef.current || !incidents.length) return;

    layersRef.current.incidents.clearLayers();

    incidents.forEach((inc) => {
      const isHigh = inc.severity === 'High';
      const color = isHigh ? '#C93B3B' : (inc.severity === 'Medium' ? '#D99B26' : '#2B75A0');

      const icon = L.divIcon({
        className: 'incident-marker-icon',
        html: `
          <div style="
            position: relative;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="
              position: absolute;
              width: 22px;
              height: 22px;
              border-radius: 50%;
              background-color: ${color};
              opacity: 0.3;
              animation: pulse-ring 1.8s infinite;
            "></div>
            <div style="
              width: 14px;
              height: 14px;
              border-radius: 50%;
              background-color: ${color};
              border: 2px solid #FFFFFF;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>
          </div>
        `,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      const marker = L.marker([inc.lat, inc.lon], { icon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px;">
          <div style="font-weight: 700; color: ${color};">${inc.type.replace('_', ' ')} (${inc.severity})</div>
          <div style="font-size: 11.5px; color: #5E6963; margin-bottom: 4px;">Corridor: ${inc.road_name}</div>
          <p style="margin: 0; line-height: 1.35;">${inc.message}</p>
        </div>
      `);

      layersRef.current.incidents.addLayer(marker);
    });
  }, [incidents]);

  // Update Route Polylines when candidate routes are computed.
  // CRITICAL: uses the real road geometry returned by the backend (OSRM
  // road-following coordinates, already normalized to [lat, lon] for
  // Leaflet) — NOT a straight line built from city node coordinates.
  useEffect(() => {
    if (!mapInstanceRef.current || !routeResults) return;

    layersRef.current.routes.clearLayers();

    const candidates = routeResults.candidates || [];
    const allCoords = [];

    const geometryFor = (candidate) => {
      // Primary source of truth: real road-following geometry from the backend.
      if (Array.isArray(candidate.geometry) && candidate.geometry.length >= 2) {
        return candidate.geometry;
      }
      // Fallback only if a route somehow has no geometry at all (e.g. very
      // old cached response): reconstruct from known city nodes so the map
      // doesn't crash, though this will not follow real roads.
      return (candidate.path || [])
        .map((cityName) => {
          const node = nodes[cityName];
          return node ? [node.lat, node.lon] : null;
        })
        .filter(Boolean);
    };

    // Render candidate alternate routes in reverse order so the
    // recommended/selected route is drawn on top.
    [...candidates].reverse().forEach((candidate, revIdx) => {
      const idx = candidates.length - 1 - revIdx;
      const isSelected = idx === selectedCandidateIndex;
      const isRecommended = idx === 0;

      const coords = geometryFor(candidate);
      if (coords.length < 2) return;

      if (isSelected) {
        allCoords.push(...coords);
      }

      const baseColor = isRecommended ? '#2E8B57' : (isSelected ? '#B5502D' : '#D99B26');
      const weight = isSelected ? 6.5 : 3.5;
      const opacity = isSelected ? 0.95 : 0.4;

      const poly = L.polyline(coords, {
        color: baseColor,
        weight,
        opacity,
        lineJoin: 'round',
      });

      const pathLabel = (candidate.path && candidate.path.length > 1)
        ? candidate.path.join(' → ')
        : `${routeResults.origin?.name || 'Origin'} → ${routeResults.destination?.name || 'Destination'}`;

      poly.bindPopup(`
        <div style="font-family: sans-serif; font-size: 13px; max-width: 240px;">
          <div style="font-weight: 700; color: ${baseColor};">
            ${isRecommended ? '⭐ RECOMMENDED ROUTE' : `Alternate Route #${idx + 1}`}
          </div>
          <div style="font-size: 11.5px; color: #5E6963; margin: 2px 0 6px;">${pathLabel}</div>
          <div>Distance: <b>${candidate.total_distance_km ?? candidate.distance_km} km</b></div>
          <div>ETA: <b>${candidate.eta_hours ?? candidate.duration_hours} hrs</b></div>
          <div>Risk: <b>${Math.round((candidate.risk_probability || 0) * 100)}% (${candidate.risk_level || 'LOW'})</b></div>
          ${candidate.safety_score != null ? `<div>Safety Score: <b>${Math.round(candidate.safety_score)}/100</b></div>` : ''}
          <div>Cost: <b>₹${Math.round(candidate.estimated_cost_inr || 0).toLocaleString()}</b></div>
          <div style="font-size: 10.5px; color: #9B9285; margin-top: 6px;">
            Source: ${candidate.source === 'osrm' ? 'Real road route (OSRM)' : 'Prototype network'}
          </div>
        </div>
      `);

      layersRef.current.routes.addLayer(poly);

      // Overlay hazard-risk-colored segments on top of the selected route so
      // the corridor visibly changes color where flood/landslide/cyclone/
      // rainfall/road-closure risk rises (green → yellow → orange → red).
      if (isSelected && Array.isArray(candidate.segment_points) && candidate.segment_points.length > 1) {
        for (let i = 0; i < candidate.segment_points.length - 1; i++) {
          const a = candidate.segment_points[i];
          const b = candidate.segment_points[i + 1];
          if (!a?.coord || !b?.coord) continue;
          const segColor = b.color || a.color || baseColor;
          if (segColor === '#2E8B57') continue; // skip drawing over low-risk (already green base line)
          const segLine = L.polyline([a.coord, b.coord], {
            color: segColor,
            weight: 7,
            opacity: 0.9,
            lineCap: 'round',
          });
          segLine.bindTooltip(`${a.level} risk (${a.risk_score}/100)`, { sticky: true });
          layersRef.current.routes.addLayer(segLine);
        }
      }
    });

    if (allCoords.length > 0 && mapInstanceRef.current) {
      try {
        const bounds = L.latLngBounds(allCoords);
        mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40] });
      } catch (err) {
        console.warn('Could not fit bounds', err);
      }
    }
  }, [routeResults, selectedCandidateIndex, nodes]);

  return (
    <div style={{ position: 'relative', width: '100%', height, borderRadius: 'var(--radius-lg)', overflow: 'hidden', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-md)' }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />
      <button
        type="button"
        onClick={() => setShowPanHazards((v) => !v)}
        style={{
          position: 'absolute',
          top: '12px',
          right: '12px',
          zIndex: 1000,
          padding: '6px 12px',
          fontSize: '11.5px',
          fontWeight: 600,
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-color)',
          backgroundColor: showPanHazards ? 'var(--forest-700)' : '#FFFFFF',
          color: showPanHazards ? '#FFFFFF' : 'var(--forest-900)',
          boxShadow: 'var(--shadow-md)',
          cursor: 'pointer',
        }}
      >
        {showPanHazards ? '☑' : '☐'} India Hazard Layer
      </button>
      <MapLegend />
    </div>
  );
}
