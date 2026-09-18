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

/**
 * Matches candidate recipient NGOs for a predicted surplus meal volume.
 * 
 * @param {Object} matchParams - { predicted_surplus_meals, food_type, source_latitude, source_longitude, max_matches }
 * @returns {Promise<Object>} Matching and capacity allocation response
 */
export async function matchNGOs(matchParams) {
  const endpoint = `${API_BASE_URL}/api/match-ngos`;

  const payload = {
    predicted_surplus_meals: parseFloat(matchParams.predicted_surplus_meals || 0),
    food_type: matchParams.food_type || "Both",
    source_latitude: matchParams.source_latitude ? parseFloat(matchParams.source_latitude) : null,
    source_longitude: matchParams.source_longitude ? parseFloat(matchParams.source_longitude) : null,
    max_matches: parseInt(matchParams.max_matches || 5, 10)
  };

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errorMessage = `Matching service error (HTTP ${response.status})`;
      try {
        const errData = await response.json();
        if (errData.detail) errorMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to connect to CIBUS-AI NGO Matching API. Please ensure the backend is running.");
    }
    throw error;
  }
}

/**
 * Plans an optimized delivery itinerary from food donor source to matched recipient NGOs.
 * 
 * @param {Object} routeParams - { source: { name, latitude, longitude }, ngos: [...] }
 * @returns {Promise<Object>} Route optimization response with ordered stops and summary
 */
export async function optimizeRoute(routeParams) {
  const endpoint = `${API_BASE_URL}/api/optimize-route`;

  const payload = {
    source: {
      name: String(routeParams.source?.name || 'Food Dispatch Facility').trim(),
      latitude: parseFloat(routeParams.source?.latitude || 13.0067),
      longitude: parseFloat(routeParams.source?.longitude || 80.2026)
    },
    ngos: (routeParams.ngos || []).map(ngo => ({
      ngo_id: String(ngo.ngo_id),
      name: String(ngo.ngo_name || ngo.name || ngo.ngo_id),
      latitude: parseFloat(ngo.latitude || (ngo.source_latitude ?? 13.0067)),
      longitude: parseFloat(ngo.longitude || (ngo.source_longitude ?? 80.2026)),
      allocated_meals: parseFloat(ngo.allocated_meals || 0)
    }))
  };

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errorMessage = `Route optimization error (HTTP ${response.status})`;
      try {
        const errData = await response.json();
        if (errData.detail) errorMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to connect to CIBUS-AI Route Optimization API. Please ensure the backend is running.");
    }
    throw error;
  }
}

/**
 * Retrieves aggregate operational dashboard summary and ML model performance metrics.
 * 
 * @returns {Promise<Object>} Dashboard summary and model performance payload
 */
export async function getDashboardSummary() {
  const endpoint = `${API_BASE_URL}/api/dashboard/summary`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Failed to load dashboard metrics (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to connect to CIBUS-AI Dashboard API. Please ensure the backend server is running.");
    }
    throw error;
  }
}

/**
 * Retrieves recent planned redistribution activity records.
 * 
 * @param {number} limit - Maximum number of recent activities to fetch (1-100)
 * @returns {Promise<Array>} List of activity objects
 */
export async function getRecentActivities(limit = 10) {
  const endpoint = `${API_BASE_URL}/api/dashboard/recent?limit=${encodeURIComponent(limit)}`;
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Failed to load recent activities (HTTP ${response.status})`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to connect to CIBUS-AI Dashboard API.");
    }
    throw error;
  }
}

/**
 * Records a completed or planned surplus redistribution workflow to the activity log.
 * 
 * @param {Object} activityData - Operational details of the workflow
 * @returns {Promise<Object>} Saved activity record
 */
export async function recordActivity(activityData) {
  const endpoint = `${API_BASE_URL}/api/dashboard/activity`;

  const payload = {
    source_name: String(activityData.source_name || 'Central Facility').trim(),
    predicted_surplus_meals: parseFloat(activityData.predicted_surplus_meals || 0),
    allocated_meals: parseFloat(activityData.allocated_meals || 0),
    matched_ngo_count: parseInt(activityData.matched_ngo_count || 0, 10),
    route_stop_count: parseInt(activityData.route_stop_count || 0, 10),
    route_distance_km: parseFloat(activityData.route_distance_km || 0),
    status: String(activityData.status || 'planned').toLowerCase(),
    notes: activityData.notes || null
  };

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errorMessage = `Activity logging failed (HTTP ${response.status})`;
      try {
        const errData = await response.json();
        if (errData.detail) errorMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error("Unable to log activity to CIBUS-AI Dashboard API.");
    }
    throw error;
  }
}



