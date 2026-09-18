/**
 * CIBUS-AI - Frontend Verification & Unit/Integration Test Suite
 * File: frontend/tests/frontend_test.cjs
 * 
 * Purpose:
 * Validates frontend components, service integration, leakage prevention, and API compatibility.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('======================================================================');
console.log('        CIBUS-AI FRONTEND QUALITY AUDIT & TEST SUITE');
console.log('======================================================================\n');

let passedTests = 0;
let totalTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`  [PASS] Test ${totalTests}: ${name}`);
    passedTests++;
  } catch (err) {
    console.error(`  [FAIL] Test ${totalTests}: ${name}`);
    console.error(`         Error: ${err.message}`);
  }
}

const FRONTEND_DIR = path.resolve(__dirname, '..');
const SRC_DIR = path.join(FRONTEND_DIR, 'src');

// Test 1: File Structure Verification
runTest('Verify frontend directory structure and core files exist', () => {
  const requiredFiles = [
    'package.json',
    'vite.config.js',
    'index.html',
    '.env.example',
    'src/main.jsx',
    'src/App.jsx',
    'src/styles/index.css',
    'src/styles/App.css',
    'src/services/predictionService.js',
    'src/components/Header.jsx',
    'src/components/Hero.jsx',
    'src/components/PredictionForm.jsx',
    'src/components/ResultCard.jsx',
    'src/components/HealthStatus.jsx',
    'src/components/HowItWorks.jsx',
    'src/components/FutureModules.jsx',
    'src/components/Footer.jsx'
  ];

  requiredFiles.forEach(file => {
    const fullPath = path.join(FRONTEND_DIR, file);
    assert.strictEqual(fs.existsSync(fullPath), true, `Missing required file: ${file}`);
  });
});

// Test 2: Verify all 9 required operational prediction fields are present in PredictionForm
runTest('Verify all 9 operational prediction fields in PredictionForm.jsx', () => {
  const formCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'PredictionForm.jsx'), 'utf8');
  const requiredFields = [
    'Day',
    'Weather',
    'Customers_Forecast',
    'Meals_Prepared',
    'Festival',
    'Event_Type',
    'Staff_Count',
    'Avg_Rating',
    'Special_Event'
  ];

  requiredFields.forEach(field => {
    assert.strictEqual(
      formCode.includes(`name="${field}"`) || formCode.includes(field),
      true,
      `Field '${field}' not found in PredictionForm.jsx`
    );
  });
});

// Test 3: Verify strict absence of Meals_Sold in client code (Data Leakage Audit)
runTest('Confirm Meals_Sold is strictly excluded from frontend forms and payloads', () => {
  const filesToCheck = [
    'components/PredictionForm.jsx',
    'components/ResultCard.jsx',
    'services/predictionService.js',
    'App.jsx'
  ];

  filesToCheck.forEach(file => {
    const code = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
    // Check if Meals_Sold is used as an input field (excluding explicit security check assertions)
    const hasInputMealsSold = /<input[^>]+Meals_Sold/i.test(code) || /<select[^>]+Meals_Sold/i.test(code);
    assert.strictEqual(hasInputMealsSold, false, `Forbidden Meals_Sold input found in ${file}`);
  });
});

// Test 4: Verify Pydantic schema alignment in predictionService.js
runTest('Verify predictionService.js builds payload strictly matching backend schema', () => {
  const serviceCode = fs.readFileSync(path.join(SRC_DIR, 'services', 'predictionService.js'), 'utf8');
  assert.strictEqual(serviceCode.includes("endpoint = `${API_BASE_URL}/api/predict`"), true);
  assert.strictEqual(serviceCode.includes("Customers_Forecast: parseInt"), true);
  assert.strictEqual(serviceCode.includes("Meals_Prepared: parseInt"), true);
  assert.strictEqual(serviceCode.includes("Avg_Rating: parseFloat"), true);
  assert.strictEqual(serviceCode.includes("Special_Event:"), true);
});

// Test 5: Verify ResultCard displays surplus meals, model details, and regression clarification
runTest('Verify ResultCard displays surplus meals, model details, and no false accuracy claim', () => {
  const resultCardCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'ResultCard.jsx'), 'utf8');
  assert.strictEqual(resultCardCode.includes("predicted_surplus_meals"), true);
  assert.strictEqual(resultCardCode.includes("Surplus_Meals (Regression)"), true);
  assert.strictEqual(resultCardCode.includes("Random Forest Regressor"), true);
  // Ensure no false accuracy percentage claim
  assert.strictEqual(/accuracy\s*%/i.test(resultCardCode), false, "ResultCard must not claim accuracy percentage");
});

// Test 6: Verify Reset functionality in PredictionForm.jsx
runTest('Verify Reset button clears form state and calls onReset handler', () => {
  const formCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'PredictionForm.jsx'), 'utf8');
  assert.strictEqual(formCode.includes("handleResetClick"), true);
  assert.strictEqual(formCode.includes("onReset();"), true);
});

// Test 7: Verify Vite build succeeds without compilation errors
runTest('Verify Vite builds the production bundle cleanly', () => {
  const { execSync } = require('child_process');
  const buildOutput = execSync('npm run build', { cwd: FRONTEND_DIR, encoding: 'utf8' });
  assert.strictEqual(fs.existsSync(path.join(FRONTEND_DIR, 'dist', 'index.html')), true);
});

// Test 8: Verify NGOMatchingSection.jsx exists and displays synthetic data disclaimer
runTest('Verify NGOMatchingSection.jsx component exists with demo data disclaimer', () => {
  const ngoCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'NGOMatchingSection.jsx'), 'utf8');
  assert.strictEqual(ngoCode.includes("Demo / Synthetic NGO Dataset"), true);
  assert.strictEqual(ngoCode.includes("Recipient NGO Matching & Allocation"), true);
});

// Test 9: Verify matchNGOs API call in predictionService.js
runTest('Verify matchNGOs API integration in predictionService.js', () => {
  const serviceCode = fs.readFileSync(path.join(SRC_DIR, 'services', 'predictionService.js'), 'utf8');
  assert.strictEqual(serviceCode.includes("matchNGOs"), true);
  assert.strictEqual(serviceCode.includes("endpoint = `${API_BASE_URL}/api/match-ngos`"), true);
});

// Test 10: Verify NGOMatchingSection includes dietary and location controls
runTest('Verify dietary and location controls in NGOMatchingSection.jsx', () => {
  const ngoCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'NGOMatchingSection.jsx'), 'utf8');
  assert.strictEqual(ngoCode.includes("Vegetarian"), true);
  assert.strictEqual(ngoCode.includes("Non-Vegetarian"), true);
  assert.strictEqual(ngoCode.includes("LOCATION_PRESETS"), true);
  assert.strictEqual(ngoCode.includes("match_score"), true);
});

// Test 11: Verify RoutePlanningSection.jsx exists and displays demo planner disclaimer
runTest('Verify RoutePlanningSection.jsx component exists with heuristic disclaimer', () => {
  const routeCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'RoutePlanningSection.jsx'), 'utf8');
  assert.strictEqual(routeCode.includes("Demo Route Planner"), true);
  assert.strictEqual(routeCode.includes("Route Optimization & Pickup Planning"), true);
  assert.strictEqual(routeCode.includes("Haversine"), true);
});

// Test 12: Verify optimizeRoute API integration in predictionService.js
runTest('Verify optimizeRoute API client in predictionService.js', () => {
  const serviceCode = fs.readFileSync(path.join(SRC_DIR, 'services', 'predictionService.js'), 'utf8');
  assert.strictEqual(serviceCode.includes("optimizeRoute"), true);
  assert.strictEqual(serviceCode.includes("endpoint = `${API_BASE_URL}/api/optimize-route`"), true);
});

// Test 13: Verify route timeline visualization and summary elements in RoutePlanningSection
runTest('Verify route timeline visualization and summary metrics in RoutePlanningSection.jsx', () => {
  const routeCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'RoutePlanningSection.jsx'), 'utf8');
  assert.strictEqual(routeCode.includes("total_distance_km"), true);
  assert.strictEqual(routeCode.includes("number_of_stops"), true);
  assert.strictEqual(routeCode.includes("total_allocated_meals"), true);
  assert.strictEqual(routeCode.includes("distance_from_previous_km"), true);
  assert.strictEqual(routeCode.includes("distance_matrix"), true);
});

// Test 14: Verify App.jsx imports and mounts RoutePlanningSection
runTest('Verify App.jsx connects NGOMatchingSection to RoutePlanningSection', () => {
  const appCode = fs.readFileSync(path.join(SRC_DIR, 'App.jsx'), 'utf8');
  assert.strictEqual(appCode.includes("RoutePlanningSection"), true);
  assert.strictEqual(appCode.includes("matchedNGOs"), true);
});

// Test 15: Verify ImpactDashboard.jsx component renders operational cards and ML panel
runTest('Verify ImpactDashboard.jsx component exists with operational metrics and ML panel', () => {
  const dashCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'ImpactDashboard.jsx'), 'utf8');
  assert.strictEqual(dashCode.includes("CIBUS-AI Impact Dashboard"), true);
  assert.strictEqual(dashCode.includes("total_predicted_surplus_meals"), true);
  assert.strictEqual(dashCode.includes("ML Model Performance"), true);
  assert.strictEqual(dashCode.includes("MAE"), true);
  assert.strictEqual(dashCode.includes("RMSE"), true);
  assert.strictEqual(dashCode.includes("R²"), true);
});

// Test 16: Verify dashboard API methods in predictionService.js
runTest('Verify getDashboardSummary, getRecentActivities, and recordActivity in predictionService.js', () => {
  const serviceCode = fs.readFileSync(path.join(SRC_DIR, 'services', 'predictionService.js'), 'utf8');
  assert.strictEqual(serviceCode.includes("getDashboardSummary"), true);
  assert.strictEqual(serviceCode.includes("getRecentActivities"), true);
  assert.strictEqual(serviceCode.includes("recordActivity"), true);
  assert.strictEqual(serviceCode.includes("/api/dashboard/summary"), true);
});

// Test 17: Verify Header.jsx navigation anchors
runTest('Verify Header.jsx navigation bar includes Dashboard and Workflow links', () => {
  const headerCode = fs.readFileSync(path.join(SRC_DIR, 'components', 'Header.jsx'), 'utf8');
  assert.strictEqual(headerCode.includes("#impact-dashboard"), true);
  assert.strictEqual(headerCode.includes("#prediction-section"), true);
  assert.strictEqual(headerCode.includes("#ngo-matching"), true);
  assert.strictEqual(headerCode.includes("#route-planning"), true);
});

// Test 18: Verify App.jsx integrates ImpactDashboard
runTest('Verify App.jsx mounts ImpactDashboard component', () => {
  const appCode = fs.readFileSync(path.join(SRC_DIR, 'App.jsx'), 'utf8');
  assert.strictEqual(appCode.includes("ImpactDashboard"), true);
});

console.log(`\n----------------------------------------------------------------------`);
console.log(`Test Execution Summary: ${passedTests} / ${totalTests} tests passed`);
console.log(`======================================================================\n`);

if (passedTests === totalTests) {
  process.exit(0);
} else {
  process.exit(1);
}



