# System Architecture - Complete Flow

## Overview

The UK Property Search Engine has **two separate but connected systems**:

1. **Backend Scraping & Data Pipeline** (automated, runs in background)
2. **Customer-Facing Property Portal** (website for property searchers)

---

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SCRAPING SYSTEM                      │
│                    (Runs Automatically)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  1. SCRAPING (Every 24 hours)                                 │
│  ─────────────────────────────                                │
│  Foxtons, Chestertons, KFH, etc.                             │
│  ↓                                                             │
│  Download: address, price, beds, baths, description, images   │
│  ↓                                                             │
│  Store in: listings_raw table                                 │
│  Upload to: S3 (images)                                       │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  2. MATCHING (Automatic after scraping)                       │
│  ────────────────────────────────────                         │
│  Match scraped listings → Base properties (UPRN database)     │
│  ↓                                                             │
│  Uses: Address matching (3-tier algorithm)                    │
│  ↓                                                             │
│  Updates: listings_raw.matched_property_id                    │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  3. ENRICHMENT (Automatic after matching)                     │
│  ──────────────────────────────────────                       │
│  For each matched listing:                                    │
│  ↓                                                             │
│  Fetch from S3 Feature Store:                                 │
│    - EPC data (rating, score, CO2)                           │
│    - IMD (deprivation index)                                  │
│    - Planning applications                                    │
│    - Flood risk                                               │
│    - Broadband speed                                          │
│  ↓                                                             │
│  Calculate with PostGIS:                                      │
│    - Distance to schools (with Ofsted ratings)               │
│    - Distance to stations                                     │
│    - Distance to airports                                     │
│    - Conservation area containment                            │
│  ↓                                                             │
│  Call AVM API:                                                │
│    - Property valuation                                       │
│    - Confidence interval                                      │
│    - Comparable properties                                    │
│  ↓                                                             │
│  Create: listings_enriched record                             │
│  (Ready for customer searches!)                               │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│                    DATABASE STATE                              │
│  ─────────────────────────────────────                        │
│  ✓ listings_raw: 10,000 listings (from scrapers)             │
│  ✓ listings_enriched: 10,000 listings (with all data)        │
│  ✓ S3 images: 100,000 images (10 per listing)                │
│  ✓ Ready for customer searches                                │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CUSTOMER-FACING PROPERTY PORTAL                     │
│              (Public Website)                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  CUSTOMER INTERACTION                                          │
│  ────────────────────                                         │
│  1. Visit: property-search.html                               │
│  2. Fill questionnaire:                                       │
│     - Budget: £500,000                                        │
│     - Bedrooms: 2+                                            │
│     - Location: SW1, SW3                                      │
│     - Preferences: Schools 30%, Safety 20%, etc.             │
│  3. Click "Search Properties"                                 │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  API CALL                                                      │
│  ────────                                                      │
│  POST http://localhost:8000/api/search                        │
│  ↓                                                             │
│  FastAPI receives questionnaire                               │
│  ↓                                                             │
│  Search & Scoring Engine:                                     │
│    1. Apply hard filters (budget, beds, location)            │
│    2. For each listing:                                       │
│       - Calculate school score (Ofsted / 4)                  │
│       - Calculate safety score (IMD + crime)                  │
│       - Calculate energy score (EPC / 100)                    │
│       - Calculate value score (AVM delta)                     │
│       - Multiply by user weights                              │
│       - Sum = match_score                                     │
│    3. Sort by match_score DESC                                │
│  ↓                                                             │
│  Return: 100 best matches                                     │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  RESULTS DISPLAY                                               │
│  ───────────────                                              │
│  property-search.html shows:                                  │
│                                                                │
│  ┌────────────────────────────────────┐                      │
│  │ £475,000              Match: 87%   │                      │
│  │ 2 Bed Flat in Chelsea              │                      │
│  │ ──────────────────────────────────  │                      │
│  │ ✓ EPC: B  ✓ Undervalued            │                      │
│  │ Schools: 85% | Crime: Low          │                      │
│  └────────────────────────────────────┘                      │
│                                                                │
│  Customer clicks → listing-detail.html                        │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  LISTING DETAIL PAGE                                           │
│  ───────────────────                                          │
│  GET /api/listing/123                                         │
│  ↓                                                             │
│  Shows:                                                        │
│    - Full address, price, beds, baths                        │
│    - All enriched data (EPC, schools, transport)             │
│    - Images from S3                                           │
│    - AVM valuation                                            │
│    - "Purchase £5 Report" button                              │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│  REPORT PURCHASE (Optional)                                    │
│  ─────────────────────────                                    │
│  Customer clicks "Purchase Report - £5.00"                    │
│  ↓                                                             │
│  POST /api/listing/123/purchase-report                        │
│  ↓                                                             │
│  1. Stripe payment (£5)                                       │
│  2. Generate PDF report:                                      │
│     - Planning history                                        │
│     - Restrictive covenants                                   │
│     - Comparable sales                                        │
│     - Detailed area analysis                                  │
│  3. Upload to S3                                              │
│  4. Return CloudFront URL                                     │
│  ↓                                                             │
│  Customer downloads PDF                                       │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Automation

### Scheduled Scraping (Daily)

```bash
# Run automatically via cron/Lambda/Celery
0 2 * * * cd /app && python -m ingestion.scrapers.orchestrator_with_s3
```

**What happens**:
1. Scraper wakes up at 2 AM
2. Visits Foxtons, Chestertons, KFH, etc.
3. Downloads new listings
4. Downloads images → uploads to S3
5. Stores in `listings_raw`
6. Auto-triggers matching
7. Auto-triggers enrichment
8. New listings appear in search results!

### Matching & Enrichment (Triggered)

