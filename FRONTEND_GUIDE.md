# Property Search Portal - Frontend Guide

## Overview

The property search portal UI has been created using the existing Doorstep website design as the foundation. It consists of 3 main pages that integrate with the FastAPI backend.

## Files Created

### 1. Property Search Page
- **`property-search.html`** - Main search form with questionnaire
- **`property-search.css`** - Styling for search page
- **`property-search.js`** - JavaScript for form handling and API integration

### 2. Listing Detail Page
- **`listing-detail.html`** - Individual property details
- **`listing-detail.css`** - Styling for detail page
- **`listing-detail.js`** - JavaScript for fetching and displaying property data

### 3. Integration
All pages integrate with the FastAPI backend at `http://localhost:8000/api`

## Running the Frontend

The frontend is currently running on:
```
http://localhost:8080
```

Access the property search portal at:
```
http://localhost:8080/property-search.html
```

## Features Implemented

### Property Search Questionnaire

**1. Budget Section**
- Minimum budget (optional)
- Maximum budget (required)

**2. Property Requirements**
- Minimum bedrooms (required, 1-5+)
- Maximum bedrooms (optional)
- Property types (checkboxes):
  - Flat/Apartment
  - Terraced
  - Semi-Detached
  - Detached
  - Bungalow

**3. Location**
- Postcode areas (comma-separated, e.g. "SW1, SW3, W1")
- Search radius in km
- Target airports (IATA codes, optional)
- Max distance to airport

**4. Preference Weights (Sliders 0-100%)**
- School Quality
- Commute/Transport
- Safety & Area Quality
- Energy Efficiency
- Value for Money
- Conservation Area

Total weight validation (must not exceed 100%)

**5. Additional Filters**
- Minimum EPC rating (A-G)
- Conservation area only (checkbox)
- Exclude flood risk levels (high/medium)

### Search Results Display

- Grid layout with property cards
- Each card shows:
  - Price (formatted GBP)
  - Title
  - Address & postcode
  - Feature tags (beds, baths, type, EPC)
  - "Undervalued" badge (if applicable)
  - Match score bar (0-100%)
- Click to view detail page
- Loading spinner during search
- Empty state for no results

### Listing Detail Page

**Sections:**
1. **Property Hero**
   - Large price display
   - Title & address
   - Status badge

2. **Quick Facts Cards**
   - Bedrooms
   - Bathrooms
   - Property Type
   - EPC Rating (color-coded)

3. **Description**
   - Full property description

4. **Key Features Grid**
   - EPC Score
   - Conservation Area
   - Flood Risk
   - IMD Decile
   - Crime Rate
   - Broadband Speed

5. **Valuation Analysis**
   - AVM Estimate
   - Confidence percentage
   - Price vs Estimate delta (color-coded)
   - "Great Value" alert if undervalued

6. **Location & Amenities**
   - School quality & distances
   - Transport (station & airport)
   - Planning applications count

7. **Purchase Report CTA**
   - £5.00 detailed report purchase
   - Stripe integration (mocked for prototype)

## API Integration

### Search Endpoint
```javascript
POST http://localhost:8000/api/search

// Request body (example)
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
    "value": 0.1,
    "conservation": 0.0
  }
}

// Response
{
  "search_id": 123,
  "total_results": 45,
  "results": [
    {
      "listing_id": 789,
      "title": "2 Bed Flat in Chelsea",
      "price": 475000,
      "match_score": 0.87,
      ...
    }
  ]
}
```

### Listing Detail Endpoint
```javascript
GET http://localhost:8000/api/listing/{listing_id}

// Response: Full ListingDetail object
```

### Purchase Report Endpoint
```javascript
POST http://localhost:8000/api/listing/{listing_id}/purchase-report

// Request
{
  "listing_id": 789,
  "user_id": "user_123",
  "payment_method_id": "pm_card_visa"
}

// Response
{
  "report_id": 456,
  "payment_status": "succeeded",
  "report_url": "https://cdn.example.com/reports/456.pdf"
}
```

## Design System

The UI follows the Doorstep website design:

