import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import ImpactDashboard from './components/ImpactDashboard';
import WorkflowStepper from './components/WorkflowStepper';
import PredictionForm from './components/PredictionForm';
import ResultCard from './components/ResultCard';
import NGOMatchingSection from './components/NGOMatchingSection';
import RoutePlanningSection from './components/RoutePlanningSection';
import HowItWorks from './components/HowItWorks';
import FutureModules from './components/FutureModules';
import Footer from './components/Footer';
import { predictSurplus } from './services/predictionService';
import './styles/App.css';

export default function App() {
  const [workflowStatus, setWorkflowStatus] = useState('IDLE');
  const [prediction, setPrediction] = useState(null);
  const [matchedNGOs, setMatchedNGOs] = useState([]);
  const [routeResult, setRouteResult] = useState(null);
  const [dashboardKey, setDashboardKey] = useState(0);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handlePredict = async (formData) => {
    setIsLoading(true);
    setError('');
    setPrediction(null);

    try {
      const result = await predictSurplus(formData);
      setPrediction(result);
      setWorkflowStatus('PREDICTED');
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during prediction.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMatchesUpdated = (matches) => {
    setMatchedNGOs(matches);
  };

  const handleMatchingSuccess = (result) => {
    setWorkflowStatus('MATCHED');
  };

  const handleRouteOptimized = (result) => {
    setRouteResult(result);
    setWorkflowStatus('ROUTE_OPTIMIZED');
  };

  const handleActivityLogged = (recordedRoute) => {
    setWorkflowStatus('RECORDED');
    // Increment key to trigger fresh data load in dashboard
    setDashboardKey(prev => prev + 1);
  };

  const handleReset = () => {
    setPrediction(null);
    setMatchedNGOs([]);
    setRouteResult(null);
    setWorkflowStatus('IDLE');
    setError('');
    setIsLoading(false);
  };

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-content">
        <Hero />

        {/* Visual Workflow Progress Stepper */}
        <WorkflowStepper
          currentStatus={workflowStatus}
          onResetWorkflow={handleReset}
        />

        {/* Operational Impact Dashboard */}
        <ImpactDashboard key={dashboardKey} />

        {/* Prediction Engine Stage */}
        <div className="prediction-grid" id="prediction-section">
          <PredictionForm
            onSubmit={handlePredict}
            isLoading={isLoading}
            onReset={handleReset}
          />
          
          <ResultCard
            prediction={prediction}
            error={error}
            isLoading={isLoading}
          />
        </div>

        {/* Recipient NGO Matching & Allocation Stage */}
        <NGOMatchingSection
          predictedSurplus={prediction ? prediction.predicted_surplus_meals : 0}
          onMatchesUpdated={handleMatchesUpdated}
          onMatchingSuccess={handleMatchingSuccess}
        />

        {/* Route Optimization & SVG Sequence Map Stage */}
        <RoutePlanningSection
          matchedNGOs={matchedNGOs}
          predictedSurplus={prediction ? prediction.predicted_surplus_meals : 0}
          onRouteOptimized={handleRouteOptimized}
          onActivityLogged={handleActivityLogged}
        />

        <HowItWorks />
        <FutureModules />
      </main>

      <Footer />
    </div>
  );
}
