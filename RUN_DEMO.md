# 🎯 RUN THE COMPLETE DEMO - Step by Step

This guide shows you how to run the complete end-to-end demonstration with:
- ✅ Real Savills property listings
- ✅ Real images uploaded to S3
- ✅ CompareTheMarket-style questionnaire
- ✅ Search results with match scores
- ✅ £5 paywall demonstration
- ✅ Professional property report

---

## Prerequisites (Quick Setup)

### 1. Start Database

```bash
cd "C:\Sales Portal"

# Option A: Docker
docker-compose up -d postgres

# Option B: Local PostgreSQL
# (Ensure PostgreSQL is running)
psql -U postgres -c "CREATE DATABASE property_search;"
psql property_search < schema.sql
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS (for S3)

Already done! You have AWS credentials configured and S3 bucket created.

---

## Step-by-Step Demo

### Step 1: Load Real Property Listings (5-10 minutes)

This will scrape 15 real Savills properties with images and upload to S3:

```bash
cd "C:\Sales Portal"
python scripts/demo_load_listings.py
```

**What this does**:
- Scrapes 15 properties from Savills
- Extracts: price, beds, baths, address, postcode, description
- Downloads 5 images per property (75 total images)
- Uploads all images to S3: `s3://uk-property-images/`
- Stores in database with S3 image URLs
- Creates mock enrichment data (EPC, schools, AVM, etc.)

**Expected output**:
```
Loaded 15 real Savills listings
Images uploaded to S3: s3://uk-property-images/images/3/
```

### Step 2: Start the Backend API

```bash
# In a new terminal
cd "C:\Sales Portal"
python cli.py serve
```

API runs at: `http://localhost:8000`

### Step 3: Start the Frontend

```bash
# In another terminal (or it's already running)
cd "C:\Sales Portal\frontend"
python -m http.server 8080
```

Frontend runs at: `http://localhost:8080`

### Step 4: Test the Complete Flow

#### 4a. Open the Questionnaire Wizard

Visit: **`http://localhost:8080/questionnaire-wizard.html`**

#### 4b. Fill in Your Preferences

**Step 1 - Budget**:
- Maximum: £2,000,000 (or any amount)
- Click "Continue"

**Step 2 - Property**:
- Click bedroom count (e.g., 4)
- Click property types (e.g., House, Flat)
- Click "Continue"

**Step 3 - Location**:
- Postcode: "SW1, W1" (or any)
- Radius: 10 km
- Click "Continue"

**Step 4 - Priorities**:
- Adjust sliders for what matters:
  - Schools: 30%
  - Value: 25%
  - Safety: 20%
  - Energy: 15%
  - Commute: 10%
- Click "Find My Perfect Home"

#### 4c. See Search Results

You'll see **real Savills properties**:
- Real prices (£1,595,000, £2,250,000, etc.)
- Real addresses
- **Real S3 images** from each property
- Match scores based on your preferences

#### 4d. Click Any Property

Clicking opens: `professional-report.html?listing_id=X`

#### 4e. £5 Paywall Appears

A beautiful modal shows:
- Property preview
- List of report features
- **£5.00 purchase button**

#### 4f. "Purchase" Report (Demo)

Click "Purchase Full Report - £5.00"
- Confirms demo payment
- Paywall disappears
- Full professional report shown with real data

---

## What You'll See

### Search Results Page
```
┌────────────────────────────────────────┐
│ [Real Savills Property Image from S3] │
│                           Match: 87%   │
├────────────────────────────────────────┤
│ £1,595,000                             │
│ 4 bedroom house for sale in...         │
│ Elton, Ludlow, Herefordshire, SY8 2HQ │
│                                        │
│ [4 bed] [3 bath] [EPC B] [Great Value] │
│                                        │
│ ████████████████░░ 87%                 │
│                                        │
│ [View Details & Get £5 Report]         │
└────────────────────────────────────────┘
```

### Professional Report (After £5 "Purchase")

Shows real data:
- ✅ Property address & price
- ✅ Bedrooms, bathrooms from Savills
- ✅ EPC rating (mock enriched)
- ✅ AVM valuation (mock)
- ✅ School quality scores
- ✅ Crime & safety data
- ✅ Planning applications
- ✅ All enriched metrics

---

## Verification

### Check S3 Images

```bash
# List uploaded images
aws s3 ls s3://uk-property-images/images/3/ --recursive

# Should show:
# images/3/1/main.jpg
# images/3/1/001.jpg
# images/3/1/002.jpg
# images/3/2/main.jpg
# ... etc (75 images total)
```

### Check Database

```bash
psql property_search

# Check listings loaded
SELECT COUNT(*) FROM listings_raw;          -- Should be 15
SELECT COUNT(*) FROM listings_enriched;     -- Should be 15

# Check image URLs stored
SELECT raw_listing_id, jsonb_array_length(image_urls) as num_images
FROM listings_raw
WHERE image_urls IS NOT NULL;

# View a sample
SELECT title, price_text, bedrooms, bathrooms
FROM listings_raw
LIMIT 3;
```

---

## Files You Need

### Backend Integration:
- ✅ `scripts/demo_load_listings.py` - Loads 15 real listings
- ✅ `ingestion/scrapers/savills_scraper.py` - Working scraper
- ✅ `ingestion/storage/s3_storage.py` - S3 upload manager
- ✅ `api/routers/search.py` - Search endpoint
- ✅ `search/scorer.py` - Updated with image URLs

### Frontend:
- ✅ `frontend/questionnaire-wizard.html` - Multi-step form
- ✅ `frontend/questionnaire-wizard.js` - Updated with images
- ✅ `frontend/listing-report-integration.js` - Paywall + report integration
- ✅ `frontend/professional-report.html` - Existing Doorstep report

---

## Troubleshooting

### No results in search?
- Check database has data: `SELECT COUNT(*) FROM listings_enriched;`
- Adjust budget in questionnaire (properties are £1-15M range)

### Images not showing?
- Check S3 URLs in database: `SELECT image_urls FROM listings_raw LIMIT 1;`
- Verify S3 bucket is public-read or use signed URLs

### API not responding?
- Check FastAPI is running: `curl http://localhost:8000/health`
- Check logs in terminal

### Paywall not appearing?
- Add script to professional-report.html:
  ```html
  <script src="listing-report-integration.js"></script>
  ```

---

## Next Steps After Demo

1. **Add more agents**: Replicate Savills scraper for other independent agents
2. **Load full property database**: Import your UK UPRN data
3. **Real enrichment**: Connect to S3 feature store (EPC, IMD, planning data)
4. **Real AVM**: Integrate valuation API
5. **Real payments**: Stripe integration
6. **Deploy**: AWS ECS + RDS + S3

---

## Expected Timeline

- **Step 1** (Load listings): 5-10 minutes
- **Steps 2-3** (Start services): 1 minute
- **Step 4** (Test flow): 2-3 minutes
- **Total**: ~15 minutes to full working demo

---

Ready to run? Execute Step 1:

```bash
python scripts/demo_load_listings.py
```

Then test at: `http://localhost:8080/questionnaire-wizard.html` 🚀
