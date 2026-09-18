import React, { useState, useEffect } from 'react';
import { checkBackendHealth } from '../services/predictionService';

export default function HealthStatus() {
  const [health, setHealth] = useState({ status: 'checking', model_loaded: false, preprocessor_loaded: false });

  const fetchStatus = async () => {
    const res = await checkBackendHealth();
    setHealth(res);
  };

  useEffect(() => {
    fetchStatus();
    // Non-aggressive 30-second heartbeat check
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health.status === 'healthy' && health.model_loaded;

  return (
    <div 
      className={`health-badge ${isHealthy ? 'healthy' : 'offline'}`}
      title={isHealthy ? 'FastAPI & Random Forest Model Ready' : 'Backend or Model Unavailable'}
    >
      <span className="health-dot"></span>
      <span>{isHealthy ? 'Backend Connected' : 'Backend Offline'}</span>
    </div>
  );
}
