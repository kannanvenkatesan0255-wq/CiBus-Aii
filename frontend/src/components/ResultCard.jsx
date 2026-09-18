import React from 'react';

export default function ResultCard({ prediction, error, isLoading }) {
  if (error) {
    return (
      <div className="glass-card result-card">
        <div className="card-header">
          <h2 className="card-title">
            <span>⚠️</span> Prediction Error
          </h2>
        </div>
        <div className="alert-error" role="alert">
          {error}
        </div>
        <p className="card-subtitle">
          Please verify your inputs or ensure the CIBUS-AI FastAPI server is running.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="glass-card result-card">
        <div className="result-placeholder">
          <div className="result-placeholder-icon">⏳</div>
          <h3 style={{ marginBottom: '0.5rem' }}>Processing Operational Features</h3>
          <p>Applying ColumnTransformer encoding and executing Random Forest regression inference...</p>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="glass-card result-card">
        <div className="card-header">
          <h2 className="card-title">
            <span>🎯</span> Prediction Intelligence
          </h2>
          <p className="card-subtitle">
            Forecast output will appear here after submission
          </p>
        </div>
        <div className="result-placeholder">
          <div className="result-placeholder-icon">🍽️</div>
          <p>Fill out the operational form and click <strong>Predict Surplus Meals</strong> to generate real-time AI food recovery intelligence.</p>
        </div>
      </div>
    );
  }

  const { predicted_surplus_meals, model_name, recommended_action, input_summary } = prediction;

  return (
    <div className="glass-card result-card result-active">
      <div className="card-header">
        <h2 className="card-title">
          <span>✨</span> Surplus Forecast Result
        </h2>
        <p className="card-subtitle">
          Estimated unconsumed meal portions available for redistribution
        </p>
      </div>

      <div className="surplus-display">
        <div className="surplus-unit">Predicted Surplus Meals</div>
        <div className="surplus-number" id="predicted-value">
          {predicted_surplus_meals.toFixed(1)}
        </div>
        <div className="surplus-unit">Portions / Meals</div>
      </div>

      {recommended_action && (
        <div className="recommendation-box">
          <strong>Logistics Advisory:</strong> {recommended_action}
        </div>
      )}

      <table className="metadata-table">
        <tbody>
          <tr>
            <td>Target Variable</td>
            <td>Surplus_Meals (Regression)</td>
          </tr>
          <tr>
            <td>Model Algorithm</td>
            <td>Random Forest Regressor</td>
          </tr>
          <tr>
            <td>Ensemble Configuration</td>
            <td>Tuned (depth=15, n=200)</td>
          </tr>
          {input_summary && (
            <>
              <tr>
                <td>Service Shift</td>
                <td>{input_summary.day} ({input_summary.weather})</td>
              </tr>
              <tr>
                <td>Meals Prepared / Forecast</td>
                <td>{input_summary.meals_prepared} / {input_summary.customers_forecast}</td>
              </tr>
            </>
          )}
        </tbody>
      </table>
    </div>
  );
}
