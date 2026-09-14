import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchNodes, fetchRoads, fetchIncidents, fetchGovDashboard } from '../services/api';

const RouteContext = createContext();

export function RouteProvider({ children }) {
  // Network GIS Data
  const [nodes, setNodes] = useState({});
  const [roads, setRoads] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [govData, setGovData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Active Route Planning State
  const [origin, setOrigin] = useState('Guwahati');
  const [destination, setDestination] = useState('Imphal');
  const [vehicleType, setVehicleType] = useState('truck');
  const [cargo, setCargo] = useState('Vegetables');
  const [weight, setWeight] = useState(2.0);
  const [monsoon, setMonsoon] = useState(false);
  const [peakHour, setPeakHour] = useState(false);

  // Computed Route Results
  const [routeResults, setRouteResults] = useState(null);
  const [selectedCandidateIndex, setSelectedCandidateIndex] = useState(0);
  const [routeMode, setRouteMode] = useState('balanced');

  // Disruption / Digital Twin State
  const [activeDisruption, setActiveDisruption] = useState(null);
  const [disruptedRoadId, setDisruptedRoadId] = useState('NH-001');
  const [disruptionReason, setDisruptionReason] = useState('LANDSLIDE');
  const [twinImpact, setTwinImpact] = useState(null);

  // Map viewport & interaction state
  const [mapFocus, setMapFocus] = useState([25.5, 93.0]);
  const [mapZoom, setMapZoom] = useState(7);
  const [highlightedCorridor, setHighlightedCorridor] = useState(null);

  // Load initial network state
  const refreshNetwork = async () => {
    try {
      setLoading(true);
      const [nodesData, roadsData, incidentsData, dashData] = await Promise.all([
        fetchNodes(),
        fetchRoads(),
        fetchIncidents(),
        fetchGovDashboard(),
      ]);
      setNodes(nodesData || {});
      setRoads(roadsData || []);
      setIncidents(incidentsData || []);
      setGovData(dashData || null);
    } catch (err) {
      console.error('Error fetching network GIS data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshNetwork();
  }, []);

  return (
    <RouteContext.Provider
      value={{
        nodes,
        roads,
        incidents,
        govData,
        loading,
        refreshNetwork,
        origin,
        setOrigin,
        destination,
        setDestination,
        vehicleType,
        setVehicleType,
        cargo,
        setCargo,
        weight,
        setWeight,
        monsoon,
        setMonsoon,
        peakHour,
        setPeakHour,
        routeResults,
        setRouteResults,
        selectedCandidateIndex,
        setSelectedCandidateIndex,
        routeMode,
        setRouteMode,
        activeDisruption,
        setActiveDisruption,
        disruptedRoadId,
        setDisruptedRoadId,
        disruptionReason,
        setDisruptionReason,
        twinImpact,
        setTwinImpact,
        mapFocus,
        setMapFocus,
        mapZoom,
        setMapZoom,
        highlightedCorridor,
        setHighlightedCorridor,
      }}
    >
      {children}
    </RouteContext.Provider>
  );
}

export function useRouteContext() {
  const context = useContext(RouteContext);
  if (!context) {
    throw new Error('useRouteContext must be used within a RouteProvider');
  }
  return context;
}
