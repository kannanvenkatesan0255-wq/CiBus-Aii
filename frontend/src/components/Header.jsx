import React from 'react';
import HealthStatus from './HealthStatus';

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

        <div className="header-badges">
          <span className="track-badge">CIT ML PBL</span>
          <HealthStatus />
        </div>
      </div>
    </header>
  );
}
