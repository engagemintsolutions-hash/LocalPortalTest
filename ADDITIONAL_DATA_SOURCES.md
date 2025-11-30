# Additional Data Sources & Questions - Ultra Plan

## 🌊 Unique Data Points to Add (Beyond Standard)

### **Geographic Features** (PostGIS + OpenStreetMap)

#### 1. Distance to Coast/Beach
```
"How important is proximity to the coast?"
Importance: [1 - - - - - - - - - 10] or "Don't care"
Max Distance: [slider: 1-50km]
```
**Data source**:
- UK coastline polygon from OS OpenData
- PostGIS: `ST_Distance(property.location, coastline_geometry)`
- Store: `distance_to_coast_m` in enrichment

#### 2. National Parks & Green Spaces
```
"Proximity to national parks or green spaces?"
Importance: [1-10 slider]
Max Distance: [5km | 10km | 20km | 50km]
```
**Data source**:
- National Parks boundaries (Natural England)
- Parks & green spaces (OS OpenData)
- Calculate: `distance_to_nearest_park_m`

#### 3. River/Water Features
```
"Near river or waterside?"
Importance: [1-10]
Type: [ ] River [ ] Lake [ ] Canal
```
**Data source**:
- OS WaterNetwork data
- PostGIS line/polygon queries

#### 4. Elevation & Views
```
"Prefer elevated properties with views?"
Importance: [1-10]
```
**Data source**:
- OS Terrain 50 (elevation data)
- Store: `elevation_m` (higher = potential views)

---

### **Lifestyle & Amenities** (Google Places API / OpenStreetMap)

#### 5. Golf Courses
```
"Distance to golf course?"
Importance: [1-10] or "Don't care"
Max distance: [2km | 5km | 10km]
```

#### 6. Restaurants & Dining
```
"Vibrant dining scene important?"
Importance: [1-10]
Density: [ ] Michelin star nearby [ ] Variety of cuisines [ ] Pubs/local
```
**Data**: Count POIs within 1km radius

#### 7. Shopping & Retail
```
"Shopping accessibility?"
Importance: [1-10]
Type: [ ] Supermarkets [ ] High street [ ] Shopping centers
```

#### 8. Healthcare
```
"Proximity to healthcare?"
Importance: [1-10]
Type: [ ] GP surgery [ ] Hospital [ ] A&E
```
**Data source**: NHS England API

#### 9. Gyms & Fitness
```
"Fitness facilities nearby?"
Importance: [1-10]
Max distance: [500m | 1km | 2km]
```

---

### **Historical & Cultural** (Historic England / Local Authorities)

#### 10. Historic Sites & Museums
```
"Interest in historic sites nearby?"
Importance: [1-10]
Type: [ ] Museums [ ] Historic buildings [ ] Heritage sites
```

#### 11. Theaters & Arts
```
"Cultural amenities important?"
Importance: [1-10]
[ ] Theaters [ ] Cinemas [ ] Art galleries
```

---

### **Family & Lifestyle** (Gov.uk Data)

#### 12. Childcare & Nurseries
```
"Need childcare facilities?"
Importance: [1-10]
Type: [ ] Nursery [ ] Pre-school [ ] Childminder
```
**Data source**: Ofsted childcare providers

#### 13. Libraries
```
"Public library access?"
Importance: [1-10]
Max distance: [500m | 1km | 2km]
```

#### 14. Sports Facilities
```
"Sports facilities nearby?"
Importance: [1-10]
Type: [ ] Swimming pool [ ] Tennis courts [ ] Football pitches
```

---

### **Transport & Connectivity** (TfL / National Rail)

#### 15. Specific Train Lines
```
"Need specific Underground/rail lines?"
Importance: [1-10]
Lines: [Multi-select: Northern, Central, Elizabeth Line, etc.]
```
**Data source**: TfL API

#### 16. Cycle Routes
```
"Cycle-friendly area?"
Importance: [1-10]
```
**Data source**:
- Cycle infrastructure (Sustrans)
- Calculate nearby cycle paths

#### 17. Bus Routes
```
"Good bus connectivity?"
Importance: [1-10]
Min frequency: [Every 10 mins | 20 mins | 30 mins]
```
**Data source**: TfL/National bus data

---

### **Environmental** (EA / Defra)

#### 18. Air Quality
```
"Air quality important?"
Importance: [1-10]
Minimum: [ ] Good [ ] Fair [ ] Any
```
**Data source**:
- Defra UK Air Quality Index
- Store: `air_quality_index` per postcode

#### 19. Noise Pollution
```
"Low noise pollution?"
Importance: [1-10]
Avoid: [ ] Major roads [ ] Railways [ ] Heathrow flight path
```
**Data source**:
- OS road network (calculate distance to A-roads)
- Heathrow noise contours

#### 20. Green Space Access
```
"Access to parks/green space?"
Importance: [1-10]
Within walking distance: [5 min | 10 min | 20 min]
```

---

### **Property Specifics** (Scraped + Land Registry)

#### 21. Off-Street Parking
```
"Off-street parking essential?"
Importance: [1-10]
Type: [ ] Driveway [ ] Garage [ ] Any
```
**Data**: Keyword match in descriptions

#### 22. Garden/Outdoor Space
```
"Garden requirements?"
Importance: [1-10]
Size: [ ] Any [ ] Small [ ] Medium [ ] Large
```
**Data**: Description keywords + area if available

