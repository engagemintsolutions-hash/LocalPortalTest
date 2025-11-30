# UK Property Search Engine - Prototype

A prototype property search platform that enriches estate agent listings with comprehensive UK property data, AVM valuations, and generates detailed property reports.

## Architecture Overview

### Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 15+ with PostGIS extension
- **Feature Store**: DuckDB querying S3 Parquet files
- **Search**: PostgreSQL full-text search with GIN indexes
- **Task Queue**: Celery + Redis
- **Report Generation**: Jinja2 + WeasyPrint
- **Infrastructure**: AWS (S3, RDS, ECS, Lambda)

### Key Components

1. **Ingestion Pipeline** (`ingestion/`)
   - S3 feature loader (EPC, planning, IMD, etc.)
   - Web scrapers for estate agent listings (prototype only)
   - Orchestrator for scheduled scraping

2. **Matching Engine** (`matching/`)
   - Address normalisation and matching
   - UPRN, postcode+number, and fuzzy matching strategies

3. **Enrichment Engine** (`enrichment/`)
   - Joins feature store data with matched listings
   - Geospatial calculations (schools, airports, stations)
   - Mock AVM integration

4. **Search & Scoring** (`search/`)
   - Hard filters (budget, beds, location)
   - Soft preference scoring (schools, safety, energy, value)
   - Weighted match score aggregation

5. **API** (`api/`)
   - `/api/search` - Property search with questionnaire
   - `/api/listing/{id}` - Free listing details
   - `/api/listing/{id}/purchase-report` - £5 report purchase

6. **Report Generation** (`reports/`)
   - HTML templating with Jinja2
   - PDF conversion with WeasyPrint
   - S3 storage + CloudFront delivery

## Project Structure

```
.
├── api/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── database.py         # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic request/response models
│   └── routers/
│       ├── search.py           # Search endpoint
│       ├── listings.py         # Listing details endpoint
│       └── reports.py          # Report purchase endpoint
├── ingestion/
│   ├── loaders/
│   │   └── s3_feature_loader.py  # DuckDB S3 feature store
│   └── scrapers/
│       ├── base_scraper.py     # Base scraper class
│       ├── example_agent_scraper.py  # Example implementation
│       └── orchestrator.py     # Scraping job coordinator
├── matching/
│   └── matchers/
│       └── address_matcher.py  # Address matching logic
├── enrichment/
│   └── enricher.py             # Listing enrichment engine
├── search/
│   └── scorer.py               # Search and scoring logic
├── reports/
│   ├── generator.py            # PDF report generator
│   └── templates/
│       └── property_report.html  # Report HTML template
├── config/
│   └── database.py             # DB connection management
├── schema.sql                  # PostgreSQL schema
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variables template
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Redis (for Celery)
- AWS credentials (for S3 access)

### 2. Database Setup

```bash
# Create database
createdb property_search

# Install PostGIS extension
psql property_search -c "CREATE EXTENSION postgis;"
psql property_search -c "CREATE EXTENSION pg_trgm;"

# Run schema
psql property_search < schema.sql
```

### 3. Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
# - DATABASE_URL
# - AWS credentials
# - STRIPE_SECRET_KEY (for payments)
# - REDIS_URL
```

### 5. Load Base Property Data

Before running scrapers, you need to populate the `properties` table with base UK property data (UPRNs, addresses, coordinates).

```python
# Example: Load from S3 or local CSV
from config.database import SessionLocal
from api.models.database import Property

# TODO: Implement property loader from your existing S3 data
```

### 6. Populate Reference Tables

Load schools, airports, conservation areas:

```bash
# Example for airports
psql property_search -c "
INSERT INTO airports (iata_code, name, location) VALUES
('LHR', 'London Heathrow', ST_GeogFromText('POINT(-0.4543 51.4700)')),
('LGW', 'London Gatwick', ST_GeogFromText('POINT(-0.1903 51.1537)')),
('STN', 'London Stansted', ST_GeogFromText('POINT(0.2350 51.8860)');
"

# TODO: Load schools from gov.uk data
# TODO: Load conservation areas from local authority data
```

## Running the Application

### API Server

```bash
# Development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production (via Gunicorn)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Scraping Jobs

The scraper is **prototype only** - replace with official agent feeds in production.

```python
# Run scraper manually
from config.database import SessionLocal
from ingestion.scrapers.orchestrator import run_scraping_job

db = SessionLocal()
stats = run_scraping_job(db)
print(stats)
```

For scheduled scraping, deploy as Lambda function or Celery task:

```bash
# Celery worker
celery -A tasks worker --loglevel=info
```

### Enrichment Pipeline

After scraping, run matching and enrichment:

```python
from config.database import SessionLocal
from matching.matchers.address_matcher import match_listing_to_property
from enrichment.enricher import enrich_all_unmatched_listings

