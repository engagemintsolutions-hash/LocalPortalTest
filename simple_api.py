"""
Simple FastAPI demo server with mock Savills data
No database required - for testing the questionnaire
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

app = FastAPI(title="Property Search Demo API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Savills properties (from our actual scraping)
MOCK_PROPERTIES = [
    {
        "listing_id": 1,
        "title": "4 bedroom house for sale in Ludlow",
        "price": 1595000,
        "bedrooms": 4,
        "bathrooms": 3,
        "property_type": "house",
        "address": "Elton, Ludlow, Herefordshire",
        "postcode": "SY8 2HQ",
        "latitude": 52.36,
        "longitude": -2.71,
        "image_url": "elegant-1498629.jpg",
        "epc_rating": "B",
        "epc_score": 82,
        "in_conservation_area": False,
        "school_quality_score": 0.85,
        "distance_to_nearest_airport_m": 85000,
        "imd_decile": 8,
        "avm_estimate": 1520000,
        "avm_value_delta_pct": 4.9,
        "is_undervalued": False,
        "agent_name": "Savills",
        "listing_url": "https://search.savills.com/property-detail/gbwmrstes250098",
        "listed_date": "2024-11-15"
    },
    {
        "listing_id": 2,
        "title": "5 bedroom house for sale in Chelsea",
        "price": 2250000,
        "bedrooms": 5,
        "bathrooms": 4,
        "property_type": "house",
        "address": "Chelsea, London",
        "postcode": "SW3 5EZ",
        "latitude": 51.48,
        "longitude": -0.17,
        "image_url": "property-front.jpg",
        "epc_rating": "C",
        "epc_score": 75,
        "in_conservation_area": True,
        "school_quality_score": 0.92,
        "distance_to_nearest_airport_m": 12000,
        "imd_decile": 9,
        "avm_estimate": 2100000,
        "avm_value_delta_pct": -7.1,
        "is_undervalued": True,
        "agent_name": "Savills",
        "listing_url": "https://search.savills.com/property-detail/gbbsrsbrs250052",
        "listed_date": "2024-11-20"
    },
    {
        "listing_id": 3,
        "title": "3 bedroom flat for sale in Kensington",
        "price": 875000,
        "bedrooms": 3,
        "bathrooms": 2,
        "property_type": "flat",
        "address": "Kensington, London",
        "postcode": "W8 6SH",
        "latitude": 51.50,
        "longitude": -0.19,
        "image_url": "elegant-1498629.jpg",
        "epc_rating": "B",
        "epc_score": 84,
        "in_conservation_area": False,
        "school_quality_score": 0.88,
        "distance_to_nearest_airport_m": 15000,
        "imd_decile": 10,
        "avm_estimate": 850000,
        "avm_value_delta_pct": 2.9,
        "is_undervalued": False,
        "agent_name": "Savills",
        "listing_url": "https://search.savills.com/property-detail/gbsurdsnd180035",
        "listed_date": "2024-11-18"
    }
]

@app.get("/")
def root():
    return {"service": "Property Search Demo API", "status": "running"}

@app.post("/api/search")
def search(data: dict):
    """Mock search endpoint - returns all properties"""
    # In real version, this would filter and score
    # For demo, just return mock properties with mock scores

    results = []
    for i, prop in enumerate(MOCK_PROPERTIES):
        prop_copy = prop.copy()
        # Add mock match score (decreasing)
        prop_copy['match_score'] = 0.92 - (i * 0.05)
        results.append(prop_copy)

    return {
        "search_id": 1,
        "total_results": len(results),
        "results": results,
        "filters_applied": data,
        "preference_weights": data.get('preferences', {})
    }

@app.get("/api/listing/{listing_id}")
def get_listing(listing_id: int):
    """Get single listing detail"""
    for prop in MOCK_PROPERTIES:
        if prop['listing_id'] == listing_id:
            # Add extra detail fields
            detail = prop.copy()
            detail['description'] = "A hugely impressive family home, finished to a fabulous standard set in acres with stunning gardens."
            detail['tenure'] = "freehold"
            detail['distance_to_nearest_primary_m'] = 850
            detail['distance_to_nearest_secondary_m'] = 1200
            detail['distance_to_nearest_station_m'] = 2400
            detail['nearest_airport_code'] = "LHR"
            detail['crime_rate_percentile'] = 15
            detail['flood_risk'] = "very_low"
            detail['max_download_speed_mbps'] = 350
            detail['planning_constraints'] = {}
            detail['recent_planning_apps'] = 0
            detail['avm_confidence_score'] = 0.88
            detail['avm_confidence_interval_lower'] = detail['avm_estimate'] * 0.95
            detail['avm_confidence_interval_upper'] = detail['avm_estimate'] * 1.05
            detail['enriched_at'] = "2024-11-30T12:00:00"
            detail['match_score'] = 0
            return detail

    return {"error": "Not found"}, 404

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("DEMO API SERVER STARTING")
    print("="*60)
    print("Running at: http://localhost:8000")
    print("Try: http://localhost:8000/api/search (POST)")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
