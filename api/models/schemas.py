"""
Pydantic models for API requests/responses
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict


# =====================================================
# ENUMS
# =====================================================

class PropertyType(str, Enum):
    DETACHED = "detached"
    SEMI_DETACHED = "semi_detached"
    TERRACED = "terraced"
    FLAT = "flat"
    BUNGALOW = "bungalow"
    MAISONETTE = "maisonette"


class EPCRating(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"


class FloodRisk(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ListingStatus(str, Enum):
    ACTIVE = "active"
    UNDER_OFFER = "under_offer"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"


# =====================================================
# QUESTIONNAIRE MODELS
# =====================================================

class LocationConstraint(BaseModel):
    """Location preferences in questionnaire"""
    postcode_areas: Optional[List[str]] = Field(
        None,
        description="List of postcode areas, e.g. ['SW1', 'W1', 'NW3']"
    )
    radius_km: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Search radius from postcode areas in km"
    )
    target_airports: Optional[List[str]] = Field(
        None,
        description="IATA codes, e.g. ['LHR', 'LGW']"
    )
    max_distance_to_airport_km: Optional[float] = Field(
        None,
        ge=0,
        le=50,
        description="Maximum distance to target airports"
    )


class PreferenceWeights(BaseModel):
    """Soft preference weights (must sum to <= 1.0)"""
    schools: float = Field(0.0, ge=0, le=1, description="School quality importance")
    commute: float = Field(0.0, ge=0, le=1, description="Commute/transport importance")
    safety: float = Field(0.0, ge=0, le=1, description="Low crime importance")
    energy: float = Field(0.0, ge=0, le=1, description="EPC rating importance")
    value: float = Field(0.0, ge=0, le=1, description="Undervalued property importance")
    conservation: float = Field(0.0, ge=0, le=1, description="Conservation area preference")

    @validator('conservation', 'value', 'energy', 'safety', 'commute', 'schools')
    def check_sum(cls, v, values):
        """Ensure weights don't exceed 1.0 in total"""
        total = sum(values.values()) + v
        if total > 1.0:
            raise ValueError(f"Total preference weights cannot exceed 1.0 (current: {total})")
        return v


class Questionnaire(BaseModel):
    """User questionnaire for property search"""

    # Hard filters
    budget_min: Optional[Decimal] = Field(None, ge=0, description="Minimum budget in GBP")
    budget_max: Decimal = Field(..., gt=0, description="Maximum budget in GBP")
    bedrooms_min: int = Field(1, ge=1, le=10, description="Minimum bedrooms")
    bedrooms_max: Optional[int] = Field(None, ge=1, le=10, description="Maximum bedrooms")
    property_types: Optional[List[PropertyType]] = Field(
        None,
        description="Preferred property types"
    )

    # Location
    location: LocationConstraint = Field(..., description="Location constraints")

    # Soft preferences (weights)
    preferences: PreferenceWeights = Field(
        default_factory=PreferenceWeights,
        description="Importance weights for soft criteria"
    )

    # Additional filters
    min_epc_rating: Optional[EPCRating] = Field(
        None,
        description="Minimum EPC rating (if energy is important)"
    )
    must_be_in_conservation_area: bool = Field(
        False,
        description="Only show properties in conservation areas"
    )
    exclude_flood_risk: Optional[List[FloodRisk]] = Field(
        None,
        description="Exclude these flood risk levels"
    )

    # Metadata
    user_id: Optional[str] = Field(None, description="User identifier")


# =====================================================
# LISTING RESPONSE MODELS
# =====================================================

