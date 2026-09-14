import React, { useState } from 'react';
import { ArrowRightLeft, Sparkles, Loader2, Truck } from 'lucide-react';
import { LocationSearch } from './LocationSearch';
import { RouteResults } from './RouteResults';
import { useRouteContext } from '../../context/RouteContext';
import { useLanguage } from '../../context/LanguageContext';
import { calculateBestRoutes } from '../../services/routingService';

export function RoutePlanner() {
  const {
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
    routeMode,
    setRouteMode,
    setRouteResults,
  } = useRouteContext();

  const { t } = useLanguage();
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState(null);

  const handleSwap = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handleCalculate = async (e) => {
    e?.preventDefault();
    if (!origin || !destination) {
      setError('Please specify both origin and destination');
      return;
    }
    if (origin.toLowerCase() === destination.toLowerCase()) {
      setError('Origin and destination cannot be identical');
      return;
    }

    try {
      setCalculating(true);
      setError(null);
      const res = await calculateBestRoutes({
        origin,
        destination,
        vehicleType,
        weight,
        cargo,
        monsoon,
        peakHour,
        mode: routeMode,
      });
      setRouteResults(res);
    } catch (err) {
      setError(err.message || 'Routing calculation failed');
      setRouteResults(null);
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="glass-panel">
      <div style={{ marginBottom: '18px' }}>
        <h2 style={{ fontSize: '18px', color: 'var(--forest-900)' }}>
          {t('planner.title')}
        </h2>
        <p style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>
          {t('planner.subtitle')}
        </p>
      </div>

      {error && (
        <div style={{
          padding: '10px 14px',
          marginBottom: '16px',
          backgroundColor: 'var(--crimson-light)',
          color: 'var(--crimson)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '12.5px',
          fontWeight: 500,
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleCalculate}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '10px', alignItems: 'center' }}>
          <LocationSearch
            label={t('planner.origin')}
            value={origin}
            onChange={setOrigin}
            placeholder="Origin (e.g. Guwahati)"
          />
          <button
            type="button"
            onClick={handleSwap}
            title="Swap Origin and Destination"
            style={{
              marginTop: '12px',
              padding: '8px',
              borderRadius: '50%',
              backgroundColor: 'var(--sand-200)',
              color: 'var(--forest-900)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ArrowRightLeft size={16} />
          </button>
          <LocationSearch
            label={t('planner.destination')}
            value={destination}
            onChange={setDestination}
            placeholder="Destination (e.g. Imphal)"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr', gap: '12px', marginTop: '4px' }}>
          <div className="form-group">
            <label className="form-label">{t('planner.vehicle_type')}</label>
            <select
              className="form-select"
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
            >
              <option value="truck">Heavy Commercial Truck (10–20T)</option>
              <option value="mini_truck">Medium Mini Truck (4–8T)</option>
              <option value="van">Logistics Cargo Van (2–4T)</option>
              <option value="car">Light Transport Utility (1–2T)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">{t('planner.cargo')}</label>
            <input
              type="text"
              className="form-input"
              value={cargo}
              onChange={(e) => setCargo(e.target.value)}
              placeholder="e.g. Vegetables, Medicine"
            />
          </div>

          <div className="form-group">
            <label className="form-label">{t('planner.weight')}</label>
            <input
              type="number"
              className="form-input"
              value={weight}
              min="0.5"
              step="0.5"
              max="40"
              onChange={(e) => setWeight(e.target.value)}
            />
          </div>
        </div>

        <div style={{ marginTop: '4px' }}>
          <label className="form-label">Route Priority</label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '6px' }}>
            {[
              { id: 'safest', label: '🛡️ Safest' },
              { id: 'fastest', label: '⚡ Fastest' },
              { id: 'balanced', label: '⚖️ Balanced' },
              { id: 'lowest_cost', label: '₹ Lowest Cost' },
              { id: 'emergency', label: '🚨 Emergency' },
            ].map((opt) => (
              <button
                type="button"
                key={opt.id}
                onClick={() => setRouteMode(opt.id)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '12.5px',
                  fontWeight: 600,
                  border: routeMode === opt.id ? '2px solid var(--forest-700)' : '1px solid var(--border-color)',
                  backgroundColor: routeMode === opt.id ? 'var(--forest-700)' : '#FFFFFF',
                  color: routeMode === opt.id ? '#FFFFFF' : 'var(--forest-900)',
                  cursor: 'pointer',
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Environmental conditions checkboxes */}
        <div style={{ display: 'flex', gap: '24px', margin: '14px 0 18px', fontSize: '13px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={monsoon}
              onChange={(e) => setMonsoon(e.target.checked)}
              style={{ accentColor: 'var(--forest-700)', width: '16px', height: '16px' }}
            />
            <span>{t('planner.monsoon')}</span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={peakHour}
              onChange={(e) => setPeakHour(e.target.checked)}
              style={{ accentColor: 'var(--forest-700)', width: '16px', height: '16px' }}
            />
            <span>{t('planner.peak_hour')}</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={calculating}
          className="btn-primary"
          style={{ width: '100%' }}
        >
          {calculating ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>{t('planner.calculating')}</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>{t('planner.find_route')}</span>
            </>
          )}
        </button>
      </form>

      <RouteResults />
    </div>
  );
}
