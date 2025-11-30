# UK Estate Agent Scraping - Ultra Plan

## Target Estate Agents (Ordered by Priority)

### Tier 1: Major National Chains (High Volume, Standardized)

#### 1. **Rightmove** ⭐⭐⭐⭐⭐
- **URL**: https://www.rightmove.co.uk
- **Volume**: 1M+ listings (largest UK property portal)
- **API**: Yes (commercial partnership required)
- **Scraping Difficulty**: Medium (anti-bot measures)
- **Data Quality**: Excellent (standardized, complete)
- **Listing URL Pattern**: `/properties/{listing-id}`
- **Key Fields Available**:
  - Full address
  - Detailed description
  - 10-30 images per listing
  - Floor plans
  - Price history
  - EPC data (sometimes)
  - Agent details
- **Scraping Strategy**:
  - Start with search by postcode
  - Paginate through results
  - Extract listing IDs
  - Visit detail pages
- **Note**: Rightmove has strict ToS. Consider API partnership or use for research only.

#### 2. **Zoopla** ⭐⭐⭐⭐⭐
- **URL**: https://www.zoopla.co.uk
- **Volume**: 500k+ listings
- **API**: Yes (Zoopla API for partners)
- **Scraping Difficulty**: Medium-High
- **Data Quality**: Excellent
- **Listing URL Pattern**: `/for-sale/details/{listing-id}`
- **Key Fields**:
  - Address
  - Description
  - Multiple images
  - Estimated value (AVM)
  - Transport links
  - Schools nearby
- **Scraping Strategy**:
  - Search API-like JSON endpoints
  - Structured data in HTML
- **Note**: Owned by Zoopla Media Group, has commercial API

#### 3. **OnTheMarket** ⭐⭐⭐⭐
- **URL**: https://www.onthemarket.com
- **Volume**: 200k+ listings
- **API**: Limited
- **Scraping Difficulty**: Low-Medium
- **Data Quality**: Good
- **Listing URL Pattern**: `/details/{listing-id}`
- **Key Fields**:
  - Address
  - Description
  - Images
  - Agent details
- **Scraping Strategy**: Simpler structure, less anti-bot
- **Note**: Agent-owned platform, less aggressive anti-scraping

### Tier 2: Regional/Independent Agents (Diverse, Specific Areas)

#### 4. **Purplebricks** ⭐⭐⭐⭐
- **URL**: https://www.purplebricks.co.uk
- **Volume**: 50k+ listings
- **Type**: Hybrid online/offline estate agent
- **Scraping Difficulty**: Low
- **Data Quality**: Very Good
- **Listing URL Pattern**: `/property-for-sale/{slug}`
- **Key Fields**:
  - Full address
  - Comprehensive description
  - Virtual tour links
  - Multiple images
  - Video walkthroughs
- **Scraping Strategy**:
  - JSON API available in page source
  - React-based SPA
  - API endpoints discoverable
- **Note**: Modern tech stack, clean data structure

#### 5. **Foxtons** (London-focused) ⭐⭐⭐
- **URL**: https://www.foxtons.co.uk
- **Volume**: 10k+ listings (London/Southeast)
- **Scraping Difficulty**: Medium
- **Data Quality**: Excellent (professional photos)
- **Listing URL Pattern**: `/properties-for-sale/{area}/{id}`
- **Key Fields**:
  - Detailed descriptions
  - High-quality images
  - Floor plans
  - 3D tours
  - Area guides
- **Scraping Strategy**: Well-structured HTML
- **Note**: Premium London agent, high-quality data

#### 6. **Savills** (Premium) ⭐⭐⭐
- **URL**: https://www.savills.com
- **Volume**: 20k+ listings (high-end)
- **Scraping Difficulty**: Low-Medium
- **Data Quality**: Excellent
- **Listing URL Pattern**: `/properties/{country}/residential/for-sale/{id}`
- **Key Fields**:
  - Luxury property details
  - Professional photography
  - Virtual tours
  - Brochures (PDF)
- **Note**: International, premium segment

#### 7. **Knight Frank** (Premium) ⭐⭐⭐
- **URL**: https://www.knightfrank.co.uk
- **Volume**: 15k+ listings
- **Scraping Difficulty**: Low
- **Data Quality**: Excellent
- **Listing URL Pattern**: `/properties/residential/for-sale/{id}`
- **Key Fields**: Similar to Savills
- **Note**: High-end market

### Tier 3: Local/Independent Agents (Niche, Local Expertise)

