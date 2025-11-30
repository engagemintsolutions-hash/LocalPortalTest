"""
Smart API with Real Savills Data & Intelligent Matching

Loads savills_properties.json and does REAL filtering/scoring based on:
- Hard filters (budget, beds, baths, location, tenure)
- Importance-weighted scoring (1-10 scale for each criterion)
- Returns properties ranked by match score
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import List, Dict, Any
import random

app = FastAPI(title="Smart Property Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Savills properties
PROPERTIES = []

def load_properties():
    global PROPERTIES
    if os.path.exists('savills_properties.json'):
        with open('savills_properties.json', 'r', encoding='utf-8') as f:
            PROPERTIES = json.load(f)
        print(f"Loaded {len(PROPERTIES)} Savills properties")

        # Add mock enrichment data to each
        for i, prop in enumerate(PROPERTIES):
            prop['listing_id'] = i + 1
            # Mock enrichment (in real version, from S3 feature store)
            prop['epc_rating'] = random.choice(['A', 'B', 'C', 'D'])
            prop['epc_score'] = random.randint(60, 95)
            prop['in_conservation_area'] = random.choice([True, False])
            prop['school_quality_score'] = round(random.uniform(0.6, 0.95), 2)
            prop['distance_to_nearest_primary_m'] = random.randint(200, 2000)
            prop['distance_to_nearest_station_m'] = random.randint(300, 2500)
            prop['distance_to_nearest_airport_m'] = random.randint(8000, 40000)
            prop['nearest_airport_code'] = random.choice(['LHR', 'LGW', 'STN'])
            prop['imd_decile'] = random.randint(5, 10)
            prop['crime_rate_percentile'] = random.randint(10, 60)
            prop['flood_risk'] = random.choice(['very_low', 'low', 'medium'])
            prop['max_download_speed_mbps'] = random.randint(50, 500)
            prop['planning_refusals'] = random.randint(0, 2)
            prop['avm_estimate'] = prop['price'] * random.uniform(0.92, 1.08) if prop['price'] else None
            prop['is_undervalued'] = prop['avm_estimate'] and prop['price'] and prop['price'] < prop['avm_estimate'] * 0.95
            prop['agent_name'] = 'Savills'
            prop['latitude'] = 51.5 + random.uniform(-0.5, 0.5)
            prop['longitude'] = -0.1 + random.uniform(-0.5, 0.5)
            # Use first image or placeholder
            prop['image_url'] = prop['image_urls'][0] if prop['image_urls'] else 'property-front.jpg'

    else:
        print("WARNING: savills_properties.json not found. Run scrape_savills_bulk.py first!")
        PROPERTIES = []

load_properties()

@app.get("/")
def root():
    return {
        "service": "Smart Property Search API",
        "status": "running",
        "properties_loaded": len(PROPERTIES)
    }

@app.post("/api/search")
def search(request: dict):
    """Smart search with importance-weighted scoring"""

    # Extract filters
    budget_max = request.get('budget_max', float('inf'))
    budget_min = request.get('budget_min', 0)
    beds_min = request.get('bedrooms_min', 0)
    baths_min = request.get('bathrooms_min', 1)
    prop_types = request.get('property_types', [])
    tenure_pref = request.get('tenure_preference', 'any')

    # Extract importance weights
    weights = request.get('importance_weights', {})
    criteria = request.get('criteria', {})

    # Filter properties
    filtered = []

    for prop in PROPERTIES:
        # Hard filters
        if prop['price'] and (prop['price'] > budget_max or prop['price'] < budget_min):
            continue

        if prop['bedrooms'] and prop['bedrooms'] < beds_min:
            continue

        if prop['bathrooms'] and prop['bathrooms'] < baths_min:
            continue

        if prop_types and prop['property_type'] and prop['property_type'] not in prop_types:
            continue

        if tenure_pref == 'freehold' and prop.get('tenure') != 'freehold':
            continue

        # Criteria filters (hard if importance > 0)
        if criteria.get('max_station_dist_m') and weights.get('station', 0) > 0.7:
            if prop['distance_to_nearest_station_m'] > criteria['max_station_dist_m']:
                continue

        if criteria.get('min_imd_decile') and weights.get('imd', 0) > 0.5:
            if prop['imd_decile'] < criteria['min_imd_decile']:
                continue

        if criteria.get('max_flood_risk') and weights.get('flood', 0) > 0.5:
            flood_order = {'very_low': 1, 'low': 2, 'medium': 3, 'high': 4}
            max_acceptable = flood_order.get(criteria['max_flood_risk'], 4)
            prop_flood = flood_order.get(prop['flood_risk'], 4)
            if prop_flood > max_acceptable:
                continue

        # Passed all filters
        filtered.append(prop)

    # Score each property based on importance weights
    for prop in filtered:
        score = calculate_match_score(prop, weights, criteria)
        prop['match_score'] = score

    # Sort by score
    filtered.sort(key=lambda x: x['match_score'], reverse=True)

    # Return top results
    results = filtered[:100]

    return {
        "search_id": random.randint(1000, 9999),
        "total_results": len(results),
        "results": results,
        "filters_applied": request,
        "preference_weights": weights
    }


def calculate_match_score(prop: dict, weights: dict, criteria: dict) -> float:
    """
    Calculate match score (0-1) based on importance weights

    Each criterion gets a normalized score (0-1), multiplied by its importance weight (0-1)
    Final score = sum of weighted scores / sum of weights
    """
    total_score = 0.0
    total_weight = 0.0

    # Schools (closer & better = higher score)
    if weights.get('schools', 0) > 0:
        school_score = prop.get('school_quality_score', 0.5)
        # Distance bonus
        dist = prop.get('distance_to_nearest_primary_m', 2000)
        if dist < 500:
            school_score = min(1.0, school_score + 0.2)
        elif dist > 2000:
            school_score *= 0.8

        total_score += school_score * weights['schools']
        total_weight += weights['schools']

    # Station proximity
    if weights.get('station', 0) > 0:
        dist = prop.get('distance_to_nearest_station_m', 2000)
        station_score = max(0, 1.0 - (dist / 2000))  # 0m=1.0, 2000m=0.0
        total_score += station_score * weights['station']
        total_weight += weights['station']

    # Airport proximity
    if weights.get('airport', 0) > 0:
        dist = prop.get('distance_to_nearest_airport_m', 50000)
        airport_score = max(0, 1.0 - (dist / 50000))
        total_score += airport_score * weights['airport']
        total_weight += weights['airport']

    # Crime (lower percentile = better)
    if weights.get('crime', 0) > 0:
        crime_pct = prop.get('crime_rate_percentile', 50)
        crime_score = (100 - crime_pct) / 100.0  # Lower crime = higher score
        total_score += crime_score * weights['crime']
        total_weight += weights['crime']

    # IMD (higher decile = better)
    if weights.get('imd', 0) > 0:
        imd = prop.get('imd_decile', 5)
        imd_score = imd / 10.0
        total_score += imd_score * weights['imd']
        total_weight += weights['imd']

    # Flood risk (very_low = best)
    if weights.get('flood', 0) > 0:
        flood = prop.get('flood_risk', 'medium')
        flood_scores = {'very_low': 1.0, 'low': 0.7, 'medium': 0.4, 'high': 0.0}
        flood_score = flood_scores.get(flood, 0.5)
        total_score += flood_score * weights['flood']
        total_weight += weights['flood']

    # EPC (A=best)
    if weights.get('epc', 0) > 0:
        epc_score = prop.get('epc_score', 50) / 100.0
        total_score += epc_score * weights['epc']
        total_weight += weights['epc']

    # Broadband
    if weights.get('broadband', 0) > 0:
        speed = prop.get('max_download_speed_mbps', 0)
        broadband_score = min(1.0, speed / 500.0)  # 500+ Mbps = perfect
        total_score += broadband_score * weights['broadband']
        total_weight += weights['broadband']

    # Conservation area
    if weights.get('conservation', 0) > 0:
        conservation_score = 1.0 if prop.get('in_conservation_area') else 0.0
        total_score += conservation_score * abs(weights['conservation'])
        total_weight += abs(weights['conservation'])

    # Value (undervalued = better)
    if weights.get('value', 0) > 0:
        value_score = 1.0 if prop.get('is_undervalued') else 0.5
        total_score += value_score * weights['value']
        total_weight += weights['value']

    # Planning issues (no refusals = better)
    if weights.get('planning', 0) > 0:
        refusals = prop.get('planning_refusals', 0)
        planning_score = 1.0 if refusals == 0 else 0.5
        total_score += planning_score * weights['planning']
        total_weight += weights['planning']

    # Coast proximity (mock - would calculate from UK coastline data)
    if weights.get('coast', 0) > 0:
        # Mock: properties with certain postcodes are "coastal"
        is_coastal = prop.get('postcode', '').startswith(('BN', 'TR', 'PL', 'TQ'))
        coast_score = 1.0 if is_coastal else 0.3
        total_score += coast_score * weights['coast']
        total_weight += weights['coast']

    # Calculate final score
    if total_weight > 0:
        final_score = total_score / total_weight
    else:
        final_score = 0.5  # Neutral if no weights

    return round(final_score, 2)


@app.get("/api/listing/{listing_id}")
def get_listing(listing_id: int):
    """Get single listing detail"""
    for prop in PROPERTIES:
        if prop.get('listing_id') == listing_id:
            return prop

    return {"error": "Not found"}, 404


if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("SMART API SERVER WITH REAL SAVILLS DATA")
    print("="*60)
    print(f"Loaded: {len(PROPERTIES)} properties")
    print("Running at: http://localhost:8000")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
