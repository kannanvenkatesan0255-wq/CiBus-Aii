import React, { useState } from 'react';

const INITIAL_STATE = {
  Day: '',
  Weather: '',
  Customers_Forecast: '',
  Meals_Prepared: '',
  Festival: '',
  Event_Type: '',
  Staff_Count: '',
  Avg_Rating: '',
  Special_Event: ''
};

export default function PredictionForm({ onSubmit, isLoading, onReset }) {
  const [formData, setFormData] = useState(INITIAL_STATE);
  const [clientError, setClientError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setClientError('');
  };

  const handleResetClick = () => {
    setFormData(INITIAL_STATE);
    setClientError('');
    if (onReset) {
      onReset();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Check that user has explicitly provided all manual values
    if (!formData.Day) {
      setClientError('Please select a Day of the week.');
      return;
    }

    if (!formData.Weather) {
      setClientError('Please select a Weather condition.');
      return;
    }

    if (formData.Customers_Forecast === '' || formData.Customers_Forecast === null) {
      setClientError('Please enter Customers Forecast.');
      return;
    }

    if (formData.Meals_Prepared === '' || formData.Meals_Prepared === null) {
      setClientError('Please enter Meals Prepared count.');
      return;
    }

    if (!formData.Event_Type) {
      setClientError('Please select an Event Type.');
      return;
    }

    if (!formData.Festival) {
      setClientError('Please select a Festival/Holiday option (select "No Holiday" if regular).');
      return;
    }

    if (formData.Staff_Count === '' || formData.Staff_Count === null) {
      setClientError('Please enter Staff Count.');
      return;
    }

    if (formData.Avg_Rating === '' || formData.Avg_Rating === null) {
      setClientError('Please enter Average Rating (between 1.0 and 5.0).');
      return;
    }

    if (formData.Special_Event === '' || formData.Special_Event === null) {
      setClientError('Please select Special Event indicator (0 or 1).');
      return;
    }

    const customers = Number(formData.Customers_Forecast);
    const meals = Number(formData.Meals_Prepared);
    const staff = Number(formData.Staff_Count);
    const rating = Number(formData.Avg_Rating);

    if (isNaN(customers) || customers < 0) {
      setClientError('Customers Forecast must be a non-negative number (0 or higher).');
      return;
    }

    if (isNaN(meals) || meals < 0) {
      setClientError('Meals Prepared must be a non-negative number (0 or higher).');
      return;
    }

    if (isNaN(staff) || staff < 1) {
      setClientError('Staff Count must be at least 1.');
      return;
    }

    if (isNaN(rating) || rating < 1.0 || rating > 5.0) {
      setClientError('Average Rating must be between 1.0 and 5.0.');
      return;
    }

    onSubmit(formData);
  };

  return (
    <div className="glass-card">
      <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 className="card-title">
            <span>📋</span> Operational Input Parameters
          </h2>
          <p className="card-subtitle">
            Enter pre-service operational metrics manually to calculate surplus forecast
          </p>
        </div>
        <button
          id="btn-reset-top"
          type="button"
          className="btn btn-secondary"
          onClick={handleResetClick}
          disabled={isLoading}
          style={{ fontSize: '0.85rem', padding: '0.45rem 1rem', display: 'flex', alignItems: 'center', gap: '0.45rem' }}
          title="Reset all values to initial blank state"
        >
          <span>🔄</span> Reset Values
        </button>
      </div>

      {clientError && (
        <div className="alert-error" role="alert">
          ⚠️ {clientError}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Day */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-day">
              Day of Week
            </label>
            <select
              id="field-day"
              name="Day"
              className="form-control"
              value={formData.Day}
              onChange={handleChange}
              disabled={isLoading}
              required
            >
              <option value="">-- Select Day (None) --</option>
              <option value="Monday">Monday</option>
              <option value="Tuesday">Tuesday</option>
              <option value="Wednesday">Wednesday</option>
              <option value="Thursday">Thursday</option>
              <option value="Friday">Friday</option>
              <option value="Saturday">Saturday</option>
              <option value="Sunday">Sunday</option>
            </select>
          </div>

          {/* Weather */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-weather">
              Weather Condition
            </label>
            <select
              id="field-weather"
              name="Weather"
              className="form-control"
              value={formData.Weather}
              onChange={handleChange}
              disabled={isLoading}
              required
            >
              <option value="">-- Select Weather (None) --</option>
              <option value="Sunny">Sunny</option>
              <option value="Cloudy">Cloudy</option>
              <option value="Rainy">Rainy</option>
              <option value="Stormy">Stormy</option>
            </select>
          </div>

          {/* Customers Forecast */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-customers">
              Customers Forecast <span className="helper-tag">(Expected footfall)</span>
            </label>
            <input
              id="field-customers"
              type="number"
              name="Customers_Forecast"
              className="form-control"
              placeholder="e.g. 0"
              min="0"
              value={formData.Customers_Forecast}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          {/* Meals Prepared */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-meals">
              Meals Prepared <span className="helper-tag">(Batch cook count)</span>
            </label>
            <input
              id="field-meals"
              type="number"
              name="Meals_Prepared"
              className="form-control"
              placeholder="e.g. 0"
              min="0"
              value={formData.Meals_Prepared}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          {/* Event Type */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-event">
              Event Type
            </label>
            <select
              id="field-event"
              name="Event_Type"
              className="form-control"
              value={formData.Event_Type}
              onChange={handleChange}
              disabled={isLoading}
              required
            >
              <option value="">-- Select Event Type (None) --</option>
              <option value="Regular">Regular Dining</option>
              <option value="Buffet">Buffet Service</option>
              <option value="Corporate">Corporate Gathering</option>
              <option value="Banquet">Banquet Hall Function</option>
            </select>
          </div>

          {/* Festival */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-festival">
              Holiday / Festival
            </label>
            <select
              id="field-festival"
              name="Festival"
              className="form-control"
              value={formData.Festival}
              onChange={handleChange}
              disabled={isLoading}
              required
            >
              <option value="">-- Select Festival / Holiday (None) --</option>
              <option value="No">No Holiday (None)</option>
              <option value="Diwali">Diwali</option>
              <option value="Eid">Eid</option>
              <option value="Christmas">Christmas</option>
              <option value="New Year">New Year</option>
            </select>
          </div>

          {/* Staff Count */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-staff">
              Staff Count <span className="helper-tag">(Kitchen & floor)</span>
            </label>
            <input
              id="field-staff"
              type="number"
              name="Staff_Count"
              className="form-control"
              placeholder="e.g. 1"
              min="1"
              value={formData.Staff_Count}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          {/* Average Rating */}
          <div className="form-group">
            <label className="form-label" htmlFor="field-rating">
              Average Rating <span className="helper-tag">(1.0 - 5.0)</span>
            </label>
            <input
              id="field-rating"
              type="number"
              step="0.1"
              name="Avg_Rating"
              className="form-control"
              placeholder="e.g. 4.0"
              min="1.0"
              max="5.0"
              value={formData.Avg_Rating}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
          </div>

          {/* Special Event Flag */}
          <div className="form-group full-width">
            <label className="form-label" htmlFor="field-special">
              Special Event Indicator
            </label>
            <select
              id="field-special"
              name="Special_Event"
              className="form-control"
              value={formData.Special_Event}
              onChange={handleChange}
              disabled={isLoading}
              required
            >
              <option value="">-- Select Special Event (None) --</option>
              <option value="0">0 - Standard Shift (No Special Event)</option>
              <option value="1">1 - Special Event / VIP Booking</option>
            </select>
          </div>

          {/* Form Action Buttons */}
          <div className="form-actions">
            <button
              id="btn-predict"
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span>⏳</span> Forecasting Surplus...
                </>
              ) : (
                <>
                  <span>⚡</span> Predict Surplus Meals
                </>
              )}
            </button>

            <button
              id="btn-reset"
              type="button"
              className="btn btn-secondary"
              onClick={handleResetClick}
              disabled={isLoading}
            >
              Reset Values
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
