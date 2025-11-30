"""
Example scraper for a fictional estate agent website.

PROTOTYPE: This demonstrates the scraper pattern. Replace with actual
agent-specific implementations or official feed integrations.
"""
from typing import List, Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, RawListing, ScraperConfig
import logging

logger = logging.getLogger(__name__)


class ExampleAgentScraper(BaseScraper):
    """
    Example scraper for "Example Estate Agents Ltd"

    Website structure assumptions (fictional):
    - Listing page: https://www.exampleagent.co.uk/properties?page={page}
    - Each listing is in a <div class="property-card">
    - Title in <h2 class="property-title">
    - Price in <span class="price">
    - Address in <p class="address">
    - Beds/baths in <ul class="features">
    """

    def parse_listing_page(self, soup: BeautifulSoup, page_num: int) -> List[RawListing]:
        """Parse the search results page"""
        listings = []

        # Find all property cards
        property_cards = soup.find_all('div', class_='property-card')

        for card in property_cards:
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to parse property card: {e}")
                continue

        return listings

    def _parse_card(self, card: BeautifulSoup) -> Optional[RawListing]:
        """Parse a single property card element"""

        # Extract listing ID from data attribute or URL
        listing_link = card.find('a', class_='property-link')
        if not listing_link or not listing_link.get('href'):
            return None

        listing_url = listing_link['href']
        if not listing_url.startswith('http'):
            listing_url = self.config.base_url + listing_url

        # Extract ID from URL (e.g. /property/12345)
        external_id = listing_url.split('/')[-1]

        # Title
        title_elem = card.find('h2', class_='property-title')
        title = title_elem.get_text(strip=True) if title_elem else "Untitled"

        # Price
        price_elem = card.find('span', class_='price')
        price_text = price_elem.get_text(strip=True) if price_elem else "POA"
        price_numeric = self.extract_price(price_text)

        # Address
        address_elem = card.find('p', class_='address')
        raw_address = address_elem.get_text(strip=True) if address_elem else ""
        postcode = self.extract_postcode(raw_address)

        # Features (bedrooms, bathrooms)
        bedrooms = None
        bathrooms = None
        property_type = None

        features_list = card.find('ul', class_='features')
        if features_list:
            features_text = features_list.get_text()
            bedrooms = self.extract_bedrooms(features_text)

            # Extract bathrooms
            import re
            bath_match = re.search(r'(\d+)\s*bath', features_text, re.IGNORECASE)
            if bath_match:
                bathrooms = int(bath_match.group(1))

            # Extract property type
            for prop_type in ['detached', 'semi-detached', 'terraced', 'flat', 'bungalow']:
                if prop_type in features_text.lower():
                    property_type = prop_type
                    break

        # Description (short excerpt on card)
        desc_elem = card.find('p', class_='description')
        description = desc_elem.get_text(strip=True) if desc_elem else None

        # Images
        img_elem = card.find('img', class_='property-image')
        image_urls = [img_elem['src']] if img_elem and img_elem.get('src') else []

        return RawListing(
            external_listing_id=external_id,
            listing_url=listing_url,
            title=title,
            description=description,
            price_text=price_text,
            price_numeric=price_numeric,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            property_type=property_type,
            raw_address=raw_address,
            postcode=postcode,
            image_urls=image_urls
        )


# Factory function to create scraper configs for different agents
def get_scraper_configs() -> List[ScraperConfig]:
    """
    Returns scraper configurations for all agents.

    In production, load from database (agents table with scraper_config JSONB)
    """
    return [
        ScraperConfig(
            agent_id=1,
            agent_name="Example Estate Agents Ltd",
            base_url="https://www.exampleagent.co.uk",
            listings_url_template="https://www.exampleagent.co.uk/properties?page={page}",
            max_pages=20,
            delay_seconds=2.0
        ),
        # Add more agent configs here
    ]


def create_scraper(config: ScraperConfig) -> BaseScraper:
    """
    Factory to create appropriate scraper for an agent.

    In a real system, map agent_id to scraper class.
    """
    # For now, all use ExampleAgentScraper
    # In production: lookup table agent_id -> scraper_class
    return ExampleAgentScraper(config)
