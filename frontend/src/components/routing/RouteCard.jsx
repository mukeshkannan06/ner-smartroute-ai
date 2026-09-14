import React from 'react';
import { Clock, ShieldAlert, Navigation, IndianRupee, Award, ArrowRight } from 'lucide-react';

export function RouteCard({ candidate, index, isSelected, onClick, isRecommended }) {
  const riskPct = Math.round((candidate.risk_probability || 0) * 100);
  const isLowRisk = riskPct < 25;
  const isMedRisk = riskPct >= 25 && riskPct < 50;

  return (
    <div
      onClick={onClick}
      style={{
        padding: '16px 20px',
        borderRadius: 'var(--radius-md)',
        backgroundColor: isSelected ? '#FFFFFF' : 'var(--bg-card-subtle)',
        border: isSelected
          ? (isRecommended ? '2px solid var(--emerald)' : '2px solid var(--clay-600)')
          : '1px solid var(--border-color)',
        cursor: 'pointer',
        boxShadow: isSelected ? 'var(--shadow-md)' : 'none',
        transition: 'all 0.2s ease',
        marginBottom: '12px',
        position: 'relative',
      }}
    >
      {/* Header Tag */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isRecommended ? (
            <span className="badge-pill badge-emerald">
              <Award size={13} /> Recommended #1
            </span>
          ) : (
            <span className="badge-pill badge-forest">
              Option #{index + 1}
            </span>
          )}
          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            Score: {Math.round(candidate.overall_score || 0)}/100
          </span>
        </div>

        <span className={`badge-pill ${isLowRisk ? 'badge-emerald' : (isMedRisk ? 'badge-amber' : 'badge-crimson')}`}>
          {riskPct}% Risk
        </span>
      </div>

      {/* Path */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '6px',
        fontSize: '13.5px',
        fontWeight: 600,
        color: 'var(--forest-900)',
        marginBottom: '12px',
      }}>
        {(candidate.path || []).map((city, idx) => (
          <React.Fragment key={idx}>
            <span>{city}</span>
            {idx < (candidate.path.length - 1) && <ArrowRight size={13} color="var(--sand-600)" />}
          </React.Fragment>
        ))}
      </div>

      {/* Key Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '8px',
        paddingTop: '10px',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '12px',
      }}>
        <div>
          <div style={{ color: 'var(--text-light)', fontSize: '10.5px' }}>DISTANCE</div>
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--forest-900)' }}>
            {candidate.total_distance_km} km
          </div>
        </div>
        <div>
          <div style={{ color: 'var(--text-light)', fontSize: '10.5px' }}>ETA</div>
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--forest-900)' }}>
            {candidate.eta_hours} hrs
          </div>
        </div>
        <div>
          <div style={{ color: 'var(--text-light)', fontSize: '10.5px' }}>ACCESS</div>
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--forest-900)' }}>
            {Math.round(candidate.accessibility_score || 0)}/100
          </div>
        </div>
        <div>
          <div style={{ color: 'var(--text-light)', fontSize: '10.5px' }}>EST. COST</div>
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--forest-900)' }}>
            ₹{Math.round(candidate.estimated_cost_inr || 0).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