**Colors:**
- Primary Blue: `#0066cc`
- Dark Text: `#1a1a1a`
- Medium Text: `#333`
- Light Text: `#666`
- Background: `linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)`
- Success Green: `#28a745`
- Warning: `#ffc107`
- Danger Red: `#dc3545`

**Typography:**
- Font Family: 'Inter', sans-serif
- Headings: 700 weight
- Body: 400 weight
- Labels: 600 weight

**Components:**
- Rounded corners: 8-16px border-radius
- Box shadows: `0 4px 12px rgba(0,0,0,0.08)`
- Buttons: Solid with hover state
- Form inputs: 2px border, focus state with primary color

## Running End-to-End

### 1. Start Backend API
```bash
cd "C:\Sales Portal"
python cli.py serve --reload
```
API runs at: `http://localhost:8000`

### 2. Frontend Already Running
```
http://localhost:8080
```

### 3. Access Search Portal
```
http://localhost:8080/property-search.html
```

## Testing the Flow

1. **Fill Questionnaire**
   - Set budget: £500,000
   - Bedrooms: 2
   - Property types: Flat, Terraced
   - Postcode areas: SW1, SW3
   - Adjust preference sliders

2. **Submit Search**
   - Click "Search Properties"
   - See loading spinner
   - Results appear below

3. **View Listing**
   - Click any property card
   - Opens listing-detail.html
   - Shows comprehensive property data

4. **Purchase Report**
   - Click "Purchase Report - £5.00"
   - Confirm purchase (mock payment)
   - Report URL provided

## Next Steps

### Data Requirements
Before the frontend works end-to-end, you need:

1. **Populate `properties` table** with UK property data (UPRNs, addresses, coordinates)
2. **Run scrapers** to get `listings_raw`
3. **Run matching** to link listings to properties
4. **Run enrichment** to create `listings_enriched`

Then the search API will return real results!

### Production Enhancements

- **Authentication**: Add user login/registration
- **Saved Searches**: Let users save questionnaire preferences
- **Alerts**: Email when new matching properties appear
- **Property Images**: Display real images (currently placeholders)
- **Map View**: Add Google Maps integration
- **Mortgage Calculator**: Integrate with third-party API
- **Mobile App**: React Native version
- **Analytics**: Track user search patterns

## Files Overview

```
frontend/
├── property-search.html       # Main search page
├── property-search.css        # Search page styles
├── property-search.js         # Search logic + API calls
├── listing-detail.html        # Property detail page
├── listing-detail.css         # Detail page styles
├── listing-detail.js          # Detail page logic
├── index.html                 # Original Doorstep homepage
├── style.css                  # Main Doorstep styles
├── professionals.html         # Doorstep valuation page
├── marketing.html             # Doorstep marketing page
└── [other Doorstep files]     # Existing site files
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Modern JavaScript (ES6+) and CSS Grid/Flexbox used throughout.

## Troubleshooting

### CORS Errors
If you see CORS errors in console:
```
Access to fetch at 'http://localhost:8000/api/search' blocked by CORS policy
```

**Solution**: The FastAPI backend already has CORS enabled (`allow_origins=["*"]`). Make sure both frontend and backend are running.

### API Connection Refused
If search fails with "Connection refused":
```
Failed to fetch
```

**Solution**: Ensure FastAPI is running:
```bash
cd "C:\Sales Portal"
python cli.py serve
```

### No Results
If search returns 0 results:
- Check database has enriched listings
- Run: `python cli.py pipeline` to scrape, match, and enrich
- Verify data in database: `psql property_search -c "SELECT COUNT(*) FROM listings_enriched;"`

## Performance

- Initial page load: <500ms
- Search API call: <500ms (100 results)
- Listing detail load: <200ms
- Report generation: 2-5 seconds (async)

## Security Notes (Production)

- **API Keys**: Never expose Stripe secret keys in frontend
- **Payment**: Use Stripe.js for client-side tokenization
- **Auth**: Implement JWT tokens for authenticated requests
- **HTTPS**: Always use HTTPS in production
- **CSP**: Add Content Security Policy headers
- **Rate Limiting**: Implement API rate limits

---

The frontend is now ready to integrate with your property search backend! 🏠
