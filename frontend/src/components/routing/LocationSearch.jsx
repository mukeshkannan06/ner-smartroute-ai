import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Search, Loader2 } from 'lucide-react';
import { useRouteContext } from '../../context/RouteContext';
import { useDebounce } from '../../hooks/useDebounce';
import { searchGeocoding } from '../../services/api';

export function LocationSearch({ label, value, onChange, placeholder }) {
  const { nodes } = useRouteContext();
  const [query, setQuery] = useState(value);
  const [open, setOpen] = useState(false);
  const [remoteResults, setRemoteResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const dropdownRef = useRef(null);
  const cacheRef = useRef(new Map());

  const debouncedQuery = useDebounce(query, 350);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // India-wide geocoding search (debounced + cached), so the planner isn't
  // limited to the 11 built-in NER demo cities.
  useEffect(() => {
    const q = (debouncedQuery || '').trim();
    if (q.length < 2) {
      setRemoteResults([]);
      return;
    }

    if (cacheRef.current.has(q.toLowerCase())) {
      setRemoteResults(cacheRef.current.get(q.toLowerCase()));
      return;
    }

    let cancelled = false;
    setSearching(true);
    searchGeocoding(q)
      .then((results) => {
        if (cancelled) return;
        const list = Array.isArray(results) ? results : [];
        cacheRef.current.set(q.toLowerCase(), list);
        setRemoteResults(list);
      })
      .catch(() => {
        if (!cancelled) setRemoteResults([]);
      })
      .finally(() => {
        if (!cancelled) setSearching(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  const cityNames = Object.keys(nodes);
  const localMatches = cityNames.filter((c) =>
    c.toLowerCase().includes((query || '').toLowerCase())
  );

  // Merge local NER quick-picks with India-wide geocoding results, de-duped by name.
  const seen = new Set(localMatches.map((c) => c.toLowerCase()));
  const remoteMatches = remoteResults.filter((r) => !seen.has((r.name || '').toLowerCase()));

  const handleSelect = (name) => {
    setQuery(name);
    onChange(name);
    setOpen(false);
  };

  return (
    <div className="form-group" style={{ position: 'relative' }} ref={dropdownRef}>
      <label className="form-label">{label}</label>
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          className="form-input"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            onChange(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder={placeholder || 'Enter any Indian city...'}
          style={{ paddingLeft: '34px', paddingRight: searching ? '30px' : undefined }}
        />
        <MapPin
          size={16}
          color="var(--clay-600)"
          style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }}
        />
        {searching && (
          <Loader2
            size={14}
            className="animate-spin"
            style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)' }}
          />
        )}
      </div>

      {open && (localMatches.length > 0 || remoteMatches.length > 0) && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          boxShadow: 'var(--shadow-lg)',
          maxHeight: '220px',
          overflowY: 'auto',
          zIndex: 100,
          marginTop: '4px',
        }}>
          {localMatches.map((city) => (
            <div
              key={`local-${city}`}
              onClick={() => handleSelect(city)}
              style={{
                padding: '8px 12px',
                fontSize: '13.5px',
                cursor: 'pointer',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--sand-100)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FFFFFF'}
            >
              <span style={{ fontWeight: 600, color: 'var(--forest-900)' }}>{city}</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {nodes[city]?.population ? `${Math.round(nodes[city].population / 1000)}k pop` : 'NER hub'}
              </span>
            </div>
          ))}
          {remoteMatches.map((r, idx) => (
            <div
              key={`remote-${r.name}-${idx}`}
              onClick={() => handleSelect(r.name)}
              style={{
                padding: '8px 12px',
                fontSize: '13.5px',
                cursor: 'pointer',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--sand-100)'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FFFFFF'}
            >
              <Search size={12} color="var(--text-muted)" />
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 600, color: 'var(--forest-900)' }}>{r.name}</span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{r.display_name}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
