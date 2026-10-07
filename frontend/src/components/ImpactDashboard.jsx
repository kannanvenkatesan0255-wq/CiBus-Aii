import React, { useState, useEffect } from 'react';
import { getRecentActivities, clearRecentActivities } from '../services/predictionService';

/**
 * Generates realistic randomized simulated operational metrics
 * for prototype demonstration sessions.
 * Range specifications:
 * - Predicted Surplus: ~500–5000 meals
 * - Planned Allocation: ~60–100% of predicted surplus
 * - Allocation Rate: ~70–100%
 * - Matched Partner NGOs: ~5–30 centers
 * - Estimated Route Distance: ~5–80 km
 * - Redistribution Plans: ~1–25 itineraries
 */
function generateRandomDemoMetrics() {
  const surplus = +(500 + Math.random() * 4500).toFixed(2);
  const allocationRatio = 0.60 + Math.random() * 0.40;
  const allocated = +(surplus * allocationRatio).toFixed(2);
  const ratePct = Math.min(100, Math.round((allocated / surplus) * 100));
  const ngos = Math.floor(5 + Math.random() * 26);
  const distance = +(5 + Math.random() * 75).toFixed(2);
  const plans = Math.floor(1 + Math.random() * 25);

  return {
    total_predicted_surplus_meals: surplus,
    total_allocated_meals: allocated,
    allocation_rate_pct: ratePct,
    total_matched_ngos: ngos,
    total_route_distance_km: distance,
    total_activities: plans,
    is_demo: true,
    is_reset: false
  };
}

function generateRandomDemoActivities() {
  const count = Math.random() < 0.5 ? 5 : 6;
  const facilities = [
    'Guindy Central Dispatch Facility',
    'Chennai Central Kitchen',
    'Adyar Catering & Banquet Hub',
    'T. Nagar Community Distribution Center',
    'Velachery Regional Food Hub',
    'Anna Nagar Prepared Food Kitchen',
    'OMR Corporate Cafeteria Hub',
    'Tambaram Relief Logistics Hub'
  ];

  // Randomize facility selection
  const shuffled = [...facilities].sort(() => 0.5 - Math.random());
  const now = Date.now();
  const activities = [];

  for (let i = 0; i < count; i++) {
    const minutesAgo = 25 + i * 45 + Math.floor(Math.random() * 20);
    const timestamp = new Date(now - minutesAgo * 60 * 1000).toISOString();
    const surplus = Math.floor(220 + Math.random() * 780);
    const allocationRate = 0.75 + Math.random() * 0.25;
    const allocated = Math.min(surplus, Math.floor(surplus * allocationRate));
    const ngos = Math.floor(2 + Math.random() * 4);
    const distance = +(5.0 + Math.random() * 25.0).toFixed(1);
    const status = i === 0 ? 'planned' : (Math.random() > 0.4 ? 'completed' : 'planned');

    activities.push({
      activity_id: `DEMO_ACT_${now}_${i + 1}`,
      timestamp,
      source_name: shuffled[i % shuffled.length],
      predicted_surplus_meals: surplus,
      allocated_meals: allocated,
      matched_ngo_count: ngos,
      route_stop_count: ngos,
      route_distance_km: distance,
      status
    });
  }

  return activities;
}

const ZERO_METRICS = {
  total_predicted_surplus_meals: 0,
  total_allocated_meals: 0,
  allocation_rate_pct: 0,
  total_matched_ngos: 0,
  total_route_distance_km: 0,
  total_activities: 0,
  is_demo: false,
  is_reset: true
};

/**
 * Note on ML Model Performance:
 * Per user specification, the ML Model Performance panel (MAE, RMSE, R²) is hidden from the
 * user-facing dashboard. The trained RandomForestRegressor model and its evaluation metrics remain
 * active and operational in the backend services (/api/model-info, /api/predict).
 */
