import React from 'react';

export default function HowItWorks() {
  const steps = [
    {
      num: '1',
      title: 'Operational Input',
      desc: 'Kitchen operations enter advance indicators (planned meals, diner forecast, weather, event format).'
    },
    {
      num: '2',
      title: 'Pydantic Validation',
      desc: 'FastAPI validates domain ranges and guarantees 0% data leakage by rejecting post-service features.'
    },
    {
      num: '3',
      title: 'ML Preprocessing',
      desc: 'Serialized ColumnTransformer applies pre-fitted OneHotEncoding and pass-through numerical scaling.'
    },
    {
      num: '4',
      title: 'Random Forest Inference',
      desc: 'Tuned ensemble regressor computes quantitative continuous surplus estimate (R² = 0.9543).'
    },
    {
      num: '5',
      title: 'Redistribution Alert',
      desc: 'System outputs forecasted surplus portions and early notification dispatch for partner shelters.'
    }
  ];

  return (
    <section className="info-section">
      <div className="section-header">
        <h2 className="section-title">How CIBUS-AI Works</h2>
        <p>End-to-end dataflow from pre-service entry to actionable recovery intelligence</p>
      </div>

      <div className="steps-grid">
        {steps.map((step) => (
          <div key={step.num} className="step-card">
            <div className="step-badge">{step.num}</div>
            <h3 className="step-title">{step.title}</h3>
            <p style={{ fontSize: '0.88rem' }}>{step.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
