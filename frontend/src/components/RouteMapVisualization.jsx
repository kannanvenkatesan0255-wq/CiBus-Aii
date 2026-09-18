import React, { useState } from 'react';

/**
 * RouteMapVisualization - SVG-based geographic coordinate & route planner visualization.
 * 
 * Features:
 * - Deterministic coordinate normalization (bounds mapping + padding).
 * - Zero external map dependencies (no Google Maps API, no Leaflet tiles, no GPS tracking).
 * - Interactive node tooltips and path segment distance labels.
 * - Academic heuristic disclaimer banner.
 */
export default function RouteMapVisualization({ route = [], source = null }) {
  const [activeStopIdx, setActiveStopIdx] = useState(null);

  if (!route || route.length === 0) {
    return (
      <div
        className="glass-card"
        style={{
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          border: '1px dashed var(--border-subtle)',
          margin: '1rem 0'
        }}
      >
        <p style={{ margin: 0 }}>📍 No route data available to visualize. Please optimize a route first.</p>
      </div>
    );
  }

  // Viewport dimensions
  const SVG_WIDTH = 700;
  const SVG_HEIGHT = 420;
  const PADDING = 65;

  // Extract coordinate bounds
  const lats = route.map(r => Number(r.latitude)).filter(n => !isNaN(n));
  const lons = route.map(r => Number(r.longitude)).filter(n => !isNaN(n));

  const minLat = lats.length > 0 ? Math.min(...lats) : 13.0;
  const maxLat = lats.length > 0 ? Math.max(...lats) : 13.1;
  const minLon = lons.length > 0 ? Math.min(...lons) : 80.1;
  const maxLon = lons.length > 0 ? Math.max(...lons) : 80.3;

  const latSpan = maxLat - minLat;
  const lonSpan = maxLon - minLon;

  // Coordinate projection to SVG pixel space
  const projectPoint = (lat, lon) => {
    let x, y;

    if (lonSpan <= 0.00001) {
      x = SVG_WIDTH / 2;
    } else {
      x = PADDING + ((lon - minLon) / lonSpan) * (SVG_WIDTH - 2 * PADDING);
    }

    if (latSpan <= 0.00001) {
      y = SVG_HEIGHT / 2;
    } else {
      // Invert Y because SVG coordinates increase downwards while latitude increases upwards
      y = SVG_HEIGHT - (PADDING + ((lat - minLat) / latSpan) * (SVG_HEIGHT - 2 * PADDING));
    }

    return { x, y };
  };

  // Projected route waypoints
  const projectedStops = route.map((stop, idx) => {
    const { x, y } = projectPoint(Number(stop.latitude), Number(stop.longitude));
    return {
      ...stop,
      x,
      y,
      index: idx
    };
  });

  // Calculate segment paths and midpoints
  const segments = [];
  for (let i = 0; i < projectedStops.length - 1; i++) {
    const p1 = projectedStops[i];
    const p2 = projectedStops[i + 1];
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;
    segments.push({
      p1,
      p2,
      midX,
      midY,
      distanceKm: p2.distance_from_previous_km ?? 0.0
    });
  }

  const activeStop = activeStopIdx !== null ? projectedStops[activeStopIdx] : null;

  return (
    <div className="route-map-visualization" style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h4 style={{ margin: 0, fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f3f4f6' }}>
          <span>🗺️</span> Spatial Distribution & Sequence Map
        </h4>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Relative coordinates projected via Haversine plane
        </span>
      </div>

      <div
        style={{
          background: 'radial-gradient(ellipse at center, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 1) 100%)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          overflow: 'hidden',
          position: 'relative',
          boxShadow: 'inset 0 0 20px rgba(0, 0, 0, 0.5)'
        }}
      >
        <svg
          viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
          style={{ width: '100%', height: 'auto', display: 'block', maxHeight: '460px' }}
          role="img"
          aria-label="Geographic route sequence visualization"
        >
          <defs>
            {/* Grid Pattern */}
            <pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255, 255, 255, 0.04)" strokeWidth="1" />
            </pattern>

            {/* Glowing Gradient for Route Lines */}
            <linearGradient id="route-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>

            {/* Filter for Glow Effect */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>

            {/* Marker Arrow */}
            <marker
              id="route-arrow"
              viewBox="0 0 10 10"
              refX="6"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#38bdf8" />
            </marker>
          </defs>

          {/* Background Grid */}
          <rect width={SVG_WIDTH} height={SVG_HEIGHT} fill="url(#grid-pattern)" />

          {/* Compass Rose / Orientation Indicator */}
          <g transform={`translate(${SVG_WIDTH - 45}, 40)`} opacity="0.6">
            <circle cx="0" cy="0" r="18" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
            <path d="M 0 -14 L 4 -2 L 0 0 L -4 -2 Z" fill="#ef4444" />
            <path d="M 0 14 L 4 2 L 0 0 L -4 2 Z" fill="rgba(255,255,255,0.5)" />
            <text x="0" y="-17" fill="#ef4444" fontSize="8" fontWeight="bold" textAnchor="middle">N</text>
          </g>

          {/* Coordinate Bounds Overlay */}
          <text x="15" y="20" fill="rgba(255,255,255,0.3)" fontSize="9" fontFamily="monospace">
            LAT: {minLat.toFixed(3)}°N — {maxLat.toFixed(3)}°N
          </text>
          <text x="15" y="34" fill="rgba(255,255,255,0.3)" fontSize="9" fontFamily="monospace">
            LON: {minLon.toFixed(3)}°E — {maxLon.toFixed(3)}°E
          </text>

          {/* Route Segment Lines */}
          {segments.map((seg, idx) => (
            <g key={`seg-${idx}`}>
              {/* Glow line */}
              <line
                x1={seg.p1.x}
                y1={seg.p1.y}
                x2={seg.p2.x}
                y2={seg.p2.y}
                stroke="url(#route-gradient)"
                strokeWidth="4"
                strokeOpacity="0.4"
                strokeLinecap="round"
                filter="url(#glow)"
              />
              {/* Solid directional line */}
              <line
                x1={seg.p1.x}
                y1={seg.p1.y}
                x2={seg.p2.x}
                y2={seg.p2.y}
                stroke="url(#route-gradient)"
                strokeWidth="2.5"
                strokeDasharray="6 3"
                markerEnd="url(#route-arrow)"
              />

              {/* Segment Distance Pill */}
              <g transform={`translate(${seg.midX}, ${seg.midY})`}>
                <rect
                  x="-28"
                  y="-11"
                  width="56"
                  height="20"
                  rx="10"
                  fill="rgba(15, 23, 42, 0.9)"
                  stroke="#38bdf8"
                  strokeWidth="1"
                />
                <text
                  x="0"
                  y="3"
                  fill="#38bdf8"
                  fontSize="9"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {seg.distanceKm.toFixed(1)} km
                </text>
              </g>
            </g>
          ))}

          {/* Waypoint Nodes */}
          {projectedStops.map((stop, idx) => {
            const isSource = stop.type === 'source';
            const isSelected = activeStopIdx === idx;

            return (
              <g
                key={`stop-${idx}`}
                transform={`translate(${stop.x}, ${stop.y})`}
                style={{ cursor: 'pointer' }}
                onClick={() => setActiveStopIdx(isSelected ? null : idx)}
                onMouseEnter={() => setActiveStopIdx(idx)}
              >
                {/* Node Outer Ripple Ring */}
                <circle
                  cx="0"
                  cy="0"
                  r={isSource ? 22 : 18}
                  fill={isSource ? 'rgba(168, 85, 247, 0.2)' : 'rgba(6, 182, 212, 0.2)'}
                  stroke={isSource ? '#a855f7' : '#06b6d4'}
                  strokeWidth={isSelected ? 2 : 1}
                  strokeDasharray={isSelected ? '4 2' : 'none'}
                />

                {/* Main Node Circle */}
                <circle
                  cx="0"
                  cy="0"
                  r={isSource ? 14 : 11}
                  fill={isSource ? '#7e22ce' : '#0e7490'}
                  stroke="#ffffff"
                  strokeWidth="2"
                />

                {/* Node Content / Icon */}
                <text
                  x="0"
                  y={isSource ? 4 : 4}
                  fill="#ffffff"
                  fontSize={isSource ? "10" : "9"}
                  fontWeight="900"
                  textAnchor="middle"
                >
                  {isSource ? '★' : stop.sequence}
                </text>

                {/* Waypoint Label */}
                <text
                  x="0"
                  y={isSource ? -26 : 28}
                  fill={isSource ? '#c084fc' : '#38bdf8'}
                  fontSize="10"
                  fontWeight="700"
                  textAnchor="middle"
                  style={{
                    textShadow: '0 1px 4px rgba(0,0,0,0.9)',
                    pointerEvents: 'none'
                  }}
                >
                  {isSource ? 'Origin Dispatch' : `Stop ${stop.sequence}: ${(stop.name || '').slice(0, 16)}`}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Stop Details Popover / Card */}
        {activeStop && (
          <div
            style={{
              position: 'absolute',
              bottom: '12px',
              left: '12px',
              right: '12px',
              background: 'rgba(15, 23, 42, 0.95)',
              backdropFilter: 'blur(8px)',
              border: `1px solid ${activeStop.type === 'source' ? 'rgba(168, 85, 247, 0.5)' : 'rgba(6, 182, 212, 0.5)'}`,
              borderRadius: 'var(--radius-sm)',
              padding: '0.65rem 1rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.75rem',
              fontSize: '0.82rem'
            }}
          >
            <div>
              <span
                style={{
                  color: activeStop.type === 'source' ? '#c084fc' : '#38bdf8',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  textTransform: 'uppercase'
                }}
              >
                {activeStop.type === 'source' ? '📍 Origin Dispatch Point' : `🏁 Sequence Stop #${activeStop.sequence}`}
              </span>
              <div style={{ color: '#f9fafb', fontWeight: 600, fontSize: '0.95rem' }}>
                {activeStop.name}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--text-muted)' }}>
              <span>Lat: {Number(activeStop.latitude).toFixed(4)}°, Lon: {Number(activeStop.longitude).toFixed(4)}°</span>
              {activeStop.type !== 'source' && (
                <span style={{ color: '#34d399', fontWeight: 700 }}>
                  📦 {activeStop.allocated_meals} meals drop
                </span>
              )}
              {activeStop.type !== 'source' && (
                <span style={{ color: '#fbbf24', fontWeight: 600 }}>
                  📏 +{activeStop.distance_from_previous_km} km
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Academic / Heuristic Disclaimer */}
      <div
        style={{
          marginTop: '0.75rem',
          padding: '0.5rem 0.85rem',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          fontSize: '0.74rem',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}
      >
        <span>ℹ️</span>
        <span>
          <strong>Geographic Visualization Note:</strong> Coordinates and route vectors are projected mathematically on a relative 2D Cartesian plane using Haversine great-circle distances. Does not represent live road networks, turn-by-turn navigation, or traffic conditions.
        </span>
      </div>
    </div>
  );
}
