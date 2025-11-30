# Estate Agent Scraping System - Complete Guide

## Overview

A complete, production-ready system for scraping property listings from independent UK estate agents with:
- ✅ Full data extraction (address, price, beds, baths, description)
- ✅ Automatic image downloading and S3 storage
- ✅ Database storage with proper indexing
- ✅ Respectful rate limiting and error handling

## Currently Implemented Scrapers

### 1. **Foxtons** (London-focused independent agent)
- **Status**: ✅ Complete
- **File**: `ingestion/scrapers/foxtons_scraper.py`
- **Coverage**: London and Southeast
- **Volume**: ~10,000 listings
- **Data Quality**: Excellent (professional photography)

### Ready to Add (Templates Available)
- Chestertons
- Kinleigh Folkard & Hayward (KFH)
- Hamptons
- Savills

## Architecture

```
Scraper Flow:
1. Search page → Extract listing URLs
2. Detail page → Extract all data
3. Download images → Upload to S3
4. Store in database → listings_raw table
5. Trigger matching → Link to properties table
6. Trigger enrichment → Create listings_enriched
```

## S3 Storage Structure

```
s3://uk-property-images/
├── images/
│   └── {agent_id}/
│       └── {listing_id}/
│           ├── main.jpg          # Primary image
│           ├── 001.jpg           # Additional images
│           ├── 002.jpg
│           ├── 003.jpg
│           └── floor_plan.jpg    # Floor plan (if available)
└── listings/
    ├── raw/
    │   └── {listing_id}.json     # Raw scraped data
    └── enriched/
        └── {listing_id}.json     # Enriched listing data
```

## Setup Instructions

### 1. Configure AWS Credentials

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=eu-west-2
export PROPERTY_IMAGES_BUCKET=uk-property-images
```

Or add to `.env`:
```
AWS_ACCESS_KEY_ID=AKIAXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxx
AWS_REGION=eu-west-2
PROPERTY_IMAGES_BUCKET=uk-property-images
```

### 2. Create S3 Bucket

The S3 storage manager will auto-create the bucket, or create manually:

```bash
aws s3 mb s3://uk-property-images --region eu-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket uk-property-images \
  --versioning-configuration Status=Enabled
```

### 3. Add Estate Agents to Database

```bash
cd "C:\Sales Portal"
python scripts/setup_agents.py
```

This adds:
- Foxtons
- Chestertons
- KFH
- Hamptons

### 4. Run Scraper

```bash
# Scrape all active agents
python -m ingestion.scrapers.orchestrator_with_s3

# Or use CLI
python cli.py scrape-with-s3  # (if added to CLI)
```

## Data Extracted

### Mandatory Fields
- ✅ `external_listing_id` - Agent's internal ID
- ✅ `listing_url` - Full URL to listing
- ✅ `title` - Property title
- ✅ `raw_address` - Full address string
- ✅ `postcode` - Extracted UK postcode
- ✅ `price_text` - Original price string (e.g. "£450,000")
- ✅ `price_numeric` - Parsed numeric price
- ✅ `bedrooms` - Number of bedrooms
- ✅ `bathrooms` - Number of bathrooms
- ✅ `property_type` - detached/semi_detached/terraced/flat
- ✅ `description` - Full property description
- ✅ `image_urls` - List of S3 URLs (after upload)

### Optional Fields
- `tenure` - freehold/leasehold
- `square_feet` - Property size
- `listed_date` - When listing was added
- `floor_plan_url` - S3 URL of floor plan

## Code Structure

### S3 Storage Manager
**File**: `ingestion/storage/s3_storage.py`

```python
from ingestion.storage.s3_storage import get_storage_manager

storage = get_storage_manager()

# Upload images
s3_urls = storage.upload_listing_images(
    listing_id=123,
    image_urls=['http://agent.com/img1.jpg', ...],
    agent_id=2
)

