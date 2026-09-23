import React from 'react';

export default function Header() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="brand-section">
          <div className="logo-badge">C</div>
          <div className="brand-title">
            <span>CIBUS-AI</span>
            <span className="tagline-small">Predict. Connect. Nourish.</span>
          </div>
        </div>

        <nav className="header-nav" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <a href="#impact-dashboard" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 600 }}>
            📊 Dashboard
          </a>
          <a href="#prediction-section" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 600 }}>
            ⚡ Predictor
          </a>
          <a href="#ngo-matching" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 600 }}>
            🤝 Redistribution
          </a>
          <a href="#route-planning" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none', fontWeight: 600 }}>
            🗺️ Routing
          </a>
        </nav>
      </div>
    </header>
  );
}

