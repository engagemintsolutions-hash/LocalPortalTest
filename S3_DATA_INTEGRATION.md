# S3 Data Integration - Connect Real UK Property Data

## 🗄️ Your S3 Data Sources (Assumed Structure)

Based on your mention of "all UK property data on S3", you likely have:

```
s3://your-bucket/
├── epc/                      # Energy Performance Certificates
│   └── *.parquet            # uprn, current_energy_rating, current_energy_efficiency, etc.
├── imd/                      # Index of Multiple Deprivation
│   └── *.parquet            # postcode, imd_decile, crime_score, crime_percentile, etc.
├── planning/                 # Planning Applications
│   └── *.parquet            # uprn, application_id, decision, application_date, etc.
├── flood/                    # Flood Risk
│   └── *.parquet            # uprn/postcode, flood_risk_level
├── broadband/                # Broadband Availability
│   └── *.parquet            # postcode, max_download_speed_mbps
├── schools/                  # Schools Data
│   └── *.parquet            # urn, name, ofsted_rating, lat, lon, postcode
├── conservation-areas/       # Conservation Areas
│   └── *.parquet            # name, local_authority, boundary_geojson
├── land-registry/            # Price Paid Data
│   └── *.parquet            # address, price, date, property_type
├── council-tax/              # Council Tax Bands
│   └── *.parquet            # address, band
└── additional/               # Other datasets
    ├── airports.parquet
    ├── stations.parquet
    ├── coastline.geojson
    ├── parks.parquet
    └── demographic-census.parquet
```

---

## 🔗 New Questions Mapped to S3 Data

### **1. EPC-Specific Questions** (epc/*.parquet)

#### Q: Energy Performance Details
```
"What energy efficiency do you need?"
Importance: [1-10]

If important:
- Minimum EPC rating: [A|B|C|D|E]
- Minimum EPC score: [slider: 50-100]
- Maximum CO2 emissions: [slider]
- Potential for improvement: [Show properties with A potential even if current is C]
```

**S3 Query**:
```sql
SELECT uprn, current_energy_rating, current_energy_efficiency,
       potential_energy_rating, co2_emissions_current
FROM epc_data
WHERE current_energy_efficiency >= {min_score}
```

**Questionnaire Integration**:
```python
# In enrichment
epc_data = duckdb.execute("""
    SELECT * FROM read_parquet('s3://bucket/epc/*.parquet')
    WHERE uprn = {property_uprn}
""").fetchone()

# Match to listing
listing.epc_rating = epc_data.current_energy_rating
listing.epc_score = epc_data.current_energy_efficiency
listing.epc_co2 = epc_data.co2_emissions_current
```

---

### **2. Deprivation & Inequality** (imd/*.parquet)

#### Q: Income Deprivation
```
"Area income levels important?"
Importance: [1-10]

Criteria:
- Income deprivation score: [Low|Medium|High]
- Employment score: [filter unemployed areas]
```

**S3 Fields**:
```python
imd_data:
  - imd_score (overall 0-100, lower = better)
  - imd_decile (1-10, higher = better)
  - income_score
  - employment_score
  - education_score
  - health_score
  - crime_score
  - barriers_to_housing_score
```

**New Questions**:
- "Prefer areas with high employment?" → `employment_score`
- "Education quality (GCSE results)?" → `education_score`
- "Local health services?" → `health_score`

---

### **3. Planning History Deep-Dive** (planning/*.parquet)

#### Q: Planning Application Concerns
```
"Planning history important?"
Importance: [1-10]

Filters:
- [ ] Avoid recent refusals (last 2 years)
- [ ] Avoid properties with enforcement notices
- [ ] Prefer properties with approved extensions
- [ ] Avoid areas with major developments planned
```

**S3 Query**:
```sql
SELECT uprn,
       COUNT(*) as total_apps,
       SUM(CASE WHEN decision = 'Refused' THEN 1 ELSE 0 END) as refusals,
       SUM(CASE WHEN application_type LIKE '%extension%' THEN 1 ELSE 0 END) as extensions
FROM planning_apps
WHERE application_date >= CURRENT_DATE - INTERVAL '5 years'
GROUP BY uprn
```

**Questionnaire**:
- "Avoid recent planning refusals?" [Yes/No]
- "Properties with extension potential?" [Importance 1-10]
- "Avoid nearby large developments?" [Yes/No]

---

### **4. Flood Risk Granular** (flood/*.parquet)

#### Q: Detailed Flood Assessment
```
"Flood concerns?"
Importance: [1-10]

Types:
- [ ] Rivers
- [ ] Surface water
- [ ] Coastal
- [ ] Groundwater

Risk tolerance:
- Very Low only
- Low acceptable
- Medium acceptable (with insurance)
```