class ListingSummary(BaseModel):
    """Listing summary for search results"""
    listing_id: int
    title: str
    price: Decimal
    bedrooms: int
    bathrooms: Optional[int]
    property_type: Optional[str]
    address: str
    postcode: str

    # Location
    latitude: float
    longitude: float

    # Image
    image_url: Optional[str] = Field(None, description="Primary image URL (S3 or external)")

    # Key enriched features
    epc_rating: Optional[str]
    epc_score: Optional[int]
    in_conservation_area: bool
    school_quality_score: Optional[Decimal]
    distance_to_nearest_airport_m: Optional[int]
    imd_decile: Optional[int]

    # AVM
    avm_estimate: Optional[Decimal]
    avm_value_delta_pct: Optional[Decimal] = Field(
        None,
        description="Price vs AVM delta as percentage"
    )
    is_undervalued: bool

    # Match score
    match_score: float = Field(..., ge=0, le=1, description="Overall match score for user preferences")

    # Agent
    agent_name: str
    listing_url: str
    listed_date: Optional[date]

    model_config = ConfigDict(from_attributes=True)


class ListingDetail(ListingSummary):
    """Full listing details (free tier)"""
    description: Optional[str]
    tenure: Optional[str]

    # Additional enrichment
    distance_to_nearest_primary_m: Optional[int]
    distance_to_nearest_secondary_m: Optional[int]
    distance_to_nearest_station_m: Optional[int]
    nearest_airport_code: Optional[str]

    crime_rate_percentile: Optional[int]
    flood_risk: Optional[str]
    max_download_speed_mbps: Optional[int]

    planning_constraints: Optional[Dict[str, Any]]
    recent_planning_apps: int = 0

    # AVM confidence
    avm_confidence_score: Optional[Decimal]
    avm_confidence_interval_lower: Optional[Decimal]
    avm_confidence_interval_upper: Optional[Decimal]

    enriched_at: Optional[datetime]


class SearchResponse(BaseModel):
    """Response for /search endpoint"""
    search_id: int
    total_results: int
    results: List[ListingSummary]

    # Search metadata
    filters_applied: Dict[str, Any]
    preference_weights: PreferenceWeights


# =====================================================
# REPORT MODELS
# =====================================================

class ReportPurchaseRequest(BaseModel):
    """Request to purchase a property report"""
    listing_id: int
    user_id: str
    payment_method_id: str = Field(..., description="Stripe payment method ID")


class ReportPurchaseResponse(BaseModel):
    """Response after purchasing report"""
    report_id: int
    payment_intent_id: str
    payment_status: str
    report_url: Optional[str] = Field(
        None,
        description="CloudFront URL to download PDF (available when payment succeeds)"
    )
    amount_gbp: Decimal


# =====================================================
# INTERNAL MODELS (for enrichment pipeline)
# =====================================================

class PropertyFeatures(BaseModel):
    """Feature vector for a property (from feature store)"""
    property_id: int
    uprn: int

    # EPC
    epc_rating: Optional[str]
    epc_score: Optional[int]
    epc_potential_rating: Optional[str]
    epc_co2_emissions_current: Optional[Decimal]
    epc_energy_consumption_current: Optional[Decimal]

    # Conservation
    in_conservation_area: bool = False
    conservation_area_name: Optional[str]

    # Planning
    planning_constraints: Dict[str, Any] = {}
    recent_planning_apps: int = 0
    planning_refusals: int = 0

    # Schools
    school_quality_score: Optional[Decimal]
    distance_to_nearest_primary_m: Optional[int]
    distance_to_nearest_secondary_m: Optional[int]

    # Transport
    distance_to_nearest_station_m: Optional[int]
    distance_to_nearest_airport_m: Optional[int]
    nearest_airport_code: Optional[str]

    # Area quality
    imd_decile: Optional[int]
    crime_rate_percentile: Optional[int]
    flood_risk: Optional[str]
    max_download_speed_mbps: Optional[int]


class AVMEstimate(BaseModel):
    """AVM valuation result"""
    property_id: int
    estimate: Decimal
    confidence_interval_lower: Decimal
    confidence_interval_upper: Decimal
    confidence_score: Decimal = Field(..., ge=0, le=1)

    # Comparable properties used
    comparable_count: int = 0
    comparables: List[Dict[str, Any]] = []


class MatchedListing(BaseModel):
    """A raw listing matched to a property"""
    raw_listing_id: int
    property_id: int
    match_confidence: Decimal
    match_method: str
