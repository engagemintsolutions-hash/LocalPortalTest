"""
Search scoring engine.

Takes a user questionnaire and computes match scores for listings.

Scoring approach:
1. Apply hard filters (budget, beds, location)
2. For each passing listing, compute normalized scores (0-1) for soft preferences
3. Weight and aggregate to final match_score
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from api.models.database import ListingEnriched, Agent
from api.models.schemas import Questionnaire, ListingSummary, PreferenceWeights

logger = logging.getLogger(__name__)


class ListingScorer:
    """Computes match scores for listings given user preferences"""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        questionnaire: Questionnaire,
        limit: int = 100,
        offset: int = 0
    ) -> List[ListingSummary]:
        """
        Search for listings matching questionnaire.

        Args:
            questionnaire: User preferences
            limit: Max results
            offset: Pagination offset

        Returns:
            List of ListingSummary with match_score
        """
        # Build query with hard filters
        query = self._build_query(questionnaire)

        # Fetch listings
        listings = query.limit(limit).offset(offset).all()

        # Compute scores
        results = []
        for listing, agent in listings:
            score = self._compute_match_score(listing, questionnaire.preferences)
            summary = self._to_listing_summary(listing, agent, score)
            results.append(summary)

        # Sort by score descending
        results.sort(key=lambda x: x.match_score, reverse=True)

        return results

    def _build_query(self, q: Questionnaire):
        """Build SQL query with hard filters"""

        filters = [
            ListingEnriched.status == 'active'
        ]

        # Budget
        if q.budget_max:
            filters.append(ListingEnriched.price <= q.budget_max)
        if q.budget_min:
            filters.append(ListingEnriched.price >= q.budget_min)

        # Bedrooms
        if q.bedrooms_min:
            filters.append(ListingEnriched.bedrooms >= q.bedrooms_min)
        if q.bedrooms_max:
            filters.append(ListingEnriched.bedrooms <= q.bedrooms_max)

        # Property types
        if q.property_types:
            type_values = [pt.value for pt in q.property_types]
            filters.append(ListingEnriched.property_type.in_(type_values))

        # EPC minimum
        if q.min_epc_rating:
            # A=1, B=2, ..., G=7
            epc_order = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
            min_val = epc_order.get(q.min_epc_rating.value, 7)
            filters.append(
                func.coalesce(
                    func.array_position(
                        ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
                        ListingEnriched.epc_rating
                    ),
                    7
                ) <= min_val
            )

        # Conservation area
        if q.must_be_in_conservation_area:
            filters.append(ListingEnriched.in_conservation_area == True)

        # Flood risk exclusions
        if q.exclude_flood_risk:
            excluded = [fr.value for fr in q.exclude_flood_risk]
            filters.append(~ListingEnriched.flood_risk.in_(excluded))

        # Location filters
        if q.location.postcode_areas:
            # Match postcode prefix (e.g. SW1, W1)
            postcode_filters = [
                ListingEnriched.postcode.like(f"{area}%")
                for area in q.location.postcode_areas
            ]
            filters.append(or_(*postcode_filters))

        # Airport distance (if specified)
        if q.location.target_airports and q.location.max_distance_to_airport_km:
            max_distance_m = q.location.max_distance_to_airport_km * 1000
            filters.append(ListingEnriched.distance_to_nearest_airport_m <= max_distance_m)
            filters.append(
                ListingEnriched.nearest_airport_code.in_(q.location.target_airports)
            )

        # Execute query joining with agent for name and raw listing for images
        from sqlalchemy.orm import joinedload

        query = self.db.query(ListingEnriched, Agent).join(
            Agent, Agent.agent_id == ListingEnriched.agent_id
        ).options(
            joinedload(ListingEnriched.raw_listing)  # Eagerly load for image URLs
        ).filter(and_(*filters))

        return query

    def _compute_match_score(
        self,
        listing: ListingEnriched,
        weights: PreferenceWeights
    ) -> float:
        """
        Compute overall match score (0-1) for a listing.

        For each weighted preference:
        - Compute normalized sub-score (0-1)
        - Multiply by weight
        - Sum to get final score

        If no weights specified, return 0.5 (neutral)
        """
        total_weight = (
            weights.schools +
            weights.commute +
            weights.safety +
            weights.energy +
            weights.value +
            weights.conservation
        )

        if total_weight == 0:
            # No preferences specified, neutral score
            return 0.5

        score = 0.0

        # 1. Schools (higher score = better)
        if weights.schools > 0 and listing.school_quality_score:
            school_score = float(listing.school_quality_score)
            score += school_score * float(weights.schools)

        # 2. Commute/Transport (lower distance = better)
        if weights.commute > 0:
            commute_score = self._normalize_distance_score(
                listing.distance_to_nearest_station_m,
                max_acceptable=2000  # 2km
            )
            score += commute_score * float(weights.commute)

        # 3. Safety (higher IMD decile, lower crime percentile = better)
        if weights.safety > 0:
            safety_score = 0.0
            components = 0

            if listing.imd_decile:
                # IMD decile 1-10, 10 = least deprived
                safety_score += listing.imd_decile / 10.0
                components += 1

            if listing.crime_rate_percentile is not None:
                # Crime percentile 0-100, lower = less crime
                safety_score += (100 - listing.crime_rate_percentile) / 100.0
                components += 1

            if components > 0:
                score += (safety_score / components) * float(weights.safety)

        # 4. Energy (EPC rating)
        if weights.energy > 0 and listing.epc_score:
            # EPC score 1-100, higher = better
            energy_score = listing.epc_score / 100.0
            score += energy_score * float(weights.energy)

        # 5. Value (undervalued properties)
        if weights.value > 0 and listing.avm_value_delta_pct is not None:
            # Negative delta = undervalued (good)
            # -10% or more = score 1.0
            # 0% = score 0.5
            # +10% or more = score 0.0
            delta = float(listing.avm_value_delta_pct)
            if delta <= -10:
                value_score = 1.0
            elif delta >= 10:
                value_score = 0.0
            else:
                # Linear scale from -10% to +10%
                value_score = 0.5 - (delta / 20.0)

            score += value_score * float(weights.value)

        # 6. Conservation area preference
        if weights.conservation > 0:
            conservation_score = 1.0 if listing.in_conservation_area else 0.0
            score += conservation_score * float(weights.conservation)

        # Normalize by total weight
        final_score = score / float(total_weight)

        return round(final_score, 2)

    @staticmethod
    def _normalize_distance_score(distance_m: Optional[int], max_acceptable: int) -> float:
        """
        Normalize distance to 0-1 score.

        0m = 1.0 (perfect)
        max_acceptable = 0.0
        """
        if distance_m is None:
            return 0.5  # Unknown, neutral

        if distance_m <= 0:
            return 1.0

        if distance_m >= max_acceptable:
            return 0.0

        # Linear decay
        return 1.0 - (distance_m / max_acceptable)

    def _to_listing_summary(
        self,
        listing: ListingEnriched,
        agent: Agent,
        match_score: float
    ) -> ListingSummary:
        """Convert DB model to ListingSummary with match score"""

        # Extract lat/lng from PostGIS geography
        # In SQLAlchemy, we'd need to use ST_Y and ST_X, but for now
        # we'll use placeholder values (in real code, fetch these in query)
        # Placeholder:
        latitude = 51.5074  # London
        longitude = -0.1278

        # Get first image URL from raw listing's S3 images
        image_url = None
        if listing.raw_listing and listing.raw_listing.image_urls:
            # image_urls is a JSONB array in database
            images = listing.raw_listing.image_urls
            if isinstance(images, list) and len(images) > 0:
                image_url = images[0]

        return ListingSummary(
            listing_id=listing.listing_id,
            title=listing.title,
            price=listing.price,
            bedrooms=listing.bedrooms,
            image_url=image_url,
            bathrooms=listing.bathrooms,
            property_type=listing.property_type,
            address=listing.address,
            postcode=listing.postcode,

            latitude=latitude,
            longitude=longitude,

            epc_rating=listing.epc_rating,
            epc_score=listing.epc_score,
            in_conservation_area=listing.in_conservation_area,
            school_quality_score=listing.school_quality_score,
            distance_to_nearest_airport_m=listing.distance_to_nearest_airport_m,
            imd_decile=listing.imd_decile,

            avm_estimate=listing.avm_estimate,
            avm_value_delta_pct=listing.avm_value_delta_pct,
            is_undervalued=listing.is_undervalued or False,

            match_score=match_score,

            agent_name=agent.name,
            listing_url=f"https://{agent.website_url}/property/{listing.listing_id}",  # Placeholder
            listed_date=listing.listed_date
        )