**S3 Fields**:
```python
flood_data:
  - flood_risk_rivers (very_low/low/medium/high)
  - flood_risk_surface_water
  - flood_risk_coastal
  - in_flood_zone_2
  - in_flood_zone_3
```

**Questions**:
- "Acceptable river flood risk?" [dropdown]
- "Surface water flooding concerns?" [Yes/No]
- "Coastal properties only?" [filter coastal areas]

---

### **5. Schools Detailed** (schools/*.parquet)

#### Q: School-Specific Needs
```
"School requirements?"

1. School age children?
   [ ] None
   [ ] Primary age (4-11)
   [ ] Secondary age (11-18)
   [ ] Both

2. Ofsted rating minimum:
   [ ] Any
   [ ] Good or better
   [ ] Outstanding only

3. School type:
   [ ] State schools
   [ ] Grammar schools
   [ ] Faith schools (specify: [ ] CoE [ ] Catholic)

4. Max distance: [slider: 0-3km]
```

**S3 Query**:
```sql
-- Find Outstanding primary schools within 1km
SELECT urn, name, ofsted_rating, phase,
       ST_Distance(location, property_location) as distance_m
FROM schools
WHERE phase = 'primary'
  AND ofsted_rating = 'Outstanding'
  AND ST_DWithin(location, property_location, 1000)
ORDER BY distance_m
```

**Questions**:
- "Specific school catchment?" [text input: school name]
- "Grammar school access?" [Importance 1-10]
- "Faith school nearby?" [Denomination dropdown]

---

### **6. Transport & Stations** (stations/*.parquet)

#### Q: Specific Transport Needs
```
"Transport requirements?"

1. Tube/Rail lines needed:
   [ ] Elizabeth Line
   [ ] Northern Line
   [ ] Central Line
   [ ] Overground
   [ ] National Rail to {destination}

2. Max walk to station:
   [ ] 5 min (400m)
   [ ] 10 min (800m)
   [ ] 15 min (1.2km)

3. Station facilities:
   [ ] Step-free access essential
   [ ] Park & Ride
```

**S3 Fields**:
```python
stations:
  - station_name
  - lines (array: ['Elizabeth', 'Central'])
  - step_free_access (boolean)
  - parking_spaces
  - lat, lon
```

**Query**:
```sql
-- Properties near Elizabeth Line stations
SELECT p.uprn, s.station_name,
       ST_Distance(p.location, s.location) as dist_m
FROM properties p
CROSS JOIN stations s
WHERE 'Elizabeth' = ANY(s.lines)
  AND ST_DWithin(p.location, s.location, 800)
```

---

### **7. Price History** (land-registry/*.parquet)

#### Q: Price Trend Preferences
```
"Price history important?"
Importance: [1-10]

Criteria:
- [ ] Show only properties with recent price growth
- [ ] Avoid properties sold multiple times (flipped)
- [ ] Prefer long-term owners (stable area)
```

**S3 Query**:
```sql
-- Get price history for property
SELECT address, price, date, property_type
FROM price_paid
WHERE postcode = {property_postcode}
  AND address LIKE '%{street}%'
ORDER BY date DESC
```

**Calculate**:
- Years since last sale
- Price appreciation %
- Number of previous sales

**Questions**:
- "Avoid recently flipped properties?" [Yes/No]
- "Prefer stable areas (low turnover)?" [Importance 1-10]

---

### **8. Council Tax** (council-tax/*.parquet)

#### Q: Running Costs
```
"Maximum council tax band?"
Importance: [1-10]

Max band: [A|B|C|D|E|F|G|H]

Note: "Band D in this area = £2,100/year"
```

**S3 Query**:
```sql
SELECT band, annual_charge
FROM council_tax
WHERE address = {property_address}
```

**Questions**:
- "Maximum annual council tax?" [£1500|£2000|£2500|£3000+]
- "Show estimated annual bills?" [Yes - add to report]

---

### **9. Coastal Proximity** (coastline.geojson)

#### Q: Seaside Living
```
"Coastal proximity?"
Importance: [1-10]

Type:
- [ ] Beach access (sandy)
- [ ] Clifftop/sea views
- [ ] Marina/harbour
- [ ] Coastal path access

Max distance: [5km|10km|25km|50km]
```

**S3 Calculation**:
```python
# Load UK coastline from S3
coastline = gpd.read_file('s3://bucket/coastline.geojson')

# Calculate distance
from shapely.geometry import Point
property_point = Point(lon, lat)
distance_to_coast = coastline.distance(property_point).min()
```

**Questions**:
- "Seafront properties only?" [Yes/No]
- "Coastal town preferred?" [Importance 1-10]
- "Type of coast?" [Sandy beach | Cliffs | Estuary]

---

