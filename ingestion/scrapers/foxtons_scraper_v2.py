"""
Foxtons Scraper v2 - JSON-based extraction

Foxtons is a Next.js site - all listing data is in __NEXT_DATA__ JSON script
No need for Selenium - just parse the JSON!
"""
import re
import json
import logging
from typing import List, Optional
from datetime import date
from decimal import Decimal
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, RawListing, ScraperConfig

logger = logging.getLogger(__name__)


class FoxtonsScraper(BaseScraper):
    """Scraper for Foxtons estate agent using Next.js JSON data"""

    def parse_listing_page(self, soup: BeautifulSoup, page_num: int) -> List[RawListing]:
        """
        Extract listings from Foxtons Next.js JSON data

        All listings are in <script id="__NEXT_DATA__">
        """
        listings = []

        # Find Next.js data script
        script = soup.find('script', id='__NEXT_DATA__', type='application/json')

        if not script:
            logger.error("Could not find __NEXT_DATA__ script")
            return []

        try:
            # Parse JSON
            data = json.loads(script.string)

            # Navigate to properties
            properties = data['props']['pageProps']['pageData']['data']['data']

            logger.info(f"Found {len(properties)} properties in JSON data")

            # Parse each property
            for prop_data in properties:
                try:
                    listing = self._parse_property_json(prop_data)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse property: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing Foxtons JSON: {e}")

        return listings

    def _parse_property_json(self, prop: dict) -> Optional[RawListing]:
        """
        Parse a single property from Foxtons JSON data

        Example structure:
        {
          "bedrooms": 4,
          "bathrooms": 4,
          "priceTo": "14950000",
          "propertyReference": "chpk6210326",
          "streetName": "Connaught Place",
          "typeGroup": "flat",
          "locationName": "Marylebone",
          "location": {"lat": 51.513149, "lon": -0.161954},
          "officeName": "Foxtons Marylebone and Mayfair",
          ...
        }
        """

        # External ID
        external_id = prop.get('propertyReference') or prop.get('instructionReference', '')

        # Build listing URL
        # Foxtons URLs: /property-for-sale/{area}/{property-ref}/
        listing_url = f"https://www.foxtons.co.uk/property-for-sale/{external_id}"

        # Title - construct from property data
        beds = prop.get('bedrooms', 0)
        prop_type = prop.get('typeGroup', 'property')
        location = prop.get('locationName', '')
        title = f"{beds} bedroom {prop_type} for sale"
        if location:
            title += f" in {location}"

        # Price
        price_to = prop.get('priceTo')  # Sale price
        price_pcm = prop.get('pricePcm')  # Rental price (ignore for sales)

        if price_to:
            price_numeric = Decimal(price_to)
            price_text = f"£{int(price_numeric):,}"
        else:
            price_numeric = None
            price_text = "POA"

        # Address
        street = prop.get('streetName', '')
        development = prop.get('developmentName', '')
        location_name = prop.get('locationName', '')

        address_parts = [p for p in [development, street, location_name] if p]
        raw_address = ', '.join(address_parts)

        # Postcode - try to extract from property data or location
        postcode_from_data = prop.get('postcode')  # May not exist
        if postcode_from_data:
            postcode = postcode_from_data
        else:
            # Try to get from location coordinates via reverse geocoding (future)
            # For now, we don't have postcode in this JSON
            postcode = None

        # Bedrooms & Bathrooms
        bedrooms = prop.get('bedrooms')
        bathrooms = prop.get('bathrooms')

        # Property type
        property_type = prop.get('typeGroup')  # e.g. "flat", "house"

        # Office/Agent
        office_name = prop.get('officeName', '')

        # FETCH DETAIL PAGE for description and images
        logger.info(f"Fetching detail page for {external_id}...")
        detail_data = self.fetch_detail_page_data(listing_url)

        description = detail_data.get('description')
        image_urls = detail_data.get('images', [])
        tenure = detail_data.get('tenure')

        # Create listing
        listing = RawListing(
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
            tenure=tenure,
            image_urls=image_urls,
            listed_date=None  # Not in JSON
        )

        return listing

    def _construct_image_urls(self, property_ref: str) -> List[str]:
        """
        Construct Foxtons image URLs from property reference.

        Foxtons stores images at predictable URLs:
        https://images.foxtons.co.uk/{ref}/main_0.jpg
        https://images.foxtons.co.uk/{ref}/main_1.jpg
        etc.

        For now, return empty list - we can fetch from detail page if needed
        """
        # Option 1: Try predictable URLs (may or may not work)
        base_url = f"https://images.foxtons.co.uk/{property_ref}"
        potential_urls = [
            f"{base_url}/main_0.jpg",
            f"{base_url}/main_1.jpg",
            f"{base_url}/main_2.jpg",
        ]

        # Option 2: Fetch detail page (more reliable but slower)
        # We'll implement this in a separate method if needed

        return []  # For now, return empty - can add detail page fetch

    def fetch_detail_page_data(self, listing_url: str) -> dict:
        """
        Fetch additional data from property detail page.

        Returns dict with: description, images, tenure, etc.
        """
        import time
        time.sleep(self.config.delay_seconds)  # Rate limiting

        try:
            response = self.session.get(listing_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find Next.js data on detail page
            script = soup.find('script', id='__NEXT_DATA__', type='application/json')
            if not script:
                logger.warning(f"No __NEXT_DATA__ found on {listing_url}")
                return {}

            data = json.loads(script.string)

            # Navigate to property detail data
            # Structure: props.pageProps.pageData.data
            page_data = data.get('props', {}).get('pageProps', {}).get('pageData', {})

            # Extract what we need
            result = {}

            # Description
            description = page_data.get('data', {}).get('description', '')
            if description:
                # Clean HTML tags if present
                desc_soup = BeautifulSoup(description, 'html.parser')
                result['description'] = desc_soup.get_text(strip=True)

            # Images - look in pageData.data.images or similar
            images_data = page_data.get('data', {}).get('images', [])

            if images_data:
                image_urls = []
                for img in images_data:
                    if isinstance(img, dict):
                        # Structure might be: {'url': '...', 'caption': '...'}
                        url = img.get('url') or img.get('src') or img.get('path', '')
                    else:
                        # Might be just a string URL
                        url = str(img)

                    if url and not url.startswith('data:'):
                        # Make absolute URL
                        if url.startswith('//'):
                            url = 'https:' + url
                        elif url.startswith('/'):
                            url = 'https://www.foxtons.co.uk' + url
                        elif not url.startswith('http'):
                            # Might be relative to images domain
                            url = f"https://images.foxtons.co.uk/{url}"

                        image_urls.append(url)

                result['images'] = image_urls
                logger.info(f"Extracted {len(image_urls)} images from detail page")

            # Tenure
            tenure = page_data.get('data', {}).get('tenure', '')
            if tenure:
                result['tenure'] = tenure.lower()

            # Postcode (might be in detail page)
            postcode = page_data.get('data', {}).get('postcode', '')
            if postcode:
                result['postcode'] = postcode

            return result

        except Exception as e:
            logger.warning(f"Failed to fetch detail page {listing_url}: {e}")
            import traceback
            logger.debug(traceback.format_exc())

        return {}


def create_foxtons_scraper(agent_id: int = 2) -> FoxtonsScraper:
    """
    Factory function to create Foxtons scraper (v2 - JSON-based)

    Args:
        agent_id: Database ID for Foxtons agent

    Returns:
        Configured Foxtons scraper
    """
    config = ScraperConfig(
        agent_id=agent_id,
        agent_name="Foxtons",
        base_url="https://www.foxtons.co.uk",
        listings_url_template="https://www.foxtons.co.uk/properties-for-sale/london?page={page}",
        max_pages=5,  # Foxtons paginates in JSON
        delay_seconds=2.0
    )

    return FoxtonsScraper(config)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = create_foxtons_scraper()
    listings = scraper.scrape_page(1)

    print(f"\nScraped {len(listings)} listings\n")

    for i, listing in enumerate(listings[:5], 1):
        print(f"{i}. {listing.title}")
        print(f"   Price: {listing.price_text}")
        print(f"   Address: {listing.raw_address}")
        print(f"   Beds: {listing.bedrooms}, Baths: {listing.bathrooms}")
        print(f"   URL: {listing.listing_url}")
        print()
