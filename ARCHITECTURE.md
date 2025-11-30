# Architecture & Design Document

## System Overview

The UK Property Search Engine is a prototype that enriches estate agent listings with comprehensive property data and provides intelligent matching based on user preferences.

### Revenue Model

- **Free Tier**: Basic search and listing enrichment (EPC, schools, transport, AVM estimate)
- **Paid Tier**: £5 per property for detailed reports (planning history, covenants, detailed analytics)

### Data Flow

```
┌─────────────────┐
│  Estate Agent   │
│    Websites     │
└────────┬────────┘
         │ Scrapers (prototype)
         ▼
┌─────────────────┐
│  listings_raw   │ ◄─── Raw scraped data
└────────┬────────┘
         │ Address Matcher
         ▼
┌─────────────────┐
│   properties    │ ◄─── Base UK property database (S3)
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Feature Store  │◄─────│  S3 Parquet  │
│    (DuckDB)     │      │  (EPC, IMD,  │
└────────┬────────┘      │  Planning)   │
         │               └──────────────┘
         │ Enrichment
         ▼
┌─────────────────┐
│listings_enriched│ ◄─── Fully enriched, search-ready
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Search/Scoring  │ ◄─── User questionnaire
│     Engine      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ranked Results │ ◄─── Match scores
└─────────────────┘
```

## Core Components

### 1. Ingestion Pipeline

**Purpose**: Acquire listing data and load property features

#### Scrapers (`ingestion/scrapers/`)

- **Base Framework**: Abstract `BaseScraper` class with retry logic, rate limiting
- **Agent-Specific**: Each estate agent has custom parser implementation
- **Orchestrator**: Coordinates multi-agent scraping, handles failures
- **Storage**: Upserts to `listings_raw` with conflict handling

**Key Design Decisions**:
- Prototype-only: Real implementation would use agent feeds/APIs
- Config-driven: Agent configs stored in DB `agents.scraper_config` JSONB
- Idempotent: `(agent_id, external_listing_id)` unique constraint

#### Feature Store (`ingestion/loaders/`)

- **DuckDB**: In-memory analytics DB with S3 integration
- **Zero-copy**: Direct queries against Parquet files on S3
- **Views**: Virtual tables over S3 data (EPC, IMD, flood, broadband, planning)
- **Batch queries**: Efficient join operations for bulk enrichment

**S3 Data Structure**:
```
s3://uk-property-features/
├── epc/           # Energy Performance Certificates (gov.uk)
├── imd/           # Index of Multiple Deprivation (ONS)
├── flood/         # EA flood risk data
├── broadband/     # Ofcom broadband availability
└── planning/      # Planning applications (local authorities)
```

### 2. Matching Engine

**Purpose**: Link scraped listings to canonical property records

#### Strategies (in priority order)

1. **UPRN Exact**: If scraper extracts UPRN (rare), use it
   - Confidence: 1.00
   - Method: `uprn_exact`

2. **Postcode + Building Number**: Normalized postcode + extracted number
   - Confidence: 0.95
   - Method: `postcode_number`

3. **Fuzzy Address**: PostgreSQL `pg_trgm` similarity on normalized text
   - Confidence: 0.70-0.95 (based on similarity score)
   - Method: `address_fuzzy`
   - Threshold: 0.7 minimum

**Address Normalization**:
- Lowercase
- Remove punctuation
- Strip common suffixes (street, road, avenue)
- Collapse whitespace

**PostgreSQL Extensions Used**:
- `pg_trgm`: Trigram-based fuzzy matching
- `similarity()` function: Returns 0-1 score

### 3. Enrichment Engine

**Purpose**: Augment matched listings with all available data

#### Data Sources

1. **Feature Store** (DuckDB):
   - EPC rating, score, potential, CO2, energy consumption
   - IMD decile, crime percentile
   - Flood risk level
   - Broadband max speed
   - Planning application counts

