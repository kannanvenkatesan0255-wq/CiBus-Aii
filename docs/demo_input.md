# Verified Synthetic Demo Input Payloads

**Project:** CIBUS-AI – AI-Based Food Surplus Prediction and Redistribution Network  
**Tagline:** *Predict. Connect. Nourish.*  

---

> [!NOTE]
> All inputs below are synthetic test scenarios designed to demonstrate distinct operational edge cases in CIBUS-AI. No personal or real restaurant data is used.

---

## Scenario A: Standard Weekend Banquet (Moderate Surplus)

- **Purpose:** Demonstrate standard operational prediction, balanced capacity allocation across 2 NGOs, and multi-stop route planning.
- **Input Parameters:**
  - **Day:** `Saturday`
  - **Weather:** `Rainy`
  - **Customers Forecast:** `280`
  - **Meals Prepared:** `350`
  - **Festival:** `No (0)`
  - **Event Type:** `Wedding`
  - **Staff Count:** `12`
  - **Average Rating:** `4.5`
  - **Special Event:** `Yes (1)`
- **Donor Location:** Latitude `12.9716`, Longitude `77.5946` (City Center)
- **Expected Prediction:** ~`65 - 75 meals` surplus.
- **Expected Matching:** Allocates to *Hope Shelter Home* and *City Food Mission*.
- **Expected Route:** 2 NGO stops, ~`8.4 km`, ~`21 minutes`.

---

## Scenario B: Sunny Weekday Corporate Lunch (Low Surplus)

- **Purpose:** Demonstrate low-surplus handling where a single nearby NGO absorbs the entire surplus quantity.
- **Input Parameters:**
  - **Day:** `Wednesday`
  - **Weather:** `Sunny`
  - **Customers Forecast:** `190`
  - **Meals Prepared:** `200`
  - **Festival:** `No (0)`
  - **Event Type:** `Corporate`
  - **Staff Count:** `8`
  - **Average Rating:** `4.8`
  - **Special Event:** `No (0)`
- **Donor Location:** Latitude `12.9716`, Longitude `77.5946`
- **Expected Prediction:** ~`15 - 25 meals` surplus.
- **Expected Matching:** Single NGO allocation (e.g., *Hope Shelter Home*).
- **Expected Route:** 1 NGO stop, ~`3.2 km`, ~`12 minutes`.

---

## Scenario C: Bad Weather Weekend Event (High Surplus)

- **Purpose:** Demonstrate high-surplus distribution across 3+ NGOs and multi-waypoint route trajectory plotting.
- **Input Parameters:**
  - **Day:** `Sunday`
  - **Weather:** `Stormy`
  - **Customers Forecast:** `150`
  - **Meals Prepared:** `320`
  - **Festival:** `No (0)`
  - **Event Type:** `Corporate`
  - **Staff Count:** `10`
  - **Average Rating:** `4.0`
  - **Special Event:** `No (0)`
- **Donor Location:** Latitude `12.9716`, Longitude `77.5946`
- **Expected Prediction:** ~`130 - 150 meals` surplus.
- **Expected Matching:** Multi-NGO greedy distribution across 3+ recipient organizations.
- **Expected Route:** 3-stop trajectory, ~`14.6 km`, ~`38 minutes`.

---

## JSON API Payload (For cURL / Swagger UI Testing)

```json
{
  "Day": "Saturday",
  "Weather": "Rainy",
  "Customers_Forecast": 280,
  "Meals_Prepared": 350,
  "Festival": 0,
  "Event_Type": "Wedding",
  "Staff_Count": 12,
  "Avg_Rating": 4.5,
  "Special_Event": 1
}
```
