import React from 'react';
import { RouteCard } from './RouteCard';
import { useRouteContext } from '../../context/RouteContext';
import { useLanguage } from '../../context/LanguageContext';

export function RouteResults() {
  const { routeResults, selectedCandidateIndex, setSelectedCandidateIndex } = useRouteContext();
  const { t } = useLanguage();

  if (!routeResults) {
    return (
      <div style={{
        padding: '32px 20px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        backgroundColor: 'var(--bg-card-subtle)',
        borderRadius: 'var(--radius-md)',
        border: '1px dashed var(--border-color)',
      }}>
        <p style={{ fontSize: '13.5px' }}>
          Select origin, destination, and payload details to calculate real multi-factor routes across NER.
        </p>
      </div>
    );
  }

  const candidates = routeResults.candidates || [];

  return (
    <div style={{ marginTop: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h3 style={{ fontSize: '15px', color: 'var(--forest-900)' }}>
          Candidate Routes ({candidates.length} Found)
        </h3>
        <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
          Click an option to highlight on map
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        {candidates.map((candidate, idx) => (
          <RouteCard
            key={idx}
            candidate={candidate}
            index={idx}
            isSelected={idx === selectedCandidateIndex}
            isRecommended={idx === 0}
            onClick={() => setSelectedCandidateIndex(idx)}
          />
        ))}
      </div>
    </div>
  );
}
