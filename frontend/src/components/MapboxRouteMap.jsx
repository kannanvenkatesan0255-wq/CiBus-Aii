import React, { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

/**
 * MapboxRouteMap - Production-grade interactive Mapbox GL visualization
 * for CIBUS-AI surplus food redistribution routes.
 * 
 * Features:
 * - Donor dispatch facility marker (vibrant violet styling)
 * - Sequenced NGO recipient markers (vibrant cyan numbered pins)
 * - Detailed interactive popups with meal drop counts & distances
 * - Haversine optimized route line rendering via GeoJSON LineString
 * - Auto-fit camera bounding box across all itinerary coordinates
 * - Map style toggle (Dark / Streets / Satellite)
 * - Comprehensive map legend & responsive layout
 */
export default function MapboxRouteMap({ route = [], source = null }) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);
  const [activeStyle, setActiveStyle] = useState('mapbox://styles/mapbox/dark-v11');

  // Token is read strictly from client environment; NEVER hardcoded
  const mapboxToken = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN || '';

  // Filter valid route coordinates
  const validStops = (route || []).filter(stop => {
    const lat = Number(stop.latitude);
    const lon = Number(stop.longitude);
    return !isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
  });

  useEffect(() => {
    if (!mapboxToken) {
      setMapError('Mapbox access token is missing. Please configure VITE_MAPBOX_ACCESS_TOKEN in frontend/.env.local.');
      return;
    }

    if (!mapContainerRef.current) return;
    if (validStops.length === 0) return;

    mapboxgl.accessToken = mapboxToken;

    const initialCenter = [
      Number(validStops[0].longitude),
      Number(validStops[0].latitude)
    ];

    try {
      const map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: activeStyle,
        center: initialCenter,
        zoom: 12,
        attributionControl: true
      });

      mapRef.current = map;

      // Add navigation controls (zoom in/out, compass)
      map.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'top-right');
      map.addControl(new mapboxgl.FullscreenControl(), 'top-right');

      map.on('load', () => {
        setMapLoaded(true);
        drawRouteAndMarkers(map);
      });

      map.on('error', (e) => {
        console.warn('Mapbox GL runtime notice:', e?.error?.message || e);
        if (e?.error?.status === 401 || (e?.error?.message && e.error.message.includes('Forbidden'))) {
          setMapError('Invalid Mapbox access token or unauthorized domain. Please check your token.');
        }
      });

      return () => {
        markersRef.current.forEach(m => m.remove());
        markersRef.current = [];
        map.remove();
        mapRef.current = null;
      };
    } catch (err) {
      console.error('Failed to initialize Mapbox GL:', err);
      setMapError(`Unable to initialize Mapbox WebGL context: ${err.message}`);
    }
  }, [mapboxToken, activeStyle]);

  // Update route line and markers whenever route data updates
  useEffect(() => {
    if (mapRef.current && mapLoaded) {
      drawRouteAndMarkers(mapRef.current);
    }
  }, [route, mapLoaded]);

  const drawRouteAndMarkers = (map) => {
    if (!map) return;

    // Clear previous markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    if (validStops.length === 0) return;

    const coordinates = validStops.map(s => [Number(s.longitude), Number(s.latitude)]);

    // 1. Add or Update Route GeoJSON Source and Layers
    const geojsonData = {
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'LineString',
        coordinates: coordinates
      }
    };

    if (map.getSource('cibus-route-source')) {
      map.getSource('cibus-route-source').setData(geojsonData);
    } else {
      map.addSource('cibus-route-source', {
        type: 'geojson',
        data: geojsonData
      });

      // Ambient glow layer underneath
      map.addLayer({
        id: 'cibus-route-glow',
        type: 'line',
        source: 'cibus-route-source',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': '#06b6d4',
          'line-width': 8,
          'line-opacity': 0.35,
          'line-blur': 3
        }
      });

      // Directional dashed route line
      map.addLayer({
        id: 'cibus-route-line',
        type: 'line',
        source: 'cibus-route-source',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': '#38bdf8',
          'line-width': 3.5,
          'line-dasharray': [2, 1]
        }
      });
    }

    // 2. Add Markers for Donor and NGOs
    const bounds = new mapboxgl.LngLatBounds();

    validStops.forEach((stop) => {
      const lat = Number(stop.latitude);
      const lon = Number(stop.longitude);
      const isSource = stop.type === 'source' || stop.sequence === 0;

      bounds.extend([lon, lat]);

      // Custom Marker Element
      const el = document.createElement('div');
      el.className = isSource ? 'cibus-marker-donor' : 'cibus-marker-ngo';
      el.style.cursor = 'pointer';

      if (isSource) {
        el.innerHTML = `
          <div style="
            background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%);
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 18px;
            box-shadow: 0 0 16px rgba(168, 85, 247, 0.7), 0 3px 8px rgba(0, 0, 0, 0.5);
            border: 2.5px solid #ffffff;
            transition: transform 0.2s ease;
          " title="${stop.name || 'Origin Donor'}">🏢</div>
        `;
      } else {
        el.innerHTML = `
          <div style="
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 13px;
            font-weight: 800;
            box-shadow: 0 0 14px rgba(6, 182, 212, 0.65), 0 3px 8px rgba(0, 0, 0, 0.5);
            border: 2px solid #ffffff;
            transition: transform 0.2s ease;
          " title="Stop ${stop.sequence}: ${stop.name}">${stop.sequence}</div>
        `;
      }

      el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.15)';
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1.0)';
      });

      // Interactive Popup
      const popupHtml = isSource ? `
        <div style="font-family: inherit; color: #0f172a; padding: 4px; min-width: 170px;">
          <div style="font-size: 10px; font-weight: 800; color: #7e22ce; text-transform: uppercase; letter-spacing: 0.5px;">
            📍 Origin Dispatch Center
          </div>
          <div style="font-size: 14px; font-weight: 700; margin: 3px 0 6px 0; color: #0f172a;">
            ${source?.name || stop.name || 'Food Dispatch Facility'}
          </div>
          <div style="font-size: 11px; color: #475569; margin-bottom: 4px;">
            Coords: <strong>${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E</strong>
          </div>
          <div style="background: #f3e8ff; color: #6b21a8; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; display: inline-block;">
            Starting Origin
          </div>
        </div>
      ` : `
        <div style="font-family: inherit; color: #0f172a; padding: 4px; min-width: 180px;">
          <div style="font-size: 10px; font-weight: 800; color: #0891b2; text-transform: uppercase; letter-spacing: 0.5px;">
            🏁 Stop #${stop.sequence} • Recipient NGO
          </div>
          <div style="font-size: 14px; font-weight: 700; margin: 3px 0 6px 0; color: #0f172a;">
            ${stop.name}
          </div>
          <div style="background: #ecfdf5; color: #059669; font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 4px; margin-bottom: 4px; display: inline-block;">
            📦 Drop: ${stop.allocated_meals} meals
          </div>
          <div style="font-size: 11px; color: #d97706; font-weight: 600; margin-bottom: 2px;">
            📏 Segment Distance: +${Number(stop.distance_from_previous_km || 0).toFixed(2)} km
          </div>
          <div style="font-size: 11px; color: #64748b;">
            Coords: <strong>${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E</strong>
          </div>
        </div>
      `;

      const popup = new mapboxgl.Popup({
        offset: isSource ? 22 : 18,
        closeButton: true,
        maxWidth: '300px'
      }).setHTML(popupHtml);

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([lon, lat])
        .setPopup(popup)
        .addTo(map);

      markersRef.current.push(marker);
    });

    // 3. Fit bounds with smooth camera animation
    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, {
        padding: { top: 60, bottom: 60, left: 60, right: 60 },
        maxZoom: 14.5,
        duration: 1200
      });
    }
  };

  if (mapError) {
    return (
      <div
        className="glass-card"
        style={{
          padding: '1.75rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          background: 'rgba(239, 68, 68, 0.05)',
          borderRadius: 'var(--radius-md)',
          margin: '1rem 0'
        }}
      >
        <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>⚠️</div>
        <h4 style={{ color: '#ef4444', margin: '0 0 0.5rem 0' }}>Mapbox Service Notice</h4>
        <p style={{ margin: 0, fontSize: '0.88rem' }}>{mapError}</p>
        <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Tip: Ensure a valid Mapbox public token is set in <code>frontend/.env.local</code>.
        </p>
      </div>
    );
  }

  return (
    <div className="mapbox-visualization-wrapper" style={{ marginTop: '1.25rem', marginBottom: '1.25rem' }}>
      {/* Map Controls Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.75rem',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.2rem' }}>🗺️</span>
          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f3f4f6' }}>
            Interactive Mapbox Route Network
          </span>
          <span
            style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '12px',
              background: 'rgba(6, 182, 212, 0.15)',
              color: '#38bdf8',
              border: '1px solid rgba(6, 182, 212, 0.3)'
            }}
          >
            Live Tiles
          </span>
        </div>

        {/* Mapbox Style Switcher */}
        <div style={{ display: 'flex', gap: '0.35rem', background: 'rgba(255, 255, 255, 0.05)', padding: '3px', borderRadius: '8px' }}>
          {[
            { id: 'mapbox://styles/mapbox/dark-v11', label: 'Dark' },
            { id: 'mapbox://styles/mapbox/streets-v12', label: 'Streets' },
            { id: 'mapbox://styles/mapbox/satellite-streets-v12', label: 'Satellite' }
          ].map(style => (
            <button
              key={style.id}
              onClick={() => setActiveStyle(style.id)}
              style={{
                background: activeStyle === style.id ? 'var(--primary, #06b6d4)' : 'transparent',
                color: activeStyle === style.id ? '#ffffff' : 'var(--text-muted)',
                border: 'none',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {style.label}
            </button>
          ))}
        </div>
      </div>

      {/* Map Container */}
      <div
        style={{
          position: 'relative',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.45)',
          background: '#0f172a'
        }}
      >
        <div
          ref={mapContainerRef}
          style={{
            width: '100%',
            height: '460px',
            minHeight: '380px'
          }}
        />

        {/* Floating Map Legend */}
        <div
          style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            background: 'rgba(15, 23, 42, 0.92)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '8px',
            padding: '8px 14px',
            fontSize: '0.78rem',
            color: '#e2e8f0',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
            zIndex: 1
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: '6px', fontSize: '0.8rem', color: '#f8fafc' }}>
            Itinerary Legend
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#a855f7', border: '1.5px solid white' }} />
              <span>Food Donor Facility</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#06b6d4', border: '1.5px solid white' }} />
              <span>Recipient NGO Stops (Sequenced)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ display: 'inline-block', width: '16px', height: '3px', background: '#38bdf8', borderRadius: '2px' }} />
              <span>Optimized Haversine Route Path</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