### **10. Parks & Green Spaces** (parks/*.parquet)

#### Q: Access to Nature
```
"Green space access?"
Importance: [1-10]

Type:
- [ ] Local park (< 500m)
- [ ] Large park/common (< 1km)
- [ ] National Park nearby (< 10km)
- [ ] Woodland walks

Area: Minimum park size [1 hectare | 10 hectares | 50+ hectares]
```

**S3 Query**:
```sql
SELECT park_name, size_hectares, type,
       ST_Distance(park_location, property_location) as distance_m
FROM parks
WHERE ST_DWithin(park_location, property_location, 1000)
ORDER BY distance_m
LIMIT 5
```

---

### **11. Demographics** (census/*.parquet)

#### Q: Neighborhood Demographics
```
"Neighborhood vibe?"

Age profile:
- [ ] Young professionals (25-35)
- [ ] Families (30-50)
- [ ] Retirees (65+)
- [ ] Diverse/mixed

Average household income:
- [ ] Above UK average
- [ ] Any

Education level:
- [ ] High % university educated
- [ ] Any
```

**S3 Fields** (Census data):
```python
- avg_age
- pct_families
- pct_65_plus
- avg_household_income
- pct_degree_educated
- pct_homeowners vs renters
```

---

### **12. Airports & Flight Paths** (airports/*.parquet)

#### Q: Aviation Impact
```
"Airport considerations?"

Noise:
- [ ] Avoid Heathrow flight paths
- [ ] Avoid low-altitude zones
- Importance: [1-10]

Access:
- Need airport proximity
- Which airport: [LHR|LGW|STN|MAN|etc]
- Max distance: [slider]
```

**S3 Data**:
```python
# Heathrow noise contours (publicly available)
noise_zones = load_geojson('s3://bucket/heathrow-noise-contours.geojson')

# Check if property in noise zone
is_noisy = property_point.within(noise_zones['55dB+'])
```

---

## 🎯 **Expanded Questionnaire with Real S3 Data**

### **New Steps to Add:**

**Step 8: Price & Value** (land-registry data)
- Historical price trends
- Recent sales nearby
- Avoid flipped properties
- Prefer stable areas

**Step 9: Running Costs** (council-tax + EPC)
- Maximum council tax band
- Energy bills estimate (from EPC)
- Service charges (leasehold)

**Step 10: Detailed Environment** (multiple S3 sources)
- Specific flood types (river/surface/coastal)
- Air quality index
- Noise pollution (roads, airports, railways)
- Light pollution

**Step 11: Lifestyle & Amenities** (POI data if available)
- Parks & green space size
- Beach/coast type
- Specific demographics
- Local facilities

**Step 12: Investment Criteria** (land-registry + AVM)
- Rental yield estimates
- Capital appreciation potential
- Market liquidity (time to sell)
- Development potential

---

## 📋 Implementation Priority

### **Phase 1: EPC Deep Dive** (You definitely have this)
```python
# Connect to S3
duckdb.execute("""
    CREATE VIEW epc_enriched AS
    SELECT
        uprn,
        current_energy_rating,
        current_energy_efficiency,
        potential_energy_rating,
        co2_emissions_current,
        co2_emissions_potential,
        lighting_cost_current,
        heating_cost_current,
        hot_water_cost_current
    FROM read_parquet('s3://your-bucket/epc/*.parquet')
""")

# Use in questionnaire
epc = get_epc_data(property_uprn)
annual_energy_cost = epc.lighting_cost + epc.heating_cost + epc.hot_water_cost

# New question
"Maximum annual energy bills?"
[£500|£1000|£1500|£2000+]
```

### **Phase 2: IMD Breakdown** (You have this)
```python
# Instead of just overall decile, show components
imd_components = {
    'income': imd.income_score,
    'employment': imd.employment_score,
    'education': imd.education_score,
    'health': imd.health_score,
    'crime': imd.crime_score,
    'barriers_housing': imd.barriers_to_housing_score,
    'environment': imd.living_environment_score
}

# New questions
"Employment opportunities in area?" [Importance 1-10]
"Education quality (GCSE results)?" [Importance 1-10]
"Access to healthcare?" [Importance 1-10]
```

### **Phase 3: Planning Deep Data** (You have this)
```python
# Extract from planning apps
planning_insights = {
    'extensions_approved': count(where type = 'extension' and decision = 'approved'),
    'loft_conversions': count(where type LIKE '%loft%'),
    'change_of_use': count(where type = 'change of use'),
    'enforcement_actions': count(where type = 'enforcement'),
    'nearby_major_developments': count(where type = 'major' and distance < 500m)
}

# New questions
"Extension potential important?" [Importance 1-10]
"Avoid areas with large developments nearby?" [Yes/No]
"Avoid enforcement issues?" [Yes/No]
```