# Upload floor plan
floor_plan_url = storage.upload_floor_plan(
    listing_id=123,
    floor_plan_url='http://agent.com/floorplan.pdf',
    agent_id=2
)

# Get all images for a listing
urls = storage.get_listing_image_urls(listing_id=123, agent_id=2)
```

### Foxtons Scraper
**File**: `ingestion/scrapers/foxtons_scraper.py`

```python
from ingestion.scrapers.foxtons_scraper import create_foxtons_scraper

scraper = create_foxtons_scraper(agent_id=2)

# Scrape first 5 pages
for page in range(1, 6):
    listings = scraper.scrape_page(page)
    print(f"Page {page}: {len(listings)} listings")

# Or scrape all pages
all_listings = scraper.scrape()  # Uses max_pages from config
```

### Enhanced Orchestrator
**File**: `ingestion/scrapers/orchestrator_with_s3.py`

```python
from config.database import SessionLocal
from ingestion.scrapers.orchestrator_with_s3 import run_scraping_job_with_s3

db = SessionLocal()
stats = run_scraping_job_with_s3(db)

print(f"Scraped: {stats['total_listings_scraped']}")
print(f"Images uploaded: {stats['total_images_uploaded']}")
```

## Adding New Estate Agent Scrapers

### Step 1: Create Scraper Class

```python
# ingestion/scrapers/my_agent_scraper.py

from .base_scraper import BaseScraper, RawListing, ScraperConfig
from ingestion.storage.s3_storage import get_storage_manager

class MyAgentScraper(BaseScraper):
    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self.s3_storage = get_storage_manager()

    def parse_listing_page(self, soup, page_num):
        """Extract listing URLs from search results"""
        listings = []

        for card in soup.find_all('div', class_='property-card'):
            # Extract data
            listing = self._parse_card(card)
            listings.append(listing)

        return listings

    def _parse_card(self, card):
        """Parse individual card"""
        # Extract: title, price, address, beds, baths, etc.
        return RawListing(...)

def create_my_agent_scraper(agent_id):
    config = ScraperConfig(
        agent_id=agent_id,
        agent_name="My Agent",
        base_url="https://www.myagent.co.uk",
        listings_url_template="https://www.myagent.co.uk/properties?page={page}",
        max_pages=20,
        delay_seconds=2.0
    )
    return MyAgentScraper(config)
```

### Step 2: Register in Orchestrator

Edit `orchestrator_with_s3.py`:

```python
def _create_scraper(self, agent: Agent):
    agent_name_lower = agent.name.lower()

    if 'foxtons' in agent_name_lower:
        return create_foxtons_scraper(agent.agent_id)
    elif 'myagent' in agent_name_lower:
        return create_my_agent_scraper(agent.agent_id)
    # ...
```

### Step 3: Add Agent to Database

```python
# scripts/setup_agents.py

{
    'name': 'My Agent',
    'branch_name': 'London',
    'website_url': 'www.myagent.co.uk',
    'is_active': True,
    'scraper_config': {...}
}
```

### Step 4: Run Scraper

```bash
python scripts/setup_agents.py  # Add to DB
python -m ingestion.scrapers.orchestrator_with_s3  # Run scraper
```

## Rate Limiting & Best Practices

### Respectful Scraping
```python
# In ScraperConfig
delay_seconds=2.0  # 2 seconds between requests (30 requests/min)

# Add random jitter
import time
import random
time.sleep(delay_seconds + random.uniform(0, 1))
```

### Error Handling
```python
try:
    listing = scraper.scrape_page(page)
except requests.RequestException as e:
    logger.error(f"Network error on page {page}: {e}")
    # Implement exponential backoff
    time.sleep(5 * (attempt ** 2))
    retry()
```

### Robots.txt Compliance
```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://www.agent.co.uk/robots.txt")
rp.read()

if not rp.can_fetch("*", url):
    logger.warning(f"Blocked by robots.txt: {url}")
    skip()
