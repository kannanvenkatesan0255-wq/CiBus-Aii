import React, { useState, useEffect } from 'react';
import { optimizeRoute } from '../services/predictionService';

const SOURCE_PRESETS = [
  { name: 'Guindy Central Dispatch (13.01° N, 80.20° E)', lat: 13.0067, lon: 80.2026 },
  { name: 'Tambaram Distribution Facility (12.92° N, 80.10° E)', lat: 12.9249, lon: 80.1000 },
  { name: 'Adyar Catering Hub (13.00° N, 80.26° E)', lat: 13.0012, lon: 80.2565 },
  { name: 'Koyambedu Food Complex (13.07° N, 80.19° E)', lat: 13.0694, lon: 80.1948 },
  { name: 'Chennai Central Kitchen (13.08° N, 80.27° E)', lat: 13.0827, lon: 80.2707 }
];

// Fallback demo NGOs for independent route exploration
const DEMO_NGOS = [
  { ngo_id: 'NGO_001', name: 'Annai Teresa Food Relief', latitude: 13.0067, longitude: 80.2026, allocated_meals: 120.0 },
  { ngo_id: 'NGO_002', name: 'Karunai Ullangal Trust', latitude: 13.0012, longitude: 80.2565, allocated_meals: 80.0 },
  { ngo_id: 'NGO_005', name: 'Aram Seiya Virumbu Trust', latitude: 13.0827, longitude: 80.2707, allocated_meals: 100.0 },
  { ngo_id: 'NGO_008', name: 'Pasumai Thayagam Kitchen', latitude: 12.9249, longitude: 80.1000, allocated_meals: 50.0 }
];

