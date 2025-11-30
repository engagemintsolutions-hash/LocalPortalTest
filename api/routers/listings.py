"""
Listings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from api.models.schemas import ListingDetail
from api.models.database import ListingEnriched, Agent

router = APIRouter()


@router.get("/listing/{listing_id}", response_model=ListingDetail)
def get_listing_detail(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """
    Get full listing details (free tier data).

    Returns enriched data including:
    - Basic listing info
    - EPC rating
    - School proximity
    - Transport links
    - Area quality (IMD, crime)
    - AVM estimate and confidence
    - Planning applications count

    Does NOT include:
    - Full planning details
    - Restrictive covenants
    - Detailed reports (requires £5 purchase)
    """

    # Fetch listing with agent
    result = db.query(ListingEnriched, Agent).join(
        Agent, Agent.agent_id == ListingEnriched.agent_id
    ).filter(
        ListingEnriched.listing_id == listing_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")

    listing, agent = result

    # Convert to response model
    # Note: In production, extract lat/lng properly using ST_Y/ST_X
    latitude = 51.5074  # Placeholder
    longitude = -0.1278

    return ListingDetail(
        listing_id=listing.listing_id,
        title=listing.title,
        description=listing.description,
        price=listing.price,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        property_type=listing.property_type,
        tenure=listing.tenure,
        address=listing.address,
        postcode=listing.postcode,

        latitude=latitude,
        longitude=longitude,

        # Enriched data
        epc_rating=listing.epc_rating,
        epc_score=listing.epc_score,
        in_conservation_area=listing.in_conservation_area,

        distance_to_nearest_primary_m=listing.distance_to_nearest_primary_m,
        distance_to_nearest_secondary_m=listing.distance_to_nearest_secondary_m,
        distance_to_nearest_station_m=listing.distance_to_nearest_station_m,
        distance_to_nearest_airport_m=listing.distance_to_nearest_airport_m,
        nearest_airport_code=listing.nearest_airport_code,

        school_quality_score=listing.school_quality_score,
        imd_decile=listing.imd_decile,
        crime_rate_percentile=listing.crime_rate_percentile,
        flood_risk=listing.flood_risk,
        max_download_speed_mbps=listing.max_download_speed_mbps,

        planning_constraints=listing.planning_constraints,
        recent_planning_apps=listing.recent_planning_apps,

        # AVM
        avm_estimate=listing.avm_estimate,
        avm_value_delta_pct=listing.avm_value_delta_pct,
        avm_confidence_score=listing.avm_confidence_score,
        avm_confidence_interval_lower=listing.avm_confidence_interval_lower,
        avm_confidence_interval_upper=listing.avm_confidence_interval_upper,
        is_undervalued=listing.is_undervalued or False,

        # Metadata
        enriched_at=listing.enriched_at,

        # Agent
        agent_name=agent.name,
        listing_url=f"https://{agent.website_url}/property/{listing.listing_id}",
        listed_date=listing.listed_date,

        # Match score placeholder (not applicable for direct fetch)
        match_score=0.0
    )
