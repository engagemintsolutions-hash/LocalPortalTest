"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.database import get_db
from api.models.schemas import Questionnaire, SearchResponse
from api.models.database import UserSearch
from search.scorer import ListingScorer

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_properties(
    questionnaire: Questionnaire,
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Search for properties matching user preferences.

    Takes a questionnaire with:
    - Hard filters (budget, bedrooms, location, etc.)
    - Soft preference weights (schools, commute, safety, energy, value)

    Returns ranked listings with match scores.
    """

    # Create scorer
    scorer = ListingScorer(db)

    # Execute search
    results = scorer.search(questionnaire, limit=limit, offset=offset)

    # Store search in database for analytics
    search_record = UserSearch(
        user_id=questionnaire.user_id,
        questionnaire_data=questionnaire.model_dump(),
        budget_min=questionnaire.budget_min,
        budget_max=questionnaire.budget_max,
        bedrooms_min=questionnaire.bedrooms_min,
        property_types=[pt.value for pt in questionnaire.property_types] if questionnaire.property_types else None,
        postcode_areas=questionnaire.location.postcode_areas,
        radius_km=questionnaire.location.radius_km,
        max_distance_to_airport_km=questionnaire.location.max_distance_to_airport_km,
        target_airports=questionnaire.location.target_airports,
        weight_schools=questionnaire.preferences.schools,
        weight_commute=questionnaire.preferences.commute,
        weight_safety=questionnaire.preferences.safety,
        weight_energy=questionnaire.preferences.energy,
        weight_value=questionnaire.preferences.value,
        weight_conservation=questionnaire.preferences.conservation,
        results_count=len(results)
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)

    return SearchResponse(
        search_id=search_record.search_id,
        total_results=len(results),
        results=results,
        filters_applied={
            "budget_max": float(questionnaire.budget_max),
            "bedrooms_min": questionnaire.bedrooms_min,
            "property_types": [pt.value for pt in questionnaire.property_types] if questionnaire.property_types else [],
            "postcode_areas": questionnaire.location.postcode_areas or [],
            "min_epc_rating": questionnaire.min_epc_rating.value if questionnaire.min_epc_rating else None
        },
        preference_weights=questionnaire.preferences
    )