```bash
# Runs automatically after scraping
python cli.py match    # Links listings to properties
python cli.py enrich   # Adds all data
```

**Result**:
- `listings_enriched` table always up-to-date
- Customer searches always show latest listings
- No manual intervention needed

---

## 🌐 Customer-Facing Portal

### What Customers See

1. **Homepage** (`index.html`)
   - Existing Doorstep website
   - "Search Properties" button → `property-search.html`

2. **Search Portal** (`property-search.html`)
   - Questionnaire form
   - Preference sliders
   - Submit → Call API → Results

3. **Search Results** (same page, dynamically loaded)
   - Grid of property cards
   - Match scores
   - Click → `listing-detail.html`

4. **Listing Detail** (`listing-detail.html`)
   - Full property info
   - S3 images displayed
   - All enriched data
   - Purchase report CTA

5. **Report** (PDF, if purchased)
   - Downloaded from S3/CloudFront
   - Comprehensive property analysis

---

## 🔄 Data Freshness

### Listing Updates

```
Estate Agent Updates Listing
        ↓
24 hours pass
        ↓
Scraper runs automatically
        ↓
Detects changes (price, description)
        ↓
Updates listings_raw
        ↓
Re-enriches (if needed)
        ↓
Customer sees updated data
```

### New Listings

```
New property listed on Foxtons
        ↓
Scraper runs next day
        ↓
Downloads new listing + images
        ↓
Matches to property database
        ↓
Enriches with all data
        ↓
Appears in customer searches immediately
```

---

## 💾 Storage Separation

### Backend (Hidden from Customers)

```
Database:
├── listings_raw           # Scraped data
├── properties             # Base UPRN database
├── agents                 # Scraper configs

S3:
└── uk-property-images/
    └── images/            # Raw scraped images
```

### Frontend (Customer-Facing)

```
API:
├── /api/search           # Search enriched listings
├── /api/listing/{id}     # Get enriched data
└── /api/purchase-report  # Generate PDF

S3 (via API):
└── Images served through listing detail page
```

---

## 🚀 Deployment Architecture

### Backend Services (AWS)

```
┌──────────────────────────────────────────────┐
│  Lambda (Scheduled)                          │
│  Run scraper daily at 2 AM                   │
│  ↓                                            │
│  Downloads listings → S3                     │
│  Stores in RDS PostgreSQL                    │
└──────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│  Lambda (Triggered)                          │
│  Runs matching & enrichment                  │
│  ↓                                            │
│  Populates listings_enriched                 │
└──────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│  RDS PostgreSQL                              │
│  - properties                                │
│  - listings_raw                              │
│  - listings_enriched (← SEARCH THIS)         │
└──────────────────────────────────────────────┘
```

### Frontend Services

```
┌──────────────────────────────────────────────┐
│  CloudFront                                  │
│  Serves: property-search.html, etc.         │
└──────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│  API Gateway + ECS (FastAPI)                 │
│  - POST /api/search                          │
│  - GET /api/listing/{id}                     │
│  - POST /api/purchase-report                 │
└──────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────────────────────┐
│  RDS PostgreSQL                              │
│  Query: listings_enriched                    │
└──────────────────────────────────────────────┘
```

---

## 📊 Data Flow Summary

| Component | Purpose | Frequency | Visibility |
|-----------|---------|-----------|------------|
| **Scraper** | Fetch listings from agents | Daily (2 AM) | Backend only |
| **S3 Images** | Store property photos | On scrape | Served via API |
| **Matching** | Link listings to properties | Auto (after scrape) | Backend only |
| **Enrichment** | Add all property data | Auto (after match) | Backend only |
| **listings_enriched** | Search-ready listings | Always current | Queried by API |
| **Search API** | Customer searches | On-demand | Public endpoint |
| **Listing API** | Property details | On-demand | Public endpoint |
| **Report API** | £5 detailed report | On purchase | Authenticated |

---

## 🎯 Key Separation Points

### Customers NEVER See:
- ❌ Raw scraping code
- ❌ `listings_raw` table
- ❌ Matching algorithms
- ❌ S3 bucket structure
- ❌ Feature store queries

### Customers ONLY See:
- ✅ Clean search interface
- ✅ Enriched listing data (via API)
- ✅ S3 images (via listing detail)
- ✅ Match scores
- ✅ PDF reports (if purchased)

---

## 🔐 Security

### Backend
- Environment variables for S3 keys
- Database credentials in Parameter Store
- Lambda execution roles (minimal permissions)

### Frontend
- CORS restricted to portal domain
- No sensitive data in HTML/JS
- Stripe tokenization (client-side)
- API rate limiting

---

## 📈 Scaling Strategy

### Current (Prototype)
- Single scraper instance
- RDS PostgreSQL (single AZ)
- Synchronous enrichment

### Production (10k listings)
- Parallel scraping (Celery workers)
- RDS Multi-AZ with read replicas
- Background enrichment (SQS queue)
- ElastiCache for search results

### Scale (100k+ listings)
- Distributed scraping (Lambda per agent)
- Aurora PostgreSQL Serverless
- OpenSearch for search queries
- CloudFront + S3 for images

---

## ✅ Current Status

- ✅ Backend scraping system: **COMPLETE**
- ✅ Frontend portal: **COMPLETE**
- ✅ API integration: **COMPLETE**
- ✅ S3 storage: **COMPLETE**
- ✅ Documentation: **COMPLETE**

**Ready for**:
1. Load UK property database (UPRNs)
2. Run live scraper (Foxtons, etc.)
3. Deploy to AWS
4. Launch to customers!

---

The systems are **separate but automated**:
- Backend runs 24/7 scraping & enriching
- Frontend queries the always-up-to-date enriched data
- Customers never see the complexity! 🎉

