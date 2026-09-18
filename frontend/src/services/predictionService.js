/**
 * CIBUS-AI - Frontend API Communication Service
 * File: frontend/src/services/predictionService.js
 * 
 * Purpose:
 * Connects the React client to the FastAPI backend service (/api/predict, /health, /api/model-info).
 * Strictly omits 'Meals_Sold' to enforce zero data leakage.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Predicts surplus meals for a scheduled dining or catering service.
 * 
 * @param {Object} formData - Operational inputs matching backend Pydantic schema
 * @returns {Promise<Object>} API Prediction response with predicted meals & recommendations
 */
export async function predictSurplus(formData) {
  // Ensure strict data leakage prevention
  const cleanPayload = {
    Day: String(formData.Day).trim(),
    Weather: String(formData.Weather).trim(),
    Customers_Forecast: parseInt(formData.Customers_Forecast, 10),
    Meals_Prepared: parseInt(formData.Meals_Prepared, 10),
    Festival: formData.Festival || "No",
    Event_Type: formData.Event_Type || "Regular",
    Staff_Count: parseInt(formData.Staff_Count, 10),
    Avg_Rating: parseFloat(formData.Avg_Rating),
    Special_Event: parseInt(formData.Special_Event, 10) === 1 ? 1 : 0
  };

  // Explicit safety assertion: Meals_Sold must never be transmitted
  if ('Meals_Sold' in cleanPayload || 'meals_sold' in cleanPayload) {
    throw new Error("Client Validation Error: 'Meals_Sold' is a post-service outcome and cannot be sent.");
  }

  const endpoint = `${API_BASE_URL}/api/predict`;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(cleanPayload)
    });

    if (!response.ok) {
      let errorMessage = `Server error (HTTP ${response.status})`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(d => `${d.loc ? d.loc.join('.') : 'Field'}: ${d.msg}`).join(', ');
          } else {
            errorMessage = errorData.detail;
          }
        }
      } catch {
        // Fallback to status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to connect to the CIBUS-AI prediction backend. Please ensure the FastAPI server is running on port 8000.");
    }
    throw error;
  }
}

/**
 * Checks system readiness and ML artifact status.
 * 
 * @returns {Promise<Object>} Health response
 */
export async function checkBackendHealth() {
  const endpoint = `${API_BASE_URL}/health`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) {
      return { status: 'degraded', model_loaded: false, preprocessor_loaded: false };
    }
    return await response.json();
  } catch {
    return { status: 'offline', model_loaded: false, preprocessor_loaded: false };
  }
}

/**
 * Retrieves active model metadata and evaluation statistics.
 * 
 * @returns {Promise<Object>} Model info response
 */
export async function getModelMetadata() {
  const endpoint = `${API_BASE_URL}/api/model-info`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) {
      throw new Error(`Failed to load model info (HTTP ${response.status})`);
    }
    return await response.json();
  } catch (error) {
    console.warn("Could not retrieve model metadata:", error.message);
    return null;
  }
}