#### 8. **Hamptons** ⭐⭐
- **URL**: https://www.hamptons.co.uk
- **Volume**: 5k+ listings
- **Scraping Difficulty**: Low
- **Note**: Good for specific regions

#### 9. **Chestertons** ⭐⭐
- **URL**: https://www.chestertons.co.uk
- **Volume**: 5k+ listings (London)
- **Scraping Difficulty**: Low
- **Note**: Well-established London agent

#### 10. **Kinleigh Folkard & Hayward (KFH)** ⭐⭐
- **URL**: https://www.kfh.co.uk
- **Volume**: 8k+ listings (London/Southeast)
- **Scraping Difficulty**: Low
- **Note**: Strong presence in specific areas

---

## Scraping Architecture

### Phase 1: Portal Aggregators (Start Here)

**Recommendation**: Begin with **OnTheMarket** or **Purplebricks**
- Less aggressive anti-scraping
- Cleaner data structures
- Smaller volume = easier testing
- Legally clearer (some allow research use)

### Phase 2: Add Regional Agents

**After proving concept**, add:
- Foxtons (London)
- Savills (premium)
- 2-3 local agents per target region

### Phase 3: Consider Aggregator APIs (Long-term)

**Instead of scraping**:
- Partner with Rightmove/Zoopla for API access
- Use RTDF (Real-Time Data Feed) if agent-direct

---

## Technical Implementation Plan

### 1. Data Fields to Extract

#### Mandatory Fields
```python
{
  "external_listing_id": str,  # Agent's ID
  "listing_url": str,
  "title": str,
  "raw_address": str,
  "postcode": str (extract via regex),
  "price_text": str,
  "price_numeric": Decimal,
  "bedrooms": int,
  "bathrooms": int,
  "property_type": str,
  "description": str,
  "listed_date": date,
  "agent_name": str,
  "agent_branch": str,
  "image_urls": list[str]
}
```

#### Optional Fields
```python
{
  "tenure": str,  # freehold/leasehold
  "square_feet": int,
  "epc_rating": str,
  "council_tax_band": str,
  "virtual_tour_url": str,
  "floor_plan_urls": list[str],
  "brochure_url": str
}
```

### 2. Scraper Components

#### A. Search Page Scraper
```python
class SearchScraper:
    """Iterates through search results pages"""

    def scrape_search(
        self,
        postcode_area: str,
        max_pages: int = 50
    ) -> List[str]:
        """Returns list of listing URLs"""
        pass
```

#### B. Detail Page Scraper
```python
class DetailScraper:
    """Extracts data from individual listing page"""

    def scrape_listing(self, url: str) -> RawListing:
        """Returns structured listing data"""
        pass
```

#### C. Image Downloader
```python
class ImageDownloader:
    """Downloads and stores property images"""

    def download_images(
        self,
        image_urls: List[str],
        listing_id: int,
        output_dir: str = "property_images"
    ) -> List[str]:
        """Downloads images, returns local paths"""
        # Save as: property_images/{listing_id}/image_{n}.jpg
        pass
```

### 3. Anti-Scraping Measures to Handle

#### Common Protections
- **Rate Limiting**: Implement delays (2-5 seconds between requests)
- **User-Agent Rotation**: Cycle through browser user agents
- **Cloudflare**: Use `cloudscraper` library
- **JavaScript Rendering**: Use Selenium or Playwright for SPAs
- **CAPTCHAs**: Manual solving or 2captcha API (avoid if possible)
- **IP Blocking**: Rotate proxies (residential proxies best)

#### Recommended Tools
```python
# HTTP Requests
import requests
from bs4 import BeautifulSoup
import cloudscraper  # For Cloudflare

# JavaScript Rendering (if needed)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# OR
from playwright.sync_api import sync_playwright

# Proxy Rotation (if needed)
# Use services like:
# - Bright Data (formerly Luminati)
# - Smartproxy
# - Oxylabs
```

### 4. Storage Strategy

#### Images
```bash
# Directory structure
property_images/
├── {listing_id}/
│   ├── main.jpg
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── floor_plan.jpg
```

#### Alternative: S3 Storage
```python
# Upload to S3
import boto3

s3 = boto3.client('s3')
s3_key = f"listings/{listing_id}/image_{n}.jpg"
s3.upload_file(local_path, bucket, s3_key)

# Store S3 URL in database
image_urls = [
    f"https://s3.amazonaws.com/{bucket}/{s3_key}",
    ...
]
```

