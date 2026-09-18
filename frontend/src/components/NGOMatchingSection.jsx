import React, { useState } from 'react';
import { matchNGOs } from '../services/predictionService';

const LOCATION_PRESETS = [
  { label: 'Tambaram / Chromepet (12.92° N, 80.10° E)', lat: 12.9249, lon: 80.1000 },
  { label: 'Guindy / Saidapet (13.00° N, 80.20° E)', lat: 13.0067, lon: 80.2025 },
  { label: 'Adyar / Thiruvanmiyur (13.00° N, 80.25° E)', lat: 13.0012, lon: 80.2565 },
  { label: 'Velachery / Perungudi (12.97° N, 80.22° E)', lat: 12.9759, lon: 80.2212 },
  { label: 'Koyambedu / Vadapalani (13.06° N, 80.19° E)', lat: 13.0694, lon: 80.1948 },
  { label: 'Location Coordinates Unavailable (General Match)', lat: null, lon: null }
];

export default function NGOMatchingSection({ predictedSurplus, onMatchesUpdated }) {
  const [foodType, setFoodType] = useState('Both');
  const [selectedLocationIdx, setSelectedLocationIdx] = useState(0);
  const [maxMatches, setMaxMatches] = useState(4);
  const [matchingResult, setMatchingResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const surplusValue = predictedSurplus !== null && predictedSurplus !== undefined
    ? Number(predictedSurplus)
    : 0;

  const handleMatchSubmit = async (e) => {
    e.preventDefault();
    if (surplusValue <= 0) {
      setError('A valid positive surplus forecast is required to match recipient NGOs.');
      return;
    }

    setIsLoading(true);
    setError('');
    setMatchingResult(null);

    const preset = LOCATION_PRESETS[selectedLocationIdx];

    try {
      const result = await matchNGOs({
        predicted_surplus_meals: surplusValue,
        food_type: foodType,
        source_latitude: preset.lat,
        source_longitude: preset.lon,
        max_matches: maxMatches
      });
      setMatchingResult(result);
      if (onMatchesUpdated) {
        onMatchesUpdated(result.matches || []);
      }
    } catch (err) {
      setError(err.message || 'Failed to match candidate recipient NGOs.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearResults = () => {
    setMatchingResult(null);
    setError('');
    if (onMatchesUpdated) {
      onMatchesUpdated([]);
    }
  };


  return (
    <section className="info-section ngo-matching-section" id="ngo-matching">
      <div className="section-header">
        <div className="hero-pill" style={{ background: 'rgba(6, 182, 212, 0.1)', borderColor: 'rgba(6, 182, 212, 0.3)', color: '#22d3ee' }}>
          <span>🤝</span> Food Redistribution Planning Module
        </div>
        <h2 className="section-title">Recipient NGO Matching & Allocation</h2>
        <p>Rule-based capacity distribution connecting forecasted excess meals with nearby relief centers</p>
      </div>

      <div className="glass-card" style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h3 className="card-title" style={{ fontSize: '1.2rem' }}>
              <span>📦</span> Surplus Redistribution Parameters
            </h3>
            <p className="card-subtitle">
              Configured for surplus forecast: <strong style={{ color: '#34d399' }}>{surplusValue.toFixed(1)} meals</strong>
            </p>
          </div>
          <span className="track-badge" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
            Demo / Synthetic NGO Dataset
          </span>
        </div>

        {error && (
          <div className="alert-error" role="alert">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleMatchSubmit}>
          <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
            {/* Food Type */}
            <div className="form-group">
              <label className="form-label" htmlFor="ngo-food-type">
                Food Dietary Classification
              </label>
              <select
                id="ngo-food-type"
                className="form-control"
                value={foodType}
                onChange={(e) => setFoodType(e.target.value)}
                disabled={isLoading}
              >
                <option value="Both">Both (Veg & Non-Veg)</option>
                <option value="Vegetarian">Vegetarian Only</option>
                <option value="Non-Vegetarian">Non-Vegetarian Only</option>
              </select>
            </div>

            {/* Donor Location Preset */}
            <div className="form-group">
              <label className="form-label" htmlFor="ngo-location">
                Donor Facility Area / Coordinates
              </label>
              <select
                id="ngo-location"
                className="form-control"
                value={selectedLocationIdx}
                onChange={(e) => setSelectedLocationIdx(Number(e.target.value))}
                disabled={isLoading}
              >
                {LOCATION_PRESETS.map((loc, idx) => (
                  <option key={idx} value={idx}>{loc.label}</option>
                ))}
              </select>
            </div>

            {/* Max NGO Allocations */}
            <div className="form-group">
              <label className="form-label" htmlFor="ngo-max-matches">
                Max Recipient Organizations
              </label>
              <select
                id="ngo-max-matches"
                className="form-control"
                value={maxMatches}
                onChange={(e) => setMaxMatches(Number(e.target.value))}
                disabled={isLoading}
              >
                <option value="2">Top 2 Organizations</option>
                <option value="3">Top 3 Organizations</option>
                <option value="4">Top 4 Organizations</option>
                <option value="5">Top 5 Organizations</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="form-group" style={{ justifyContent: 'flex-end' }}>
              <label className="form-label" style={{ opacity: 0 }}>Action</label>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  id="btn-match-ngos"
                  type="submit"
                  className="btn btn-primary"
                  style={{ background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)', flex: 1 }}
                  disabled={isLoading || surplusValue <= 0}
                >
                  {isLoading ? 'Finding NGOs...' : '⚡ Match Candidate NGOs'}
                </button>
                {matchingResult && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleClearResults}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>
        </form>

        {/* Matching Results View */}
        {matchingResult && (
          <div className="result-active" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem', marginTop: '1rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Forecasted Surplus</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#34d399' }}>{matchingResult.predicted_surplus_meals} <span style={{ fontSize: '0.85rem' }}>meals</span></div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Allocated</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#22d3ee' }}>{matchingResult.total_allocated_meals} <span style={{ fontSize: '0.85rem' }}>meals</span></div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Unallocated Balance</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: matchingResult.unallocated_meals > 0 ? '#f59e0b' : '#9ca3af' }}>{matchingResult.unallocated_meals} <span style={{ fontSize: '0.85rem' }}>meals</span></div>
              </div>
            </div>

            <h4 style={{ marginBottom: '1rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🏛️</span> Recommended Recipient Centers ({matchingResult.matches.length})
            </h4>

            {matchingResult.matches.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                No active NGOs matched the specified dietary and capacity criteria.
              </p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
                {matchingResult.matches.map((match) => (
                  <div key={match.ngo_id} className="step-card" style={{ background: 'rgba(15, 23, 42, 0.85)', borderColor: 'rgba(6, 182, 212, 0.25)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <span className="step-badge" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>{match.ngo_id}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                        {Math.round(match.match_score * 100)}% Match
                      </span>
                    </div>

                    <h4 style={{ fontSize: '1.05rem', marginBottom: '0.2rem' }}>{match.ngo_name}</h4>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                      📍 {match.area} • {match.food_type} Meals • 👥 Serves ~{match.people_served} people
                    </p>

                    <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', marginBottom: '0.75rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                        <span>Recommended Allocation:</span>
                        <strong style={{ color: '#22d3ee' }}>{match.allocated_meals} meals</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        <span>Shelter Capacity:</span>
                        <span>{match.capacity_meals} meals</span>
                      </div>
                      <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', marginTop: '0.4rem', overflow: 'hidden' }}>
                        <div
                          style={{
                            width: `${Math.min(100, (match.allocated_meals / match.capacity_meals) * 100)}%`,
                            height: '100%',
                            background: 'linear-gradient(90deg, #06b6d4, #10b981)',
                            borderRadius: '3px'
                          }}
                        />
                      </div>
                    </div>

                    <p style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                      <strong>Distance:</strong> {match.distance_km !== null ? `${match.distance_km} km (approx.)` : 'Distance unavailable'}
                    </p>
                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      💡 {match.reason}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {matchingResult.matches.length > 0 && (
              <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                <a
                  href="#route-planning"
                  className="btn btn-primary"
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: 'linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)',
                    textDecoration: 'none'
                  }}
                >
                  🗺️ Proceed to Route Optimization & Pickup Planning ↓
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </section>

  );
}
