import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
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

  return (
    <div className="app-container">
      <Header />
      
      <main className="main-content">
        <Hero />

        <div className="prediction-grid">
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
        />

        <HowItWorks />
        <FutureModules />
      </main>

      <Footer />
    </div>
  );
}

