import React from 'react';

export default function FutureModules() {
  const modules = [
    {
      title: 'Automated NGO Matching',
      desc: 'Pairing surplus batches with nearby verified shelters based on dietary requirements and storage capacity.'
    },
    {
      title: 'Multi-Stop Vehicle Routing',
      desc: 'Optimizing pickup paths and delivery windows across multiple dining halls using heuristic route planning.'
    },
    {
      title: 'Volunteer Dispatch Network',
      desc: 'Push notification dispatch system assigning local courier volunteers to urgent food recovery runs.'
    },
    {
      title: 'Geospatial Live Tracking',
      desc: 'Real-time telemetry and food transit temperature monitoring mapped on interactive GIS dashboards.'
    }
  ];

  return (
    <section className="info-section">
      <div className="section-header">
        <h2 className="section-title">Future Platform Roadmap</h2>
        <p>Upcoming system modules scheduled for future expansion (Currently in design phase)</p>
      </div>

      <div className="future-modules-grid">
        {modules.map((m, idx) => (
          <div key={idx} className="future-card">
            <span className="future-status-tag">Future Scope</span>
            <h3 className="step-title" style={{ marginTop: '0.25rem' }}>{m.title}</h3>
            <p style={{ fontSize: '0.88rem' }}>{m.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
