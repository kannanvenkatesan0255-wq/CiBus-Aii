import React, { useState, useEffect } from 'react';
import { getDashboardSummary, getRecentActivities } from '../services/predictionService';

export default function ImpactDashboard() {
  const [summaryData, setSummaryData] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [recentActivities, setRecentActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError('');

    try {
      const [summaryRes, recentRes] = await Promise.all([
        getDashboardSummary(),
        getRecentActivities(8)
      ]);

      if (summaryRes && summaryRes.summary) {
        setSummaryData(summaryRes.summary);
        setModelMetrics(summaryRes.model_performance);
      }
      if (Array.isArray(recentRes)) {
        setRecentActivities(recentRes);
      }
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message || 'Failed to load dashboard operational analytics.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

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
            onClick={fetchDashboardData}
            disabled={isLoading}
          >
            <span>🔄</span> {isLoading ? 'Refreshing...' : 'Refresh Metrics'}
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
            <h4 style={{ fontSize: '1.05rem', color: '#f3f4f6', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🌐</span> Redistribution Impact Summary
            </h4>

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

        {/* ML Model Performance Panel */}
        {modelMetrics && (
          <div style={{ marginBottom: '2rem', background: 'rgba(15, 23, 42, 0.7)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
              <div>
                <h4 style={{ fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span>🧠</span> ML Model Performance
                </h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: '0.2rem 0 0 0' }}>
                  Model: <strong style={{ color: '#38bdf8' }}>{modelMetrics.model_name}</strong> • {modelMetrics.evaluation_dataset}
                </p>
              </div>

              <span style={{ fontSize: '0.72rem', padding: '0.2rem 0.6rem', borderRadius: '4px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.3)', fontWeight: 600 }}>
                Held-Out Test Metrics
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#93c5fd' }}>MAE (Mean Absolute Error)</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff' }}>{modelMetrics.mae}</span>
                </div>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.3rem 0 0 0' }}>
                  Average absolute deviation between predicted and actual surplus meals.
                </p>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#93c5fd' }}>RMSE (Root Mean Squared Error)</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff' }}>{modelMetrics.rmse}</span>
                </div>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.3rem 0 0 0' }}>
                  Square-rooted mean squared error, penalizing larger deviations.
                </p>
              </div>

              <div style={{ background: 'rgba(255, 255, 255, 0.04)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399' }}>R² (Explained Variance)</span>
                  <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399' }}>{modelMetrics.r2}</span>
                </div>
                <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: '0.3rem 0 0 0' }}>
                  Proportion of target variance explained relative to baseline.
                </p>
              </div>
            </div>

            <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: '0.75rem 0 0 0', fontStyle: 'italic' }}>
              💡 {modelMetrics.note}
            </p>
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
          ℹ️ <strong>Demonstration Dashboard Note:</strong> Operational metrics reflect planned surplus redistribution workflows recorded within the application session. Haversine distance represents straight-line geographic estimation. Verified physical food delivery requires on-ground logistics confirmation.
        </div>
      </div>
    </section>
  );
}