2. **PostGIS Queries**:
   - Conservation area containment (`ST_Contains`)
   - Nearest schools with Ofsted ratings (`ST_Distance`)
   - Nearest transport (stations, airports)

3. **AVM** (Mock):
   - Property valuation estimate
   - Confidence interval
   - Comparable properties (future)

#### Derived Metrics

- `school_quality_score`: Average of nearest primary/secondary Ofsted ratings (normalized to 0-1)
- `avm_value_delta_pct`: `(price - avm_estimate) / avm_estimate * 100`
- `is_undervalued`: Flag when delta < -5%

**Storage**: `listings_enriched` table with all denormalized data

### 4. Search & Scoring

**Purpose**: Match user preferences to listings with relevance scores

#### Hard Filters (must satisfy ALL)

- Budget range
- Bedroom count
- Property types
- Location (postcode areas, airport proximity)
- EPC minimum rating
- Conservation area requirement
- Flood risk exclusions

#### Soft Preferences (weighted scoring)

Each listing gets 0-1 scores for:

1. **Schools** (`weight_schools`):
   - Score = `school_quality_score` (Ofsted-based)

2. **Commute** (`weight_commute`):
   - Score = `1 - (distance_to_station_m / 2000)`
   - Closer stations = higher score

3. **Safety** (`weight_safety`):
   - Score = `(imd_decile / 10 + (100 - crime_percentile) / 100) / 2`
   - Higher IMD decile + lower crime = higher score

4. **Energy** (`weight_energy`):
   - Score = `epc_score / 100`
   - Better EPC = higher score

5. **Value** (`weight_value`):
   - Score = `0.5 - (avm_value_delta_pct / 20)`
   - Undervalued properties score higher
   - -10% delta = 1.0, +10% delta = 0.0

6. **Conservation** (`weight_conservation`):
   - Score = `1.0` if in area, `0.0` otherwise

#### Final Score Calculation

```python
match_score = Σ(weight_i × score_i) / Σ(weight_i)
```

Results sorted by `match_score` descending.

### 5. Report Generation

**Purpose**: Generate detailed PDF reports for purchased properties

#### Pipeline

1. **Payment**: Stripe payment intent (£5)
2. **Data Gathering**:
   - All enriched listing data
   - Planning application details (from S3/API)
   - Restrictive covenants (HM Land Registry)
   - Comparable sales (AVM)
3. **Rendering**:
   - Jinja2 template → HTML
   - WeasyPrint → PDF
4. **Storage**:
   - S3 upload with encryption
   - CloudFront signed URL (expiry: 7 days)
5. **Delivery**:
   - URL returned to user
   - Email notification (future)

**Report Sections**:
- Property summary (address, price, characteristics)
- Valuation analysis (AVM, confidence, comparables)
- Energy performance (EPC with potential)
- Planning & legal (history, constraints, covenants)
- Location & amenities (schools, transport)
- Area quality (IMD, crime, flood)

## API Design

### Endpoints

#### `POST /api/search`

**Request**:
```json
{
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
}
```

**Response**:
```json
{
  "search_id": 123,
  "total_results": 45,
  "results": [
    {
      "listing_id": 789,
      "title": "2 Bed Flat in Chelsea",
      "price": 475000,
      "match_score": 0.87,
      "epc_rating": "B",
      "is_undervalued": true,
      ...
    }
  ]
}
```

**Performance**:
- Query: `listings_enriched` with GIN indexes on filters
- Target: <500ms for 100 results

#### `GET /api/listing/{id}`

**Response**: Full `ListingDetail` with all enriched data (free tier)

#### `POST /api/listing/{id}/purchase-report`

**Request**:
```json
{
  "user_id": "user_xyz",
  "payment_method_id": "pm_card_visa"
}
```

**Response**:
```json
{
  "report_id": 456,
  "payment_intent_id": "pi_xxx",
  "payment_status": "succeeded",
  "report_url": "https://cdn.example.com/reports/456.pdf"
}
```

## Database Schema Highlights

