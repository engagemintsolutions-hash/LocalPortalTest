# COMPLETE WORKING DEMO - Quick Test Guide

## What's Working NOW

### 1. ✅ Foxtons Scraper (100 real listings)
- Price: £14,950,000, £13,500,000, £10,750,000, etc.
- Bedrooms: 4, 12, 6, etc.
- Bathrooms: 4, 12, 5, etc.
- Address: Connaught Place, Westbourne Gardens, etc.
- Property type: flat, house, site
- URLs: Real Foxtons listing links

**Note**: Images require JavaScript rendering. For MVP, we have 3 options:

**Option A (Quick MVP)**: Use the data we have + placeholder images
**Option B (Complete)**: Add Selenium to render JavaScript pages
**Option C (Best)**: Find simpler independent agents with static HTML

### 2. ✅ CompareTheMarket-style Questionnaire
- Beautiful multi-step wizard
- Visual property type cards
- Priority sliders with icons
- Links to existing professional report

### 3. ✅ Complete Backend
- FastAPI with search endpoint
- S3 storage manager (ready)
- Matching & enrichment engines
- Report generation

## Quick Demo Test (Without Images)

### Step 1: Add Sample Data to Database

```bash
cd "C:\Sales Portal"

# Start database
docker-compose up -d postgres

# Or if already running locally
psql property_search < schema.sql

# Add Foxtons as agent
psql property_search << EOF
INSERT INTO agents (name, website_url, is_active)
VALUES ('Foxtons', 'www.foxtons.co.uk', true);
EOF
```

### Step 2: Load Scraped Listings into Database

```python
# Save as: scripts/load_foxtons_sample.py
from config.database import SessionLocal
from api.models.database import ListingRaw
from ingestion.scrapers.foxtons_scraper_v2 import create_foxtons_scraper

db = SessionLocal()

# Scrape first page (100 listings)
scraper = create_foxtons_scraper(agent_id=1)
listings = scraper.scrape_page(1)

print(f"Loading {len(listings)} listings into database...")

for listing in listings:
    data = listing.to_dict()
    data['agent_id'] = 1

    db_listing = ListingRaw(**data)
    db.add(db_listing)

db.commit()
print(f"Loaded {len(listings)} listings!")
db.close()
```

```bash
python scripts/load_foxtons_sample.py
```

### Step 3: Test the Questionnaire

```bash
# Frontend already running at:
http://localhost:8080/questionnaire-wizard.html

# Backend API:
python cli.py serve
```

## Adding Images - Three Options

### Option A: Placeholder Images (Quick Test)

Use placeholder service for demo:

```python
# In the frontend JS
const placeholderImage = `https://via.placeholder.com/400x300/667eea/ffffff?text=${listing.bedrooms}+Bed`;
```

### Option B: Selenium (Get Real Images)

Install Selenium:

```bash
pip install selenium webdriver-manager
```

Update scraper:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def fetch_with_selenium(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)  # Wait for JavaScript

    # Find images
    img_elements = driver.find_elements(By.CSS_SELECTOR, '.gallery img')
    image_urls = [img.get_attribute('src') for img in img_elements]

    driver.quit()
    return image_urls
```

### Option C: Simpler Estate Agents (Best for MVP)

Try local independent agents with static HTML:

```
- Barnard Marcus
- Kinleigh Folkard & Hayward (older site structure)
- Small local agents (often use basic CMSs)
```

## S3 Integration Test

The S3 storage manager is ready. Test it:

```python
from ingestion.storage.s3_storage import get_storage_manager

storage = get_storage_manager()

# Upload test images
test_image_urls = [
    'https://via.placeholder.com/800x600.jpg',
    'https://via.placeholder.com/800x600/667eea.jpg'
]

s3_urls = storage.upload_listing_images(
    listing_id=1,
    image_urls=test_image_urls,
    agent_id=1
)

print(f"Uploaded to S3: {s3_urls}")

# Verify
import boto3
s3 = boto3.client('s3')
objects = s3.list_objects_v2(Bucket='uk-property-images', Prefix='images/1/1/')
for obj in objects.get('Contents', []):
    print(f"  - {obj['Key']}")
```

## Current Status Summary

✅ **Working**:
- Foxtons scraper (100 listings with complete data except images)
- S3 storage system (tested, ready)
- CompareTheMarket-style wizard
- Backend API
- Database schema

🔄 **Needs Work**:
- Image extraction (requires Selenium OR simpler agent sites)

🚀 **Ready to Test**:
- Load 100 Foxtons listings
- Run questionnaire wizard
- See results (with placeholder images)
- Click → professional report

## Quick Win: Test NOW with What We Have

1. Load the 100 Foxtons listings (no images)
2. Use the wizard
3. See real search results
4. Click → existing professional report

Then decide on image strategy (Selenium vs. simpler agents).

Want me to create the quick test script to load the listings and demonstrate the full flow?
