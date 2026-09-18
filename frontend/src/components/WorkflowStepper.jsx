import React from 'react';

const STEPS = [
  {
    id: 'prediction',
    num: 1,
    title: 'Surplus Forecast',
    subtitle: 'ML Model Inference',
    icon: '⚡',
    anchor: '#prediction-section',
    requiredStatus: ['PREDICTED', 'MATCHED', 'ROUTE_OPTIMIZED', 'RECORDED']
  },
  {
    id: 'matching',
    num: 2,
    title: 'Recipient Matching',
    subtitle: 'Multi-Criteria Allocation',
    icon: '🤝',
    anchor: '#ngo-matching',
    requiredStatus: ['MATCHED', 'ROUTE_OPTIMIZED', 'RECORDED']
  },
  {
    id: 'routing',
    num: 3,
    title: 'Route Planning',
    subtitle: 'Nearest-Neighbor Sequence',
    icon: '🗺️',
    anchor: '#route-planning',
    requiredStatus: ['ROUTE_OPTIMIZED', 'RECORDED']
  },
  {
    id: 'dashboard',
    num: 4,
    title: 'Impact Telemetry',
    subtitle: 'Activity Logging & Analytics',
    icon: '📊',
    anchor: '#impact-dashboard',
    requiredStatus: ['RECORDED']
  }
];

export default function WorkflowStepper({ currentStatus = 'IDLE', onResetWorkflow }) {
  const getStepState = (step) => {
    const isCompleted = step.requiredStatus.includes(currentStatus);
    let isActive = false;

    if (currentStatus === 'IDLE' && step.id === 'prediction') isActive = true;
    else if (currentStatus === 'PREDICTED' && step.id === 'matching') isActive = true;
    else if (currentStatus === 'MATCHED' && step.id === 'routing') isActive = true;
    else if (currentStatus === 'ROUTE_OPTIMIZED' && step.id === 'dashboard') isActive = true;
    else if (currentStatus === 'RECORDED' && step.id === 'dashboard') isActive = true;

    return { isCompleted, isActive };
  };

  return (
    <div className="glass-card workflow-stepper-container" style={{ margin: '0 auto 2rem auto', maxWidth: '1100px', padding: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span style={{ fontSize: '1.2rem' }}>🔄</span>
          <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#f3f4f6' }}>
            End-to-End Redistribution Workflow
          </h3>
          <span
            className="track-badge"
            style={{
              background: currentStatus === 'RECORDED'
                ? 'rgba(16, 185, 129, 0.15)'
                : 'rgba(56, 189, 248, 0.15)',
              color: currentStatus === 'RECORDED' ? '#34d399' : '#38bdf8',
              borderColor: currentStatus === 'RECORDED'
                ? 'rgba(16, 185, 129, 0.3)'
                : 'rgba(56, 189, 248, 0.3)'
            }}
          >
            Status: {currentStatus}
          </span>
        </div>

        {currentStatus !== 'IDLE' && onResetWorkflow && (
          <button
            type="button"
            className="btn btn-secondary"
            style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem' }}
            onClick={onResetWorkflow}
          >
            Reset Workflow
          </button>
        )}
      </div>

      <div className="stepper-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', position: 'relative' }}>
        {STEPS.map((step) => {
          const { isCompleted, isActive } = getStepState(step);

          let borderColor = 'var(--border-subtle)';
          let bgColor = 'rgba(255, 255, 255, 0.02)';
          let iconBg = 'rgba(255, 255, 255, 0.08)';

          if (isCompleted) {
            borderColor = 'rgba(16, 185, 129, 0.4)';
            bgColor = 'rgba(16, 185, 129, 0.06)';
            iconBg = 'linear-gradient(135deg, #10b981, #059669)';
          } else if (isActive) {
            borderColor = 'rgba(56, 189, 248, 0.4)';
            bgColor = 'rgba(56, 189, 248, 0.08)';
            iconBg = 'linear-gradient(135deg, #0284c7, #0369a1)';
          }

          return (
            <a
              key={step.id}
              href={step.anchor}
              style={{
                textDecoration: 'none',
                color: 'inherit',
                display: 'block'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  padding: '0.85rem',
                  borderRadius: 'var(--radius-md)',
                  background: bgColor,
                  border: `1px solid ${borderColor}`,
                  transition: 'all 0.2s ease',
                  cursor: 'pointer'
                }}
              >
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '50%',
                    background: iconBg,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 800,
                    fontSize: '0.9rem',
                    color: '#ffffff',
                    flexShrink: 0,
                    boxShadow: isCompleted ? '0 0 10px rgba(16, 185, 129, 0.3)' : 'none'
                  }}
                >
                  {isCompleted ? '✓' : step.num}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <span style={{ fontSize: '0.85rem' }}>{step.icon}</span>
                    <span style={{ fontSize: '0.88rem', fontWeight: 700, color: isCompleted ? '#34d399' : isActive ? '#38bdf8' : '#e5e7eb' }}>
                      {step.title}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {step.subtitle}
                  </div>
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
