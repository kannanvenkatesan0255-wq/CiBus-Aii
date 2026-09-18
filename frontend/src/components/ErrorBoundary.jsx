import React from 'react';

/**
 * ErrorBoundary - Top-level React error boundary preventing blank white screens
 * and providing a user-friendly recovery interface.
 */
export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error internally in developer console without exposing sensitive data
    console.error('CIBUS-AI Error Boundary Caught UI Exception:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  returnHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            background: '#0b0f19',
            color: '#f3f4f6',
            fontFamily: 'Inter, system-ui, sans-serif'
          }}
        >
          <div
            className="glass-card"
            style={{
              maxWidth: '520px',
              width: '100%',
              padding: '2.5rem',
              borderRadius: '16px',
              background: 'rgba(15, 23, 42, 0.85)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
              textAlign: 'center'
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2rem',
                margin: '0 auto 1.25rem auto',
                border: '1px solid rgba(239, 68, 68, 0.3)'
              }}
            >
              ⚠️
            </div>

            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 0.5rem 0', color: '#f87171' }}>
              Something went wrong
            </h2>

            <p style={{ fontSize: '0.9rem', color: '#9ca3af', lineHeight: 1.6, marginBottom: '1.75rem' }}>
              An unexpected interface rendering issue occurred. Your data has not been corrupted. Please reload the application to resume workflow.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={this.handleReload}
                style={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#ffffff',
                  border: 'none',
                  padding: '0.65rem 1.4rem',
                  borderRadius: '8px',
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  cursor: 'pointer'
                }}
              >
                🔄 Reload Application
              </button>

              <button
                type="button"
                onClick={this.handleReset}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  color: '#e5e7eb',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  padding: '0.65rem 1.2rem',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: 'pointer'
                }}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