### Key Indexes

- `listings_enriched.location` (GIST): Geospatial queries
- `listings_enriched.search_vector` (GIN): Full-text search
- `listings_enriched.postcode` (B-tree): Prefix matching
- Composite: `(status, price, bedrooms, property_type)` for common filters

### Generated Columns

- `search_vector`: Auto-updated tsvector from title/description/address
- `is_undervalued`, `is_overvalued`: Computed from AVM delta

### Materialized View

- `listings_search`: Pre-filtered active listings for faster search
- Refresh strategy: Every 5 minutes or post-enrichment

## Scalability Considerations

### Current (Prototype)

- Single PostgreSQL instance
- In-memory DuckDB
- Synchronous enrichment
- Simple full-text search

### Production Scale (100k+ listings)

1. **Database**:
   - RDS Multi-AZ with read replicas
   - Partition `listings_enriched` by region/postcode prefix
   - Consider TimescaleDB for time-series price data

2. **Search**:
   - Migrate to OpenSearch/Elasticsearch for advanced scoring
   - Use Logstash for real-time indexing
   - Faceted search, geo-radius queries

3. **Enrichment**:
   - Lambda functions for parallel enrichment
   - SQS queue for decoupling
   - Step Functions for orchestration

4. **Caching**:
   - Redis for search results (TTL: 1 hour)
   - CloudFront for static assets
   - API Gateway caching

5. **Monitoring**:
   - CloudWatch metrics
   - X-Ray tracing
   - Sentry for error tracking

## Security & Compliance

### Data Protection

- **PII**: User emails, payment data (Stripe tokenization)
- **Encryption**: At-rest (RDS, S3), in-transit (TLS)
- **Access Control**: IAM roles, least privilege
- **Audit Logs**: CloudTrail, database query logs

### GDPR Compliance

- User data retention policies
- Right to deletion (cascade deletes)
- Data export functionality
- Cookie consent (frontend)

### Payment Security

- PCI DSS: Stripe handles card data
- Payment webhooks validated with signatures
- Refund process for failed reports

## Testing Strategy

### Unit Tests

- Scoring algorithms (`test_scorer.py`)
- Address matching logic
- AVM calculations

### Integration Tests

- API endpoints with test database
- Scraper with mock HTML
- Report generation with fixtures

### E2E Tests

- Full pipeline: scrape → match → enrich → search
- Payment flow with Stripe test mode
- Report generation and S3 upload

## Deployment

### Infrastructure as Code

Use Terraform or AWS CDK:

```
modules/
├── networking/    # VPC, subnets, security groups
├── database/      # RDS, parameter groups
├── compute/       # ECS, Lambda functions
├── storage/       # S3 buckets, lifecycle policies
└── monitoring/    # CloudWatch, alarms
```

### CI/CD Pipeline

1. **GitHub Actions**:
   - Lint (black, mypy)
   - Test (pytest)
   - Build Docker image
   - Push to ECR

2. **Deployment**:
   - Staging: Auto-deploy on `develop` branch
   - Production: Manual approval on `main` branch
   - Blue/green deployment with ALB

### Environment Variables

Managed via AWS Systems Manager Parameter Store:
- `/property-search/database-url`
- `/property-search/stripe-secret-key`
- `/property-search/s3-buckets`

## Future Enhancements

1. **Machine Learning**:
   - Train custom AVM on historical sales
   - Learn user preferences for personalized ranking
   - Predict price drops / good deals

2. **Real-time Updates**:
   - WebSocket for live listing updates
   - Price change alerts via email/push

3. **Advanced Features**:
   - Commute time API integration (Google Maps)
   - School catchment area polygons
   - 3D property tours (integration)
   - Mortgage calculator

4. **Agent Platform**:
   - Direct upload portal for agents
   - Analytics dashboard (views, enquiries)
   - Lead generation (charge per enquiry)

5. **Mobile App**:
   - React Native with map view
   - Saved searches with notifications
   - AR property visualization
