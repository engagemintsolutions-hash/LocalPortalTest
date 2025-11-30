"""
Listing enrichment engine.

Takes a matched raw listing and enriches it with:
- Feature store data (EPC, planning, IMD, etc.)
- Geospatial calculations (distance to schools, airports, stations)
- AVM valuation
- Derived scores and flags
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.models.database import (
    ListingRaw, ListingEnriched, Property, School, Airport, ConservationArea
)
from ingestion.loaders.s3_feature_loader import get_feature_store

logger = logging.getLogger(__name__)


class ListingEnricher:
    """Enriches matched listings with all available data"""

    def __init__(self, db: Session):
        self.db = db
        self.feature_store = get_feature_store()

    def enrich_listing(self, raw_listing_id: int) -> Optional[int]:
        """
        Enrich a single raw listing.

        Args:
            raw_listing_id: ID of raw listing

        Returns:
            listing_id of enriched listing, or None if failed
        """
        # Get raw listing
        raw = self.db.query(ListingRaw).filter(
            ListingRaw.raw_listing_id == raw_listing_id
        ).first()

        if not raw:
            logger.error(f"Raw listing {raw_listing_id} not found")
            return None

        if not raw.matched_property_id:
            logger.warning(f"Raw listing {raw_listing_id} not matched to property")
            return None

        # Get property
        prop = self.db.query(Property).filter(
            Property.property_id == raw.matched_property_id
        ).first()

        if not prop:
            logger.error(f"Property {raw.matched_property_id} not found")
            return None

        try:
            # Gather all enrichment data
            enrichment_data = self._gather_enrichment_data(raw, prop)

            # Create or update enriched listing
            listing_id = self._upsert_enriched_listing(raw, enrichment_data)

            logger.info(f"Enriched listing {raw_listing_id} -> {listing_id}")
            return listing_id

        except Exception as e:
            logger.error(f"Failed to enrich listing {raw_listing_id}: {e}", exc_info=True)
            return None

    def _gather_enrichment_data(self, raw: ListingRaw, prop: Property) -> Dict[str, Any]:
        """Gather all enrichment data for a listing"""

        data = {}

        # 1. Feature store data (EPC, planning, IMD, flood, broadband)
        feature_data = self.feature_store.get_property_features(
            uprn=prop.uprn,
            postcode=prop.postcode
        )
        data.update(feature_data)

        # 2. Conservation area check
        conservation = self._check_conservation_area(prop)
        data.update(conservation)

        # 3. School proximity and quality
        schools = self._calculate_school_metrics(prop)
        data.update(schools)

        # 4. Transport (station, airport)
        transport = self._calculate_transport_metrics(prop)
        data.update(transport)

        # 5. AVM valuation
        avm = self._get_avm_estimate(prop, raw.price_numeric)
        data.update(avm)

        return data

    def _check_conservation_area(self, prop: Property) -> Dict[str, Any]:
        """Check if property is in a conservation area"""

        # PostGIS ST_Contains query
        ca = self.db.query(ConservationArea).filter(
            func.ST_Contains(
                ConservationArea.boundary,
                prop.location
            )
        ).first()

        if ca:
            return {
                'in_conservation_area': True,
                'conservation_area_name': ca.name
            }
        else:
            return {
                'in_conservation_area': False,
                'conservation_area_name': None
            }

    def _calculate_school_metrics(self, prop: Property) -> Dict[str, Any]:
        """Calculate school quality and distance metrics"""

        # Find nearest primary school
        primary = self.db.query(
            School.school_id,
            School.ofsted_rating_score,
            func.ST_Distance(School.location, prop.location).label('distance')
        ).filter(
            School.school_type == 'primary'
        ).order_by(
            func.ST_Distance(School.location, prop.location)
        ).first()

        # Find nearest secondary school
        secondary = self.db.query(
            School.school_id,
            School.ofsted_rating_score,
            func.ST_Distance(School.location, prop.location).label('distance')
        ).filter(
            School.school_type == 'secondary'
        ).order_by(
            func.ST_Distance(School.location, prop.location)
        ).first()

        # Calculate aggregate school quality score (0-1)
        # Average of nearest primary and secondary Ofsted scores (normalized)
        scores = []
        if primary and primary.ofsted_rating_score:
            scores.append(primary.ofsted_rating_score / 4.0)  # 4 = outstanding
        if secondary and secondary.ofsted_rating_score:
            scores.append(secondary.ofsted_rating_score / 4.0)

        school_quality_score = Decimal(str(sum(scores) / len(scores))) if scores else None

        return {
            'school_quality_score': school_quality_score,
            'distance_to_nearest_primary_m': int(primary.distance) if primary else None,
            'distance_to_nearest_secondary_m': int(secondary.distance) if secondary else None
        }

    def _calculate_transport_metrics(self, prop: Property) -> Dict[str, Any]:
        """Calculate distance to nearest station and airports"""

        # Nearest airport
        airport = self.db.query(
            Airport.iata_code,
            func.ST_Distance(Airport.location, prop.location).label('distance')
        ).order_by(
            func.ST_Distance(Airport.location, prop.location)
        ).first()

        # For station, we'd query a stations table (not in schema yet)
        # Placeholder:
        distance_to_station = None  # TODO: implement stations table

        return {
            'distance_to_nearest_station_m': distance_to_station,
            'distance_to_nearest_airport_m': int(airport.distance) if airport else None,
            'nearest_airport_code': airport.iata_code if airport else None
        }

    def _get_avm_estimate(self, prop: Property, listing_price: Optional[Decimal]) -> Dict[str, Any]:
        """
        Get AVM valuation estimate.

        MOCK IMPLEMENTATION: Replace with real AVM API call.
        """
        # Mock AVM - uses listing price with some noise
        if not listing_price:
            return {
                'avm_estimate': None,
                'avm_confidence_interval_lower': None,
                'avm_confidence_interval_upper': None,
                'avm_confidence_score': None,
                'avm_value_delta_pct': None
            }

        # Simulate AVM estimate (±10% of listing price)
        import random
        random.seed(prop.property_id)  # Deterministic for demo

        noise_factor = Decimal(str(random.uniform(0.92, 1.08)))
        estimate = listing_price * noise_factor

        # Confidence interval (±5%)
        ci_lower = estimate * Decimal('0.95')
        ci_upper = estimate * Decimal('1.05')

        # Confidence score (0-1)
        confidence = Decimal(str(random.uniform(0.75, 0.95)))

        # Value delta percentage
        delta_pct = ((listing_price - estimate) / estimate) * 100

        return {
            'avm_estimate': estimate.quantize(Decimal('0.01')),
            'avm_confidence_interval_lower': ci_lower.quantize(Decimal('0.01')),
            'avm_confidence_interval_upper': ci_upper.quantize(Decimal('0.01')),
            'avm_confidence_score': confidence.quantize(Decimal('0.01')),
            'avm_value_delta_pct': delta_pct.quantize(Decimal('0.01'))
        }

    def _upsert_enriched_listing(
        self,
        raw: ListingRaw,
        enrichment_data: Dict[str, Any]
    ) -> int:
        """Create or update enriched listing record"""

        # Check if already enriched
        existing = self.db.query(ListingEnriched).filter(
            ListingEnriched.raw_listing_id == raw.raw_listing_id
        ).first()

        # Get property for location
        prop = self.db.query(Property).filter(
            Property.property_id == raw.matched_property_id
        ).first()

        # Build enriched record
        enriched_values = {
            'raw_listing_id': raw.raw_listing_id,
            'property_id': raw.matched_property_id,
            'agent_id': raw.agent_id,

            # Core listing data
            'title': raw.title or 'Untitled',
            'description': raw.description,
            'price': raw.price_numeric or Decimal('0'),
            'bedrooms': raw.bedrooms or 0,
            'bathrooms': raw.bathrooms,
            'property_type': raw.property_type,
            'tenure': raw.tenure,

            # Address
            'address': prop.address_normalised,
            'postcode': prop.postcode,
            'location': prop.location,

            # Status
            'status': raw.status,
            'listed_date': raw.listed_date,

            # Enriched data
            **enrichment_data
        }

        if existing:
            # Update
            for key, value in enriched_values.items():
                setattr(existing, key, value)
            self.db.commit()
            return existing.listing_id
        else:
            # Insert
            new_listing = ListingEnriched(**enriched_values)
            self.db.add(new_listing)
            self.db.commit()
            self.db.refresh(new_listing)
            return new_listing.listing_id


def enrich_all_unmatched_listings(db: Session) -> int:
    """
    Enrich all raw listings that are matched but not yet enriched.

    Returns:
        Count of enriched listings
    """
    enricher = ListingEnricher(db)

    # Find matched but not enriched listings
    unmatched = db.query(ListingRaw).filter(
        ListingRaw.matched_property_id.isnot(None),
        ~ListingRaw.raw_listing_id.in_(
            db.query(ListingEnriched.raw_listing_id)
        )
    ).all()

    count = 0
    for raw in unmatched:
        if enricher.enrich_listing(raw.raw_listing_id):
            count += 1

    logger.info(f"Enriched {count} listings")
    return count