### 5. Legal & Ethical Considerations

#### ⚠️ Important Notes

**Legal Risks**:
- Scraping may violate Terms of Service
- Copyright issues with images
- GDPR compliance required

**Recommended Approach**:
1. **Start with robots.txt compliance**
   ```python
   from urllib.robotparser import RobotFileParser

   rp = RobotFileParser()
   rp.set_url("https://www.example.com/robots.txt")
   rp.read()

   if rp.can_fetch("*", url):
       # OK to scrape
   ```

2. **Respect rate limits**
   - 1-2 requests per second maximum
   - Implement exponential backoff

3. **Add User-Agent with contact**
   ```python
   headers = {
       'User-Agent': 'PropertyResearchBot/1.0 (+mailto:your@email.com)'
   }
   ```

4. **Consider API partnerships instead**
   - Rightmove API (requires partnership)
   - Zoopla API (for registered partners)
   - Direct agent feeds (RTDF/XML)

**Long-Term Solution**:
- Partner with agents for direct feeds
- Use official APIs where available
- Build relationships with multiple local agents
- Scraping only for prototype/research

---

## Implementation Priority

### Week 1: OnTheMarket Scraper
- Build scraper for OnTheMarket
- Implement search + detail page scraping
- Add image downloading
- Test with 100 listings

### Week 2: Add Purplebricks
- Replicate for Purplebricks
- Refine base scraper class
- Add error handling

### Week 3: Regional Agents
- Add 2-3 local agents (Foxtons, Chestertons, KFH)
- Build agent config system

### Week 4: Scaling
- Add proxy rotation (if needed)
- Implement distributed scraping (Celery workers)
- Set up monitoring/alerts

---

## Example: OnTheMarket Scraper Spec

### URL Patterns
```python
# Search
https://www.onthemarket.com/for-sale/property/london/?page=1

# Listing detail
https://www.onthemarket.com/details/12345678/
```

### HTML Structure (Approximate)
```html
<!-- Search results -->
<div class="property-result">
  <a href="/details/12345678/">
    <h2 class="property-title">2 bedroom flat for sale</h2>
    <span class="price">£475,000</span>
    <address>Chelsea, London SW3</address>
  </a>
</div>

<!-- Detail page -->
<div class="property-detail">
  <h1 class="price">£475,000</h1>
  <h2 class="address">Flat 5, 123 King's Road, Chelsea, London SW3 5EZ</h2>
  <div class="details">
    <span class="beds">2 bedrooms</span>
    <span class="baths">1 bathroom</span>
  </div>
  <div class="description">...</div>
  <div class="gallery">
    <img src="https://images.onthemarket.com/12345678/1.jpg">
    <img src="https://images.onthemarket.com/12345678/2.jpg">
  </div>
</div>
```

### Scraper Pseudocode
```python
class OnTheMarketScraper(BaseScraper):
    base_url = "https://www.onthemarket.com"

    def search(self, postcode_area: str, page: int):
        url = f"{self.base_url}/for-sale/property/{postcode_area}/?page={page}"
        soup = BeautifulSoup(self.fetch(url))

        for card in soup.select('.property-result'):
            listing_url = card.select_one('a')['href']
            yield self.scrape_detail(listing_url)

    def scrape_detail(self, url: str) -> RawListing:
        soup = BeautifulSoup(self.fetch(url))

        return RawListing(
            external_listing_id=extract_id_from_url(url),
            listing_url=url,
            title=soup.select_one('.property-title').text,
            price_text=soup.select_one('.price').text,
            raw_address=soup.select_one('.address').text,
            bedrooms=extract_number(soup.select_one('.beds').text),
            description=soup.select_one('.description').text,
            image_urls=[img['src'] for img in soup.select('.gallery img')]
        )
```

---

## Monitoring & Alerts

### Metrics to Track
- Listings scraped per hour
- Success rate (% successful scrapes)
- Duplicate listings
- Images downloaded
- Errors encountered

### Alerting
```python
# Send alert if scraper fails
if error_rate > 10%:
    send_slack_alert("OnTheMarket scraper failing!")
```

---

## Next Steps

1. **Choose Target Agent**: Start with OnTheMarket or Purplebricks
2. **Implement Scraper**: Use existing base scraper framework
3. **Test**: Scrape 50-100 listings
4. **Refine**: Handle edge cases
5. **Scale**: Add more agents
6. **Consider APIs**: Long-term partnership approach

Ready to implement! Which estate agent would you like to start with?
