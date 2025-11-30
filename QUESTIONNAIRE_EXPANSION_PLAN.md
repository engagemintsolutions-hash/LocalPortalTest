# Questionnaire Expansion Ultra-Plan

## Current Questions (5 steps)
1. Budget (min/max)
2. Property (beds, type)
3. Location (postcode, radius, airport)
4. Priorities (6 sliders)
5. Results

## 🎯 Expanded Questionnaire - Leveraging Our Data

Since we have access to rich UK property data (EPC, planning, schools, IMD, flood, etc.), we can ask targeted questions that directly map to our enrichment data.

---

## 📋 New Questions to Add

### **Step 2B: Property Details** (After beds/type)

#### 2B.1 Minimum Bathrooms
```
"How many bathrooms do you need?"
[ ] Any  [ ] 1+  [ ] 2+  [ ] 3+  [ ] 4+
```
**Maps to**: `listings_enriched.bathrooms`

#### 2B.2 Outdoor Space
```
"Do you need outdoor space?"
[ ] Not important
[ ] Balcony/Terrace preferred
[ ] Garden essential
```
**Maps to**: Property descriptions (keyword search: "garden", "terrace", "patio")

#### 2B.3 Parking
```
"Parking requirements?"
[ ] Not needed
[ ] Street parking OK
[ ] Off-street parking required
[ ] Garage essential
```
**Maps to**: Property descriptions (keyword: "parking", "garage")

---

### **Step 3B: Location Lifestyle** (After basic location)

#### 3B.1 Proximity to Outstanding Schools
```
"How important is proximity to Outstanding-rated schools?"
[slider: 0-5km or "Not important"]
```
**Maps to**:
- `schools.ofsted_rating = 'outstanding'`
- Calculate distance with PostGIS
- Filter: `distance_to_nearest_primary_m <= value`

#### 3B.2 Commute Requirements
```
"Do you commute to work?"
( ) No
( ) Yes - within walking distance of station (< 800m)
( ) Yes - within reasonable distance (< 2km)
```
**Maps to**: `distance_to_nearest_station_m`

#### 3B.3 Near Specific Amenities
```
"What amenities matter to you?" (multi-select)
[ ] Supermarkets nearby
[ ] Parks & green spaces
[ ] Restaurants & cafes
[ ] Gyms & fitness centers
```
**Maps to**: Future enhancement - POI data from Google Places API

---

### **Step 4B: Property Condition & Features**

#### 4B.1 Energy Performance (EPC)
```
"Minimum energy performance certificate?"
Dropdown: [ A | B | C | D | E | F | G | Any ]
```
**Maps to**: `epc_rating`, already implemented as filter

#### 4B.2 New Build vs Period
```
"Property age preference?"
[ ] Any
[ ] Modern (< 20 years)
[ ] Period properties (character features)
```
**Maps to**: Property descriptions or build date if available

#### 4B.3 Condition
```
"Preferred property condition?"
[ ] Move-in ready
[ ] Light renovation OK
[ ] Project/renovation opportunity
```
**Maps to**: Keywords in description: "refurbished", "modernised", "requires updating"

---

### **Step 5: Area Quality & Safety**

#### 5.1 Deprivation Index (IMD)
```
"Area quality preferences?"
[slider with visual labels]
< - - - - - - - - - - >
Any    Good    Excellent
```
**Maps to**: `imd_decile` (7-10 = excellent, 4-6 = good)

#### 5.2 Crime Concerns
```
"How important is low crime?"
( ) Not a priority
( ) Moderately important (below 50th percentile)
( ) Very important (below 25th percentile)
```
**Maps to**: `crime_rate_percentile <= threshold`

#### 5.3 Flood Risk Tolerance
```
"Flood risk tolerance?"
[ ] Accept any level (don't filter)
[ ] Low to Medium OK
[ ] Only Very Low risk
```
**Maps to**: `exclude_flood_risk = ['high', 'medium']`

---

### **Step 6: Planning & Legal**

#### 6.1 Conservation Areas
```
"Conservation area preference?"
( ) No preference
( ) Prefer conservation areas
( ) Avoid conservation areas (planning freedom)
```
**Maps to**:
- Prefer: `in_conservation_area = true` (boost score)
- Avoid: `in_conservation_area = false` (filter)

#### 6.2 Planning History
```
"Comfortable with recent planning activity?"
( ) Yes - no concerns
( ) Prefer properties with no recent applications
```
**Maps to**: `recent_planning_apps = 0`

#### 6.3 Listed Buildings
```
"Interested in listed buildings?"
( ) Yes
( ) No preference
( ) No - avoid listed status
```
**Maps to**: `planning_constraints.listed_building`

---

### **Step 7: Investment vs Living**

#### 7.1 Purpose
```
"What's your main goal?"
( ) Primary residence - family home
( ) Investment property - rental income
( ) Second home - holiday/weekend
```
**Maps to**:
- Investment → Prioritize `avm_value_delta_pct` (undervalued)
- Primary → Prioritize schools, safety, commute

#### 7.2 Tenure Preference
```
"Tenure preference?"
( ) Any
( ) Freehold only
( ) Leasehold acceptable
```
**Maps to**: `tenure = 'freehold'` filter

#### 7.3 Value Priority
```
"Are you looking for undervalued properties?"
[slider: 0% (don't care) - 100% (only show bargains)]
```
**Maps to**: Weight for `is_undervalued` flag