db = SessionLocal()

# 1. Match raw listings to properties
from api.models.database import ListingRaw

unmatched = db.query(ListingRaw).filter(
    ListingRaw.matched_property_id.is_(None)
).all()

for raw in unmatched:
    match = match_listing_to_property(db, raw.raw_address, raw.postcode)
    if match:
        raw.matched_property_id = match[0]
        raw.match_confidence = match[1]
        raw.match_method = match[2]

db.commit()

# 2. Enrich matched listings
enrich_all_unmatched_listings(db)
```

## API Usage Examples

### Search Properties

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "budget_max": 500000,
    "bedrooms_min": 2,
    "property_types": ["flat", "terraced"],
    "location": {
      "postcode_areas": ["SW1", "SW3"],
      "radius_km": 5
    },
    "preferences": {
      "schools": 0.3,
      "commute": 0.2,
      "safety": 0.2,
      "energy": 0.2,
      "value": 0.1
    }
  }'
```

### Get Listing Details

```bash
curl http://localhost:8000/api/listing/123
```

### Purchase Report

```bash
curl -X POST http://localhost:8000/api/listing/123/purchase-report \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 123,
    "user_id": "user_xyz",
    "payment_method_id": "pm_card_visa"
  }'
```

## Scoring Algorithm

The match score (0-1) is computed as:

```
match_score = Σ(weight_i × normalised_score_i) / Σ(weight_i)
```

Where:
- **Schools**: Ofsted ratings normalised to 0-1
- **Commute**: Distance to station (closer = higher score)
- **Safety**: IMD decile + crime percentile
- **Energy**: EPC score / 100
- **Value**: AVM delta (undervalued properties score higher)
- **Conservation**: Binary (in area = 1.0)

## Data Sources

### S3 Feature Store (Parquet files)

Expected S3 structure:

```
s3://uk-property-features/
├── epc/*.parquet              # Energy Performance Certificates
├── imd/*.parquet              # Index of Multiple Deprivation
├── flood/*.parquet            # Flood risk data
├── broadband/*.parquet        # Broadband availability
└── planning/*.parquet         # Planning applications
```

Each Parquet file should include `uprn` or `postcode` for joining.

## Production Deployment

### AWS Architecture

1. **API**: ECS Fargate with ALB
2. **Database**: RDS PostgreSQL with Multi-AZ
3. **Scrapers**: Lambda functions (scheduled via EventBridge)
4. **Enrichment**: Batch jobs (Step Functions + Lambda)
5. **Reports**: S3 + CloudFront + signed URLs
6. **Task Queue**: ElastiCache Redis + ECS tasks

### Environment Variables (Production)

Use AWS Systems Manager Parameter Store or Secrets Manager:

```bash
aws ssm put-parameter --name /property-search/database-url --value "..." --type SecureString
aws ssm put-parameter --name /property-search/stripe-key --value "..." --type SecureString
```

### Database Migrations

Use Alembic for schema changes:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

## Known Limitations (Prototype)

1. **Scrapers**: Web scraping is for demonstration only. Replace with:
   - Official agent feeds (XML/JSON)
   - RTDF (Real-Time Data Feed) integration
   - Direct API partnerships

2. **AVM**: Mock implementation. Integrate real AVM:
   - Zoopla/Rightmove APIs
   - Custom ML model (XGBoost, etc.)
   - Third-party valuation providers

3. **Payments**: Stripe integration is stubbed. Implement:
   - Real payment intent creation
   - Webhook handling for payment status
   - Refund logic

4. **Authentication**: No user auth implemented. Add:
   - JWT or session-based auth
   - User registration/login
   - Report access control

5. **Frontend**: This is backend only. Build React/Next.js frontend with:
   - Questionnaire form
   - Map-based search results
   - Listing detail pages
   - Report purchase flow

## Future Enhancements

- [ ] User authentication and saved searches
- [ ] Email alerts for new matching listings
- [ ] Mobile app (React Native)
- [ ] Real-time AVM updates
- [ ] Integration with mortgage calculators
- [ ] Agent dashboard for direct listing uploads
- [ ] Machine learning for better scoring
- [ ] Historical price data and trends

## Contributing

This is a prototype. For production use:
1. Replace scrapers with official feeds
2. Integrate real AVM
3. Add comprehensive tests
4. Implement proper auth
5. Build frontend UI

## License

Proprietary - UK Property Search Engine Prototype