#### 23. Property Tax (Council Tax)
```
"Maximum council tax band?"
Importance: [1-10]
Max band: [ ] A [ ] B [ ] C [ ] D [ ] E [ ] Any
```
**Data source**: VOA council tax data

#### 24. Lease Length (Leasehold)
```
"If leasehold, minimum years remaining?"
[ ] 80+ [ ] 100+ [ ] 125+ [ ] 999 (virtual freehold)
```

---

## 🎨 UI Pattern: "Importance + Criteria"

### Universal Question Template:
```html
<div class="question-card">
  <h3>Distance to Beach/Coast</h3>

  <!-- Importance Slider -->
  <div class="importance-section">
    <label>How important is this to you?</label>
    <div class="importance-slider">
      <span>Don't care</span>
      <input type="range" min="0" max="10" value="0">
      <span>Essential</span>
    </div>
    <div class="importance-value">
      <span id="importance-beach">Not important</span>
    </div>
  </div>

  <!-- Conditional Criteria (only show if importance > 0) -->
  <div class="criteria-section" style="display: none;">
    <label>Maximum acceptable distance</label>
    <select>
      <option>Within 5km</option>
      <option>Within 10km</option>
      <option>Within 25km</option>
      <option>Within 50km</option>
    </select>
  </div>
</div>
```

### JavaScript Logic:
```javascript
// Show criteria only if user cares
importanceSlider.addEventListener('input', function() {
  const value = parseInt(this.value);

  if (value === 0) {
    criteriaSection.style.display = 'none';
    importanceLabel.textContent = "Not important";
  } else if (value <= 3) {
    criteriaSection.style.display = 'block';
    importanceLabel.textContent = "Somewhat important";
  } else if (value <= 7) {
    criteriaSection.style.display = 'block';
    importanceLabel.textContent = "Important";
  } else {
    criteriaSection.style.display = 'block';
    importanceLabel.textContent = "Very important";
  }

  // Update weighting
  weights.beach_proximity = value / 10;  // 0-1 scale
});
```

---

## 🗺️ Data We Can Easily Add (Free/Open Sources)

### **Geographic (1 week to implement)**
- ✅ Coastline distance (OS Boundary-Line)
- ✅ National parks (Natural England)
- ✅ Rivers/canals (OS WaterNetwork)
- ✅ Elevation (OS Terrain 50)
- ✅ Parks (OS Open Greenspace)

### **Transport (3 days)**
- ✅ TfL Underground lines (TfL API)
- ✅ Bus routes (TfL Open Data)
- ✅ Cycle infrastructure (Sustrans)
- ✅ Specific stations (National Rail)

### **Amenities (Google Places - costs $)**
- ⚠️ Restaurants, shops, gyms (£ per query)
- ⚠️ Alternative: OpenStreetMap (free but less complete)

### **Quality of Life (Gov.uk)**
- ✅ Air quality (Defra API)
- ✅ Noise pollution maps (Defra)
- ✅ Council tax bands (VOA)
- ✅ Childcare (Ofsted)

---

## 📊 Proposed Enhanced Flow (8 Steps)

### **Step 1**: Budget
- Min/max budget

### **Step 2**: Property Basics
- Bedrooms
- Property type
- **NEW**: Minimum bathrooms [1+ | 2+ | 3+]
- **NEW**: Tenure [Any | Freehold only | Leasehold OK]

### **Step 3**: Location
- Postcode areas
- Radius
- Airport proximity

### **Step 4**: Schools & Family (if important)
- **NEW**: Outstanding schools only? [Importance: 1-10]
- **NEW**: Max distance to school [slider: 0-3km]
- **NEW**: Childcare nearby? [Importance: 1-10]

### **Step 5**: Transport & Commute
- **NEW**: Max distance to station [Importance: 1-10] [slider: 0-2km]
- **NEW**: Specific tube lines? [Multi-select] [Importance: 1-10]
- **NEW**: Good bus connectivity? [Importance: 1-10]

### **Step 6**: Area Quality & Safety
- **NEW**: Minimum area quality (IMD) [Importance: 1-10] [slider: decile 1-10]
- **NEW**: Low crime area? [Importance: 1-10] [Below 25th percentile?]
- **NEW**: Flood risk tolerance [Any | Low-Medium OK | Very Low only]

### **Step 7**: Environment & Lifestyle
- **NEW**: Minimum EPC rating [Importance: 1-10] [A | B | C | D | Any]
- **NEW**: Proximity to coast [Importance: 1-10] [slider: 0-50km]
- **NEW**: Near green spaces [Importance: 1-10]
- **NEW**: Broadband speed [Importance: 1-10] [50+ | 100+ | 300+ Mbps]

### **Step 8**: Results
- Ranked by combined importance weights

---

## 💡 Smart Features

### Auto-Skip Logic
```javascript
// If importance = 0, skip detailed criteria
if (importance_schools === 0) {
  skipSchoolDetails();
}
```

### Incompatible Selections Warning
```javascript
// Budget too low for all filters
if (budget_max < 300000 && epc_min === 'A' && outstanding_schools_only) {
  showWarning("Your criteria are very restrictive. Consider relaxing some filters.");
}
```

### Save & Resume
```javascript
// Save to localStorage
localStorage.setItem('questionnaire_progress', JSON.stringify(wizardState));

// "Resume Previous Search" button
```

---

Want me to implement the enhanced 8-step questionnaire with importance sliders and the coastal proximity question now?