```

## Monitoring

### Key Metrics

```python
# Track in orchestrator
stats = {
    'listings_scraped': 0,
    'images_uploaded': 0,
    'errors': 0,
    'duration_seconds': 0
}
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

### Alerts

```python
# Send alert if error rate > 10%
if error_rate > 0.1:
    send_slack_alert(f"Scraper failing: {error_rate*100}% error rate")
```

## Testing

### Test Individual Scraper

```bash
cd "C:\Sales Portal"
python -m ingestion.scrapers.foxtons_scraper
```

### Test S3 Upload

```python
from ingestion.storage.s3_storage import get_storage_manager

storage = get_storage_manager()

# Test image upload
urls = storage.upload_listing_images(
    listing_id=999,
    image_urls=['https://example.com/image.jpg'],
    agent_id=1
)

print(f"Uploaded: {urls}")

# Verify in S3
aws s3 ls s3://uk-property-images/images/1/999/
```

## Scaling

### Distributed Scraping with Celery

```python
# tasks.py
from celery import Celery

app = Celery('scraper', broker='redis://localhost:6379/0')

@app.task
def scrape_agent(agent_id):
    """Scrape a single agent (Celery task)"""
    db = SessionLocal()
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    orchestrator = EnhancedScraperOrchestrator(db)
    return orchestrator.run_scraper_for_agent(agent)

# Run in parallel
for agent_id in [1, 2, 3, 4]:
    scrape_agent.delay(agent_id)
```

### Proxy Rotation (if needed)

```python
# For high-volume scraping
proxies = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
]

session.proxies = {'http': random.choice(proxies)}
```

## Costs

### S3 Storage Costs (Estimate)

- **Images**: ~500KB per image
- **10,000 listings** × 10 images = 100,000 images
- **Storage**: 50GB = ~$1.15/month
- **Requests**: Minimal (<$0.01/month)

### Total Monthly Cost
- S3 Storage: ~$1.15
- Data Transfer: ~$0.50
- **Total**: ~$2/month for 10k listings

## Legal Considerations

⚠️ **Important**:
- Scraping may violate Terms of Service
- Images are copyrighted
- GDPR compliance required
- Use robots.txt compliance

**Recommended**:
1. Start with 1-2 agents for testing
2. Respect rate limits (2-5 sec delays)
3. Add User-Agent with contact email
4. Consider API partnerships long-term

## Troubleshooting

### Images Not Uploading
```bash
# Check AWS credentials
aws s3 ls

# Check bucket exists
aws s3 ls s3://uk-property-images/

# Test upload manually
echo "test" > test.txt
aws s3 cp test.txt s3://uk-property-images/test.txt
```

### Scraper Blocked
```
Error: 403 Forbidden
```
**Solution**: Add delays, rotate user agents, use proxies

### Missing Data Fields
**Solution**: Inspect HTML structure, update CSS selectors:
```python
# Use browser DevTools to find correct selectors
soup.find('div', class_='new-class-name')
```

## Next Steps

1. ✅ **Test Foxtons scraper** with 1-2 pages
2. **Add more agents** (Chestertons, KFH, Hamptons)
3. **Set up scheduled scraping** (daily via Celery/Lambda)
4. **Monitor S3 costs** and optimize image sizes
5. **Consider API partnerships** for long-term

## Commands Quick Reference

```bash
# Setup
python scripts/setup_agents.py

# Scrape all agents
python -m ingestion.scrapers.orchestrator_with_s3

# View S3 images
aws s3 ls s3://uk-property-images/images/ --recursive | head -20

# Check database
psql property_search -c "SELECT COUNT(*) FROM listings_raw WHERE image_urls IS NOT NULL;"

# Full pipeline (scrape → match → enrich)
python cli.py pipeline
```

---

Ready to scrape! Start with Foxtons and expand from there. 🏠📸
