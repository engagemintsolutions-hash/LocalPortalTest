# Quick Start Guide

Get the UK Property Search Engine prototype running locally in 10 minutes.

## Prerequisites

- Docker & Docker Compose (recommended)
- OR: Python 3.11+, PostgreSQL 15+, Redis

## Option 1: Docker Compose (Recommended)

### 1. Clone and Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials (for S3 feature data)
# Minimum required:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - FEATURE_S3_BUCKET
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, API)
docker-compose up -d

# View logs
docker-compose logs -f api
```

### 3. Initialize Database

```bash
# The schema is automatically loaded via docker-entrypoint-initdb.d
# But you can manually run migrations if needed:
docker-compose exec api python cli.py init-db
```

### 4. Access API

```bash
# Health check
curl http://localhost:8000/health

# API docs (Swagger UI)
open http://localhost:8000/docs
```

## Option 2: Local Development (Without Docker)

### 1. Setup PostgreSQL

```bash
# Install PostGIS
# On macOS:
brew install postgresql@15 postgis

# On Ubuntu:
sudo apt install postgresql-15 postgresql-15-postgis-3

# Create database
createdb property_search
psql property_search -c "CREATE EXTENSION postgis;"
psql property_search -c "CREATE EXTENSION pg_trgm;"

# Load schema
psql property_search < schema.sql
```

### 2. Setup Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt install redis-server
sudo systemctl start redis
```

### 3. Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL and AWS credentials
```

### 4. Run API

```bash
# Using CLI
python cli.py serve --reload

# Or directly with uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Initial Data Load

Before you can search properties, you need data:

### 1. Load Base Properties

You'll need to load your existing UK property data from S3 into the `properties` table:

```python
# Example script (create as scripts/load_properties.py)
import pandas as pd
from config.database import SessionLocal
from api.models.database import Property

# Load from S3 parquet
df = pd.read_parquet("s3://your-bucket/uk-properties.parquet")

db = SessionLocal()

for _, row in df.iterrows():
    prop = Property(
        uprn=row['uprn'],
        building_number=row['building_number'],
        street=row['street'],
        town_city=row['town'],
        postcode=row['postcode'],
        address_normalised=row['full_address'],
        location=f"SRID=4326;POINT({row['longitude']} {row['latitude']})",
        property_type=row['type']
    )
    db.add(prop)

    if len(db.new) % 1000 == 0:
        db.commit()
        print(f"Loaded {len(db.new)} properties...")

db.commit()
print("Properties loaded!")
```

### 2. Load Reference Data

```bash
# Example: Load airports
psql property_search << EOF
INSERT INTO airports (iata_code, name, location) VALUES
('LHR', 'London Heathrow', ST_GeogFromText('POINT(-0.4543 51.4700)')),
('LGW', 'London Gatwick', ST_GeogFromText('POINT(-0.1903 51.1537)')),
('STN', 'London Stansted', ST_GeogFromText('POINT(0.2350 51.8860)')),
('LTN', 'London Luton', ST_GeogFromText('POINT(-0.3717 51.8747)')),
('LCY', 'London City', ST_GeogFromText('POINT(0.0553 51.5048)');
EOF
```

**TODO**: Load schools from gov.uk edubase data, conservation areas from local authorities.

### 3. Add Sample Agent

```bash
psql property_search << EOF
INSERT INTO agents (name, branch_name, website_url, is_active, scraper_config) VALUES
('Example Estate Agents', 'Central London', 'www.exampleagent.co.uk', true,
 '{"base_url": "https://www.exampleagent.co.uk", "max_pages": 10}'::jsonb);
EOF
```

### 4. Run Ingestion Pipeline

```bash
# Full pipeline: scrape -> match -> enrich
python cli.py pipeline

# Or run steps individually:
python cli.py scrape
python cli.py match
python cli.py enrich
```

## Testing the API

### 1. Search for Properties

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "budget_max": 750000,
    "bedrooms_min": 2,
    "property_types": ["flat"],
    "location": {
      "postcode_areas": ["SW1", "SW3", "SW7"],
      "radius_km": 3
    },
    "preferences": {
      "schools": 0.25,
      "commute": 0.25,
      "safety": 0.2,
      "energy": 0.2,
      "value": 0.1,
      "conservation": 0.0
    }
  }' | jq
```

### 2. Get Listing Details

```bash
# Use listing_id from search results
curl http://localhost:8000/api/listing/1 | jq
```

### 3. Purchase Report (Mock Payment)

```bash
curl -X POST http://localhost:8000/api/listing/1/purchase-report \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 1,
    "user_id": "test_user_123",
    "payment_method_id": "pm_test_visa"
  }' | jq
```

**Note**: The prototype uses mock Stripe payments. In production, use real Stripe payment methods.

## Development Workflow

### Run Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_search.py -v

# With coverage
pytest --cov=api --cov=search --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy api/ search/ enrichment/

# Linting
flake8 api/ search/ enrichment/
```

### Database Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql $DATABASE_URL

# Check PostGIS installed
psql property_search -c "SELECT PostGIS_Version();"
```

### S3 Access Issues

```bash
# Test AWS credentials
aws s3 ls s3://your-feature-bucket/

# Check IAM permissions (need s3:GetObject, s3:ListBucket)
```

### DuckDB S3 Errors

If DuckDB can't read S3:

```python
# Test in Python REPL
import duckdb
con = duckdb.connect()
con.execute("INSTALL httpfs;")
con.execute("LOAD httpfs;")
con.execute("SET s3_region='eu-west-2';")

# Try reading
result = con.execute("SELECT * FROM read_parquet('s3://bucket/file.parquet') LIMIT 1;").fetchall()
print(result)
```

### Report Generation Fails

WeasyPrint requires system libraries:

```bash
# macOS
brew install cairo pango gdk-pixbuf

# Ubuntu
sudo apt install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
```

## Next Steps

1. **Load Real Data**: Import your UK property database into `properties` table
2. **Configure S3**: Ensure S3 buckets have EPC, IMD, planning data in Parquet format
3. **Setup Scrapers**: Implement real agent scrapers or integrate with feeds
4. **Build Frontend**: Create React/Next.js UI for user-facing search
5. **Deploy to AWS**: Use Terraform/CDK to provision infrastructure

## Useful CLI Commands

```bash
# Initialize database
python cli.py init-db

# Run scraping job
python cli.py scrape

# Match unmatched listings
python cli.py match

# Enrich matched listings
python cli.py enrich

# Full pipeline
python cli.py pipeline

# Start API server
python cli.py serve --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Support

For issues or questions:
1. Check logs: `docker-compose logs api`
2. Verify database schema: `psql property_search -c "\dt"`
3. Test feature store: Run DuckDB queries manually
4. Review API errors in Swagger UI

## Production Checklist

Before going to production:

- [ ] Replace web scrapers with official agent feeds
- [ ] Integrate real AVM API
- [ ] Setup real Stripe payment processing
- [ ] Configure CloudFront for report delivery
- [ ] Setup monitoring (CloudWatch, Sentry)
- [ ] Enable API rate limiting
- [ ] Add user authentication (JWT)
- [ ] Configure backup strategy for RDS
- [ ] Setup CI/CD pipeline
- [ ] Load test with realistic data volumes
- [ ] GDPR compliance review
- [ ] Security audit (penetration testing)

Happy searching! 🏠
