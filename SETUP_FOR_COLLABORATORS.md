# Setup Guide for Collaborators

## Quick Start (5 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/engagemintsolutions-hash/LocalPortalTest.git
cd LocalPortalTest
```

### 2. Install Python Dependencies
```bash
pip install fastapi uvicorn pydantic requests beautifulsoup4 boto3
```

### 3. Start the Frontend
```bash
cd frontend
python -m http.server 8080
```
Leave this terminal running.

### 4. Start the Backend API (New Terminal)
```bash
cd ..
python smart_api.py
```
Leave this terminal running.

### 5. Open the Portal
Open your browser to:
```
http://localhost:8080/questionnaire-expanded.html
```

## What You'll See

- **8-step questionnaire** with importance sliders (1-10)
- **50 real Savills properties** with images
- **Intelligent matching** based on your preferences
- **£5 paywall** demonstration

## Files Overview

```
LocalPortalTest/
├── frontend/                    # Frontend files
│   ├── questionnaire-expanded.html   # Main questionnaire (8 steps)
│   ├── questionnaire-expanded.js     # JavaScript logic
│   ├── questionnaire-wizard.css      # Doorstep-branded styles
│   ├── professional-report.html      # £5 report page
│   └── [Doorstep website files]      # Original site
├── smart_api.py                 # Backend API with real Savills data
├── savills_properties.json      # 50 scraped properties (976 images)
├── ingestion/                   # Scraping system
│   └── scrapers/
│       └── savills_scraper.py   # Working Savills scraper
├── schema.sql                   # Database schema (for future)
└── requirements.txt             # Full Python dependencies

```

## Testing the System

### Fill Out Questionnaire

**Example inputs:**

- **Budget**: £2,000,000
- **Bedrooms**: 4
- **Bathrooms**: 2+
- **Property Type**: Detached, Semi-Detached
- **Location**: "London" or "SW1"
- **Schools importance**: 7/10
- **Transport importance**: 8/10
- **Crime importance**: 9/10
- **EPC importance**: 6/10
- **Value importance**: 5/10

### See Results

- 50 Savills properties ranked by match score
- Properties with high importance factors score higher
- Click any property → Professional report
- £5 paywall appears
- Click "Purchase" → Full enriched data revealed

## AWS Credentials (Optional)

If you want to scrape more properties or upload images to S3:

1. Get AWS credentials from project admin
2. Create `.env` file:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=eu-west-2
```

## Scrape More Properties

```bash
python scrape_savills_bulk.py
```

This will scrape 50 more properties with images and save to `savills_properties.json`.

## Troubleshooting

### Port 8080 already in use
```bash
# Kill the process
taskkill //F //IM python.exe

# Or use different port
python -m http.server 8081
```

### Port 8000 already in use
```bash
# Kill and restart
taskkill //F //IM python.exe
python smart_api.py
```

### No properties showing
- Check `savills_properties.json` exists in root directory
- Restart the smart_api.py
- Check browser console for errors (F12)

## Next Steps

1. **Test the current system** - works immediately
2. **Add real S3 data** - connect to EPC/IMD/planning buckets
3. **Deploy to production** - AWS ECS + RDS
4. **Add more estate agents** - replicate Savills scraper

## Support

- GitHub Issues: https://github.com/engagemintsolutions-hash/LocalPortalTest/issues
- Contact: Project admin

---

Everything should work out of the box! Just run steps 1-5 above. 🚀