export default function RoutePlanningSection({ matchedNGOs, sourceLocation }) {
  const [selectedSourceIdx, setSelectedSourceIdx] = useState(0);
  const [activeNGOs, setActiveNGOs] = useState([]);
  const [routeResult, setRouteResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showMatrix, setShowMatrix] = useState(false);

  // Sync active NGOs when upstream matching produces recipients
  useEffect(() => {
    if (matchedNGOs && matchedNGOs.length > 0) {
      const formatted = matchedNGOs.map(m => ({
        ngo_id: m.ngo_id,
        name: m.ngo_name || m.name || m.ngo_id,
        latitude: m.latitude ?? 13.0067,
        longitude: m.longitude ?? 80.2026,
        allocated_meals: m.allocated_meals ?? 50.0
      }));
      setActiveNGOs(formatted);
    } else {
      setActiveNGOs(DEMO_NGOS);
    }
  }, [matchedNGOs]);

  const handleOptimizeSubmit = async (e) => {
    if (e) e.preventDefault();

    if (!activeNGOs || activeNGOs.length === 0) {
      setError('Please provide at least one recipient NGO to plan a distribution route.');
      return;
    }

    setIsLoading(true);
    setError('');
    setRouteResult(null);

    const sourcePreset = SOURCE_PRESETS[selectedSourceIdx];

    try {
      const payload = {
        source: {
          name: sourcePreset.name.split('(')[0].trim(),
          latitude: sourcePreset.lat,
          longitude: sourcePreset.lon
        },
        ngos: activeNGOs
      };

      const result = await optimizeRoute(payload);
      setRouteResult(result);
    } catch (err) {
      setError(err.message || 'Failed to optimize distribution route.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearRoute = () => {
    setRouteResult(null);
    setError('');
  };

  return (
    <section className="info-section route-planning-section" id="route-planning" style={{ marginTop: '2rem' }}>
      <div className="section-header">
        <div
          className="hero-pill"
          style={{
            background: 'rgba(168, 85, 247, 0.1)',
            borderColor: 'rgba(168, 85, 247, 0.3)',
            color: '#c084fc'
          }}
        >
          <span>🗺️</span> Logistics & Distribution Planning Module
        </div>
        <h2 className="section-title">Route Optimization & Pickup Planning</h2>
        <p>Deterministic graph routing using Haversine great-circle distances and greedy Nearest-Neighbor sequencing</p>
      </div>

      <div className="glass-card" style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h3 className="card-title" style={{ fontSize: '1.2rem' }}>
              <span>🚚</span> Dispatch Route Optimizer
            </h3>
            <p className="card-subtitle">
              Ready to sequence delivery for <strong style={{ color: '#c084fc' }}>{activeNGOs.length} recipient stops</strong>
            </p>
          </div>
          <span className="track-badge" style={{ background: 'rgba(168, 85, 247, 0.1)', color: '#c084fc', borderColor: 'rgba(168, 85, 247, 0.3)' }}>
            Demo Route Planner
          </span>
        </div>

        {error && (
          <div className="alert-error" role="alert" style={{ marginBottom: '1rem' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Source Configuration and Trigger Form */}
        <form onSubmit={handleOptimizeSubmit}>
          <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
            {/* Origin Dispatch Facility */}
            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label className="form-label" htmlFor="route-source-location">
                Starting Food Source / Dispatch Origin
              </label>
              <select
                id="route-source-location"
                className="form-control"
                value={selectedSourceIdx}
                onChange={(e) => setSelectedSourceIdx(Number(e.target.value))}
                disabled={isLoading}
              >
                {SOURCE_PRESETS.map((preset, idx) => (
                  <option key={idx} value={idx}>{preset.name}</option>
                ))}
              </select>
            </div>

            {/* Action Buttons */}
            <div className="form-group" style={{ gridColumn: 'span 2', justifyContent: 'flex-end' }}>
              <div style={{ display: 'flex', gap: '0.75rem', width: '100%' }}>
                <button
                  id="btn-optimize-route"
                  type="submit"
                  className="btn btn-primary"
                  style={{
                    background: 'linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)',
                    flex: 1
                  }}
                  disabled={isLoading || activeNGOs.length === 0}
                >
                  {isLoading ? 'Sequencing Optimal Route...' : '🚀 Optimize Delivery Route'}
                </button>
                {routeResult && (
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleClearRoute}
                  >
                    Clear Route
                  </button>
                )}
              </div>
            </div>
          </div>
        </form>

        {/* Route Optimization Results Presentation */}
        {routeResult && (
          <div className="result-active" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem', marginTop: '1rem' }}>
            {/* Summary Metrics Banner */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Route Distance</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#c084fc' }}>
                  {routeResult.summary.total_distance_km} <span style={{ fontSize: '0.85rem' }}>km</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Recipient NGO Stops</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8' }}>
                  {routeResult.summary.number_of_stops} <span style={{ fontSize: '0.85rem' }}>stops</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Meals Distributed</div>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#34d399' }}>
                  {routeResult.summary.total_allocated_meals} <span style={{ fontSize: '0.85rem' }}>meals</span>
                </div>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Starting Facility</div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f3f4f6', marginTop: '0.35rem' }}>
                  {routeResult.summary.start_location}
                </div>
              </div>
            </div>

            {/* Visual Route Flow Timeline */}
            <h4 style={{ marginBottom: '1.25rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>📍</span> Sequenced Itinerary Plan (Nearest-Neighbor)
            </h4>

            <div className="route-timeline" style={{ position: 'relative', paddingLeft: '1rem', marginBottom: '1.5rem' }}>
              {routeResult.route.map((stop, idx) => {
                const isSource = stop.type === 'source';
                return (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.25rem', position: 'relative' }}>
                    {/* Node Dot & Connector Line */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <div
                        style={{
                          width: '36px',
                          height: '36px',
                          borderRadius: '50%',
                          background: isSource
                            ? 'linear-gradient(135deg, #a855f7, #6b21a8)'
                            : 'linear-gradient(135deg, #06b6d4, #0e7490)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '0.85rem',
                          color: '#ffffff',
                          boxShadow: '0 0 12px rgba(168, 85, 247, 0.3)',
                          zIndex: 2
                        }}
                      >
                        {isSource ? '🏁' : stop.sequence}
                      </div>
                      {idx < routeResult.route.length - 1 && (
                        <div
                          style={{
                            width: '2px',
                            height: '45px',
                            background: 'rgba(255, 255, 255, 0.15)',
                            margin: '0.25rem 0'
                          }}
                        />
                      )}
                    </div>

                    {/* Waypoint Details Card */}
                    <div
                      style={{
                        flex: 1,
                        background: isSource ? 'rgba(168, 85, 247, 0.08)' : 'rgba(15, 23, 42, 0.85)',
                        border: `1px solid ${isSource ? 'rgba(168, 85, 247, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
                        borderRadius: 'var(--radius-md)',
                        padding: '0.85rem 1.15rem'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                        <div>
                          <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: isSource ? '#c084fc' : '#38bdf8', fontWeight: 700 }}>
                            {isSource ? 'Origin / Food Facility' : `Stop ${stop.sequence} • ${stop.ngo_id}`}
                          </span>
                          <h4 style={{ margin: '0.15rem 0 0.25rem 0', fontSize: '1rem', color: '#f9fafb' }}>
                            {stop.name}
                          </h4>
                        </div>

                        {!isSource && (
                          <div style={{ textAlign: 'right' }}>
                            <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>
                              📦 {stop.allocated_meals} meals drop
                            </span>
                          </div>
                        )}
                      </div>

                      <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                        <span>📍 ({stop.latitude.toFixed(4)}°, {stop.longitude.toFixed(4)}°)</span>
                        {!isSource && (
                          <span style={{ color: '#fbbf24' }}>
                            📏 +{stop.distance_from_previous_km} km from previous waypoint
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Collapsible Distance Matrix Section */}
            <div style={{ marginTop: '1rem' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: '0.82rem', padding: '0.4rem 0.8rem' }}
                onClick={() => setShowMatrix(!showMatrix)}
              >
                {showMatrix ? '▲ Hide Pairwise Distance Matrix' : '▼ View Pairwise Distance Matrix Details'}
              </button>

              {showMatrix && routeResult.distance_matrix && (
                <div style={{ marginTop: '0.75rem', overflowX: 'auto', background: 'rgba(0, 0, 0, 0.25)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
                  <table style={{ width: '100%', fontSize: '0.75rem', borderCollapse: 'collapse', textAlign: 'center' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
                        <th style={{ textAlign: 'left', padding: '0.4rem' }}>Node</th>
                        {routeResult.location_names.map((name, i) => (
                          <th key={i} style={{ padding: '0.4rem' }}>{name.slice(0, 12)}...</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {routeResult.distance_matrix.map((row, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                          <td style={{ textAlign: 'left', padding: '0.4rem', fontWeight: 600, color: '#c084fc' }}>
                            {routeResult.location_names[i].slice(0, 15)}
                          </td>
                          {row.map((dist, j) => (
                            <td key={j} style={{ padding: '0.4rem', color: i === j ? 'var(--text-muted)' : '#f3f4f6' }}>
                              {dist.toFixed(1)} km
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Heuristic Disclaimer */}
            <div
              style={{
                marginTop: '1.25rem',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.2)',
                fontSize: '0.78rem',
                color: '#f59e0b'
              }}
            >
              ℹ️ <strong>Heuristic Estimation Note:</strong> Route distance is estimated using straight-line geographic coordinates (Haversine formula) and a nearest-neighbor heuristic. This academic prototype does not account for road congestion, one-way road networks, or live traffic conditions.
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