---

## 🔧 **Quick Implementation Script**

```python
# File: enrichment/s3_enricher_real.py

import duckdb
import os

class RealS3Enricher:
    """Use YOUR actual S3 data for enrichment"""

    def __init__(self, s3_bucket: str):
        self.bucket = s3_bucket
        self.conn = duckdb.connect()

        # Configure S3
        self.conn.execute("INSTALL httpfs;")
        self.conn.execute("LOAD httpfs;")
        self.conn.execute(f"SET s3_region='eu-west-2';")

        # Create views
        self._create_views()

    def _create_views(self):
        """Create views over YOUR S3 data"""

        # EPC
        self.conn.execute(f"""
            CREATE VIEW epc AS
            SELECT * FROM read_parquet('s3://{self.bucket}/epc/*.parquet')
        """)

        # IMD - ALL components
        self.conn.execute(f"""
            CREATE VIEW imd_detailed AS
            SELECT
                postcode,
                imd_score,
                imd_decile,
                income_score,
                employment_score,
                education_score,
                health_score,
                crime_score,
                barriers_to_housing_score,
                living_environment_score
            FROM read_parquet('s3://{self.bucket}/imd/*.parquet')
        """)

        # Planning - aggregated
        self.conn.execute(f"""
            CREATE VIEW planning_summary AS
            SELECT
                uprn,
                COUNT(*) as total_apps,
                SUM(CASE WHEN decision = 'Refused' THEN 1 ELSE 0 END) as refusals,
                SUM(CASE WHEN decision = 'Granted' THEN 1 ELSE 0 END) as approvals,
                SUM(CASE WHEN application_type LIKE '%extension%' THEN 1 ELSE 0 END) as extensions,
                MAX(application_date) as most_recent_app
            FROM read_parquet('s3://{self.bucket}/planning/*.parquet')
            GROUP BY uprn
        """)

        # Flood - all types
        self.conn.execute(f"""
            CREATE VIEW flood_detailed AS
            SELECT
                uprn,
                flood_risk_rivers,
                flood_risk_surface_water,
                flood_risk_coastal,
                in_flood_zone_2,
                in_flood_zone_3
            FROM read_parquet('s3://{self.bucket}/flood/*.parquet')
        """)

        # Council Tax
        if self._s3_file_exists(f'{self.bucket}/council-tax/'):
            self.conn.execute(f"""
                CREATE VIEW council_tax AS
                SELECT * FROM read_parquet('s3://{self.bucket}/council-tax/*.parquet')
            """)

    def enrich_property(self, uprn: int, postcode: str) -> dict:
        """Get ALL enrichment for a property"""

        query = f"""
            SELECT
                -- EPC
                epc.current_energy_rating,
                epc.current_energy_efficiency,
                epc.co2_emissions_current,
                epc.lighting_cost_current + epc.heating_cost_current + epc.hot_water_cost_current as annual_energy_cost,

                -- IMD detailed
                imd.imd_decile,
                imd.income_score,
                imd.employment_score,
                imd.education_score,
                imd.health_score,
                imd.crime_score,

                -- Planning
                planning.total_apps,
                planning.refusals,
                planning.extensions,

                -- Flood
                flood.flood_risk_rivers,
                flood.flood_risk_surface_water,

                -- Council Tax
                ct.band,
                ct.annual_charge

            FROM (SELECT {uprn} as uprn, '{postcode}' as postcode) prop
            LEFT JOIN epc ON epc.uprn = prop.uprn
            LEFT JOIN imd_detailed imd ON imd.postcode = prop.postcode
            LEFT JOIN planning_summary planning ON planning.uprn = prop.uprn
            LEFT JOIN flood_detailed flood ON flood.uprn = prop.uprn
            LEFT JOIN council_tax ct ON ct.postcode = prop.postcode
        """

        result = self.conn.execute(query).fetchone()
        columns = [desc[0] for desc in self.conn.description]

        return dict(zip(columns, result)) if result else {}
```

---

## 🚀 **Action Plan**

### **Immediate (Connect YOUR S3 now)**:

1. **Update `.env`**:
```bash
FEATURE_S3_BUCKET=your-actual-bucket-name
AWS_REGION=eu-west-2
```

2. **Test S3 connection**:
```python
python -c "
from ingestion.loaders.s3_feature_loader import get_feature_store
store = get_feature_store()
# Should connect to your bucket
"
```

3. **Run real enrichment**:
```bash
# Match Savills postcodes to your S3 data
python scripts/enrich_savills_with_s3.py
```

4. **Update questionnaire**:
- Add EPC cost question
- Add IMD component questions
- Add detailed flood questions
- Add planning history questions

---

Want me to create the script that connects the 50 Savills properties to YOUR real S3 data right now?