export default function ImpactDashboard({ loggedActivity = null }) {
  // Initialize with fresh random demo metrics on every page load/reload
  const [summaryData, setSummaryData] = useState(() => generateRandomDemoMetrics());
  // Initialize with 5 to 6 realistic random demo activities on page load/reload
  const [recentActivities, setRecentActivities] = useState(() => generateRandomDemoActivities());
  const [lastRefreshed, setLastRefreshed] = useState(() => new Date().toLocaleTimeString());
  const [error, setError] = useState('');

  // Update metrics when actual application activities are logged
  useEffect(() => {
    if (loggedActivity && loggedActivity.summary) {
      setSummaryData(prev => {
        const current = prev || ZERO_METRICS;
        const newSurplus = +(Number(current.total_predicted_surplus_meals) + Number(loggedActivity.summary.total_allocated_meals || 0)).toFixed(2);
        const newAllocated = +(Number(current.total_allocated_meals) + Number(loggedActivity.summary.total_allocated_meals || 0)).toFixed(2);
        const newRate = newSurplus > 0 ? Math.min(100, Math.round((newAllocated / newSurplus) * 100)) : 100;

        return {
          total_predicted_surplus_meals: newSurplus,
          total_allocated_meals: newAllocated,
          allocation_rate_pct: newRate,
          total_matched_ngos: Number(current.total_matched_ngos) + Number(loggedActivity.summary.number_of_stops || 1),
          total_route_distance_km: +(Number(current.total_route_distance_km) + Number(loggedActivity.summary.total_distance_km || 0)).toFixed(2),
          total_activities: Number(current.total_activities) + 1,
          is_demo: false,
          is_reset: false
        };
      });

      // Add to recent activity list
      const newEntry = {
        activity_id: `ACT_${Date.now()}`,
        timestamp: new Date().toISOString(),
        source_name: loggedActivity.summary.start_location || 'Central Dispatch',
        predicted_surplus_meals: loggedActivity.summary.total_allocated_meals,
        allocated_meals: loggedActivity.summary.total_allocated_meals,
        matched_ngo_count: loggedActivity.summary.number_of_stops,
        route_stop_count: loggedActivity.summary.number_of_stops,
        route_distance_km: loggedActivity.summary.total_distance_km,
        status: 'planned'
      };

      setRecentActivities(prev => [newEntry, ...prev.slice(0, 6)]);
      setLastRefreshed(new Date().toLocaleTimeString());
    }
  }, [loggedActivity]);

  /**
   * Reset operational dashboard metrics to 0 upon clicking Refresh Metrics
   * and clears recent planned activities. Does NOT generate new random values immediately.
   */
  const handleRefreshClick = async () => {
    setSummaryData(ZERO_METRICS);
    setRecentActivities([]);
    setLastRefreshed(new Date().toLocaleTimeString());
    setError('');
    try {
      await clearRecentActivities();
    } catch {
      // Fallback silently if offline
    }
  };

  return (
    <section className="info-section impact-dashboard-section" id="impact-dashboard">
      <div className="section-header" style={{ marginBottom: '1.5rem' }}>
        <div
          className="hero-pill"
          style={{
            background: 'rgba(16, 185, 129, 0.1)',
            borderColor: 'rgba(16, 185, 129, 0.3)',
            color: '#34d399'
          }}
        >
          <span>📊</span> Operational Intelligence & Analytics
        </div>
        <h2 className="section-title">CIBUS-AI Impact Dashboard</h2>
        <p>Monitor predicted surplus, planned redistribution, NGO matching and route activity</p>
      </div>

      <div className="glass-card" style={{ maxWidth: '1100px', margin: '0 auto' }}>
        {/* Dashboard Control Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>📈</span> Operations & Model Telemetry
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0.2rem 0 0 0' }}>
              {lastRefreshed ? `Last updated: ${lastRefreshed}` : 'Connecting to analytics store...'}
            </p>
          </div>

          <button
            id="btn-refresh-dashboard"
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            onClick={handleRefreshClick}
          >
            <span>🔄</span> Refresh Metrics
          </button>
        </div>

        {error && (
          <div className="alert-error" role="alert" style={{ marginBottom: '1.5rem' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Aggregate Operational Impact Cards */}
        {summaryData && (
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
              <h4 style={{ fontSize: '1.05rem', color: '#f3f4f6', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>🌐</span> Redistribution Impact Summary
              </h4>
              <span
                className="track-badge"
                style={{
                  fontSize: '0.7rem',
                  padding: '2px 8px',
                  background: summaryData.is_reset ? 'rgba(239, 68, 68, 0.15)' : 'rgba(6, 182, 212, 0.15)',
                  color: summaryData.is_reset ? '#f87171' : '#38bdf8',
                  borderColor: summaryData.is_reset ? 'rgba(239, 68, 68, 0.3)' : 'rgba(6, 182, 212, 0.3)'
                }}
              >
                {summaryData.is_reset ? 'Metrics Reset (0)' : 'Simulated Operational Metrics'}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '1rem' }}>
              {/* Card 1: Total Surplus Predicted */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Predicted Surplus</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#34d399', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.total_predicted_surplus_meals} <span style={{ fontSize: '0.85rem' }}>meals</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>ML Forecast Total</div>
              </div>

              {/* Card 2: Planned Allocation */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Planned Allocation</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#22d3ee', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.total_allocated_meals} <span style={{ fontSize: '0.85rem' }}>meals</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Shelter Target Volume</div>
              </div>

              {/* Card 3: Allocation Rate */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Allocation Rate</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#38bdf8', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.allocation_rate_pct}%
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Allocated / Surplus</div>
              </div>

              {/* Card 4: Matched NGOs */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Matched Partner NGOs</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#f59e0b', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.total_matched_ngos}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Recipient Centers</div>
              </div>

              {/* Card 5: Route Distance */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Est. Route Distance</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#c084fc', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.total_route_distance_km} <span style={{ fontSize: '0.85rem' }}>km</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Haversine Transit Sum</div>
              </div>

              {/* Card 6: Total Activities */}
              <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1.1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Redistribution Plans</div>
                <div style={{ fontSize: '1.65rem', fontWeight: 800, color: '#f43f5e', margin: '0.3rem 0 0.1rem 0' }}>
                  {summaryData.total_activities}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Recorded Itineraries</div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Activity Table */}
        <div>
          <h4 style={{ fontSize: '1.05rem', color: '#f3f4f6', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🕒</span> Recent Planned Redistribution Activity
          </h4>

          {recentActivities.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-subtle)' }}>
              <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                No redistribution activity recorded yet. Run a prediction and route optimization to log activities.
              </p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto', background: 'rgba(0, 0, 0, 0.2)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>Date & Time</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Source Facility</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Predicted Surplus</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Planned Allocation</th>
                    <th style={{ padding: '0.75rem 1rem' }}>NGOs</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Est. Distance</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivities.map((act) => (
                    <tr key={act.activity_id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '0.75rem 1rem', color: '#cbd5e1' }}>
                        {act.timestamp ? new Date(act.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#f3f4f6' }}>
                        {act.source_name}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: '#34d399', fontWeight: 700 }}>
                        {act.predicted_surplus_meals} meals
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: '#22d3ee', fontWeight: 700 }}>
                        {act.allocated_meals} meals
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: '#f59e0b' }}>
                        {act.matched_ngo_count} NGOs ({act.route_stop_count} stops)
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: '#c084fc' }}>
                        {act.route_distance_km} km
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ fontSize: '0.72rem', textTransform: 'capitalize', padding: '0.2rem 0.55rem', borderRadius: '4px', background: act.status === 'completed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(59, 130, 246, 0.15)', color: act.status === 'completed' ? '#34d399' : '#60a5fa', fontWeight: 700 }}>
                          {act.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Prototype Disclaimer */}
        <div
          style={{
            marginTop: '1.5rem',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.2)',
            fontSize: '0.78rem',
            color: '#f59e0b'
          }}
        >
          ℹ️ <strong>Demonstration Dashboard Note:</strong> Operational metrics reflect simulated demo values on session initialization, and can track planned redistribution workflows recorded within the application session. Haversine distance represents straight-line geographic estimation. Verified physical food delivery requires on-ground logistics confirmation.
        </div>
      </div>
    </section>
  );
}
