import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import ImpactDashboard from './components/ImpactDashboard';
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
  const [prediction, setPrediction] = useState(null);
  const [matchedNGOs, setMatchedNGOs] = useState([]);
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
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during prediction.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setPrediction(null);
    setMatchedNGOs([]);
    setError('');
    setIsLoading(false);
  };

  const handleActivityLogged = () => {
    // Increment key to trigger fresh data load in dashboard
    setDashboardKey(prev => prev + 1);
  };

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-content">
        <Hero />

        {/* Operational Impact Dashboard & ML Performance Panel */}
        <ImpactDashboard key={dashboardKey} />

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

        {/* Extended Redistribution Module (Active when prediction exists or accessible for demo) */}
        <NGOMatchingSection
          predictedSurplus={prediction ? prediction.predicted_surplus_meals : 0}
          onMatchesUpdated={(matches) => setMatchedNGOs(matches)}
        />

        {/* Route Optimization & Pickup Planning Module */}
        <RoutePlanningSection
          matchedNGOs={matchedNGOs}
          predictedSurplus={prediction ? prediction.predicted_surplus_meals : 0}
          onActivityLogged={handleActivityLogged}
        />

        <HowItWorks />
        <FutureModules />
      </main>

      <Footer />
    </div>
  );
}