---

### **Step 8: Connectivity & Modern Amenities**

#### 8.1 Broadband Speed
```
"Internet speed requirements?"
( ) Not important
( ) Standard (50+ Mbps)
( ) Fast (100+ Mbps)
( ) Ultrafast (300+ Mbps)
```
**Maps to**: `max_download_speed_mbps >= threshold`

#### 8.2 Mobile Coverage
```
"Mobile coverage important?"
( ) Not a priority
( ) Yes - good coverage essential
```
**Maps to**: Future - mobile coverage data from Ofcom

---

## 📊 Recommended Question Flow (Expanded)

### **Short Version** (5 steps - current):
Budget → Property → Location → Priorities → Results

### **Standard Version** (7 steps):
1. Budget
2. Property Basics (beds, type, baths)
3. Location (postcode, radius, transport)
4. Priorities (sliders)
5. Area Quality (IMD, crime, flood)
6. **NEW**: Property Features (EPC, condition, age)
7. Results

### **Comprehensive Version** (10 steps):
1. Budget
2. Property Basics
3. Location
4. Schools & Education
5. Transport & Commute
6. Area Quality & Safety
7. Energy & Sustainability
8. Value & Investment
9. Planning & Legal
10. Results

---

## 🎨 UI/UX Recommendations

### Progressive Disclosure
```
Start: 5 essential questions
↓
"Want more control?" button
↓
Expand to 10 detailed questions
```

### Question Types to Use

**Multiple Choice** (exclusive):
```html
<div class="radio-group">
  <label class="radio-card">
    <input type="radio" name="question">
    <span>Option 1</span>
  </label>
</div>
```

**Multi-Select** (inclusive):
```html
<div class="checkbox-group">
  <label class="checkbox-card">
    <input type="checkbox">
    <span>Feature A</span>
  </label>
</div>
```

**Range with Labels**:
```html
<div class="range-with-labels">
  <span>Not important</span>
  <input type="range">
  <span>Essential</span>
</div>
```

**Yes/No Toggle**:
```html
<div class="toggle-switch">
  <input type="checkbox" id="x">
  <label for="x">
    <span>No</span>
    <span>Yes</span>
  </label>
</div>
```

---

## 🔄 Smart Question Logic

### Conditional Questions (Show/Hide)

```javascript
// If user selects "Yes" to commute
if (userCommutes) {
  showQuestion("How far from station?");
  showQuestion("Which stations/lines?");
}

// If user prioritizes schools
if (prioritySchools > 50) {
  showQuestion("Primary or secondary school age?");
  showQuestion("Specific school catchment areas?");
}

// If investment property
if (purpose === 'investment') {
  hideQuestion("School proximity");  // Not relevant
  showQuestion("Rental yield estimates");
}
```

### Question Skip Logic
```javascript
// "Not sure" option on complex questions
if (userSelectsNotSure) {
  skipToNextStep();
  useDefaultWeights();
}
```

---

## 💡 Data-Driven Question Design

### Match Questions to Available Data

**We HAVE data for**:
✅ EPC rating/score
✅ Schools (distance, Ofsted rating)
✅ Stations (distance)
✅ Airports (distance, code)
✅ Conservation areas
✅ IMD decile
✅ Crime percentile
✅ Flood risk
✅ Broadband speed
✅ Planning apps count
✅ AVM valuation
✅ Tenure

**We DON'T have** (skip or future):
❌ Specific room counts (dining room, study, etc.)
❌ Garden size (sqft)
❌ Year built
❌ Council tax band (could add)
❌ Service charges (leasehold)

---

## 🎯 Recommended Implementation

### Phase 1: Add 2 High-Impact Questions (15 mins)
1. **Minimum EPC rating** (Step 3 or 4)
2. **Flood risk exclusion** (Step 5 - Area Quality)

### Phase 2: Add Schools Deep-Dive (30 mins)
- Do you have school-age children?
- Primary or secondary?
- Only Outstanding rated?
- Max distance to school?

### Phase 3: Add Investment Questions (30 mins)
- Purpose: Living vs Investment
- Tenure preference
- Value importance (undervalued filter)

### Phase 4: Full Expansion (2 hours)
- All 10-step comprehensive version
- Conditional logic
- "Quick" vs "Detailed" mode toggle

---

## 📐 Suggested Priority Order

### **Must-Have** (add now):
1. ✅ Minimum bathrooms
2. ✅ Minimum EPC rating (already in schema, just add UI)
3. ✅ Flood risk exclusions (already in schema, add UI)
4. ✅ Tenure preference (freehold/leasehold)

### **Should-Have** (add next):
5. ⏳ School proximity (if children)
6. ⏳ Commute distance from station
7. ⏳ Purpose (living vs investment)

### **Nice-to-Have** (polish):
8. ⏳ Broadband speed minimum
9. ⏳ IMD quality slider
10. ⏳ Planning history concerns

---

## 🚀 Quick Win Implementation

Want me to add **4 new high-impact questions** right now?

1. **Minimum bathrooms** (Step 2)
2. **Tenure preference** (Step 2)
3. **Minimum EPC** (Step 4 or new Step 5)
4. **Flood risk** (new Step 5)

These map directly to our existing data and add significant value!

Should I implement these 4 questions now?
