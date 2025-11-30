"""
Address matching logic to link scraped listings to base properties.

Strategies (in order of preference):
1. UPRN exact match (if available in scraped data)
2. Postcode + building number exact match
3. Postcode + fuzzy address match (using trigram similarity)
"""
import re
import logging
from typing import Optional, Tuple
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.models.database import Property

logger = logging.getLogger(__name__)


class AddressMatcher:
    """Matches scraped addresses to properties in database"""

    # Minimum similarity score for fuzzy matching (0-1)
    FUZZY_MATCH_THRESHOLD = 0.7

    def __init__(self, db: Session):
        self.db = db

    def match(
        self,
        raw_address: str,
        postcode: Optional[str],
        uprn: Optional[int] = None
    ) -> Optional[Tuple[int, Decimal, str]]:
        """
        Match a raw address to a property.

        Args:
            raw_address: Full address string from scraper
            postcode: Postcode (may be None)
            uprn: UPRN if available (rare in scraped data)

        Returns:
            Tuple of (property_id, confidence, match_method) or None
        """

        # Strategy 1: UPRN exact match
        if uprn:
            result = self._match_by_uprn(uprn)
            if result:
                return result

        # Strategy 2: Postcode + building number
        if postcode:
            result = self._match_by_postcode_and_number(raw_address, postcode)
            if result:
                return result

        # Strategy 3: Fuzzy address match (within postcode)
        if postcode:
            result = self._match_by_fuzzy_address(raw_address, postcode)
            if result:
                return result

        # No match found
        logger.warning(f"No match found for address: {raw_address}")
        return None

    def _match_by_uprn(self, uprn: int) -> Optional[Tuple[int, Decimal, str]]:
        """Match by UPRN (highest confidence)"""
        prop = self.db.query(Property).filter(Property.uprn == uprn).first()
        if prop:
            return (prop.property_id, Decimal('1.00'), 'uprn_exact')
        return None

    def _match_by_postcode_and_number(
        self,
        raw_address: str,
        postcode: str
    ) -> Optional[Tuple[int, Decimal, str]]:
        """
        Match by postcode + building number/name.

        Extract building number from address and match against properties
        with same postcode.
        """
        # Normalize address
        normalized = self._normalize_address(raw_address)

        # Extract building number (leading digits)
        building_num = self._extract_building_number(normalized)

        if not building_num:
            return None

        # Query properties with matching postcode and building number
        prop = self.db.query(Property).filter(
            Property.postcode == postcode.upper().replace(' ', ''),
            Property.building_number == building_num
        ).first()

        if prop:
            return (prop.property_id, Decimal('0.95'), 'postcode_number')

        return None

    def _match_by_fuzzy_address(
        self,
        raw_address: str,
        postcode: str
    ) -> Optional[Tuple[int, Decimal, str]]:
        """
        Fuzzy match using PostgreSQL trigram similarity.

        Finds properties in same postcode with similar address strings.
        """
        normalized = self._normalize_address(raw_address)

        # Use pg_trgm similarity
        # similarity() returns 0-1, higher is better
        query = self.db.query(
            Property.property_id,
            func.similarity(Property.address_normalised, normalized).label('sim_score')
        ).filter(
            Property.postcode == postcode.upper().replace(' ', '')
        ).filter(
            func.similarity(Property.address_normalised, normalized) >= self.FUZZY_MATCH_THRESHOLD
        ).order_by(
            func.similarity(Property.address_normalised, normalized).desc()
        ).first()

        if query:
            property_id, sim_score = query
            # Convert similarity to decimal confidence (0.7-1.0 range)
            confidence = Decimal(str(round(sim_score, 2)))
            return (property_id, confidence, 'address_fuzzy')

        return None

    @staticmethod
    def _normalize_address(address: str) -> str:
        """
        Normalize address for matching.

        - Lowercase
        - Remove punctuation
        - Collapse whitespace
        - Remove common suffixes (street, road, avenue, etc.)
        """
        normalized = address.lower()

        # Remove punctuation
        normalized = re.sub(r'[.,\-]', ' ', normalized)

        # Remove common street suffixes for better matching
        suffixes = ['street', 'road', 'avenue', 'lane', 'drive', 'close', 'way', 'place']
        for suffix in suffixes:
            normalized = re.sub(rf'\b{suffix}\b', '', normalized)

        # Collapse whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    @staticmethod
    def _extract_building_number(address: str) -> Optional[str]:
        """
        Extract building number from start of address.

        Examples:
        "42 High Street" -> "42"
        "123a Main Road" -> "123a"
        "Flat 5, 10 Oak Lane" -> "10"
        """
        # Try to match leading number (possibly with suffix like 'a')
        match = re.match(r'^(\d+[a-z]?)\b', address)
        if match:
            return match.group(1)

        # Handle "Flat X, NUMBER Street" pattern
        match = re.search(r',\s*(\d+[a-z]?)\b', address)
        if match:
            return match.group(1)

        return None


def match_listing_to_property(
    db: Session,
    raw_address: str,
    postcode: Optional[str],
    uprn: Optional[int] = None
) -> Optional[Tuple[int, Decimal, str]]:
    """
    Convenience function to match a listing.

    Args:
        db: Database session
        raw_address: Raw address string
        postcode: Postcode (optional)
        uprn: UPRN (optional)

    Returns:
        Tuple of (property_id, confidence, match_method) or None
    """
    matcher = AddressMatcher(db)
    return matcher.match(raw_address, postcode, uprn)
