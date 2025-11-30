"""
Savills Estate Agent Scraper - COMPLETE WITH IMAGES

Scrapes from Savills premium estate agent
- Gets: address, price, beds, baths, description, images
- Uploads images to S3
- Stores complete listing data

URL: https://search.savills.com
"""
import re
import logging
import time
from typing import List, Optional
from decimal import Decimal
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, RawListing, ScraperConfig

logger = logging.getLogger(__name__)


class SavillsScraper(BaseScraper):
    """Scraper for Savills estate agent"""

    def parse_listing_page(self, soup: BeautifulSoup, page_num: int) -> List[RawListing]:
        """
        Parse Savills search results page

        URL: https://search.savills.com/list/property-for-sale/uk?Page={page}
        """
        listings = []

        # Savills uses class='property-list-item' or similar
        property_cards = soup.find_all(class_=lambda x: x and ('property' in x.lower() or 'listing' in x.lower()))

        logger.info(f"Found {len(property_cards)} potential property cards")

        for card in property_cards:
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
                    # Rate limiting - be respectful
                    time.sleep(self.config.delay_seconds)
            except Exception as e:
                logger.warning(f"Failed to parse card: {e}")
                continue

        return listings

    def _parse_card(self, card: BeautifulSoup) -> Optional[RawListing]:
        """Parse a Savills property card"""

        # Find link to detail page
        link = card.find('a', href=lambda x: x and '/property' in x)
        if not link:
            return None

        listing_url = link['href']
        if not listing_url.startswith('http'):
            listing_url = f"https://search.savills.com{listing_url}"

        # Extract ID from URL
        external_id = listing_url.split('/')[-1] or listing_url.split('/')[-2]

        # Title
        title_elem = card.find(['h2', 'h3'], class_=lambda x: x and ('title' in x.lower() or 'heading' in x.lower()))
        if not title_elem:
            title_elem = card.find(['h2', 'h3'])
        title = title_elem.get_text(strip=True) if title_elem else "Property for sale"

        # Price
        price_elem = card.find(string=lambda x: x and '£' in str(x))
        price_text = price_elem.strip() if price_elem else "POA"
        price_numeric = self.extract_price(price_text)

        # Address
        address_elem = card.find(class_=lambda x: x and 'address' in x.lower())
        if not address_elem:
            # Try to find it in the card text
            card_text = card.get_text()
            address_elem = card

        raw_address = address_elem.get_text(strip=True) if address_elem else ""

        # Extract postcode
        postcode = self.extract_postcode(raw_address)

        # Beds/baths
        bedrooms = self.extract_bedrooms(card.get_text())

        bathrooms = None
        bath_match = re.search(r'(\d+)\s*bath', card.get_text(), re.IGNORECASE)
        if bath_match:
            bathrooms = int(bath_match.group(1))

        # Property type
        property_type = self._extract_property_type(title)

        # Image on card (thumbnail)
        img_elem = card.find('img')
        card_image = img_elem['src'] if img_elem and img_elem.get('src') else None

        # Fetch detail page for full data
        logger.info(f"Fetching detail page: {listing_url}")
        detail_data = self._fetch_detail_page(listing_url)

        return RawListing(
            external_listing_id=external_id,
            listing_url=listing_url,
            title=title,
            description=detail_data.get('description'),
            price_text=price_text,
            price_numeric=price_numeric,
            bedrooms=bedrooms,
            bathrooms=bathrooms or detail_data.get('bathrooms'),
            property_type=property_type,
            raw_address=raw_address,
            postcode=postcode or detail_data.get('postcode'),
            tenure=detail_data.get('tenure'),
            image_urls=detail_data.get('images', [card_image] if card_image else []),
            listed_date=None
        )

    def _fetch_detail_page(self, url: str) -> dict:
        """
        Fetch detail page and extract description + images

        Returns dict with: description, images, tenure, postcode
        """
        import json
        import time

        time.sleep(self.config.delay_seconds)  # Rate limiting

        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            result = {}

            # Find Redux state in HTML (contains all property data including images!)
            script_text = soup.find('script', string=lambda x: x and 'PropertyCardImagesGallery' in str(x))

            if script_text:
                script_content = script_text.string

                # Extract the full JSON object
                # Pattern: {"dataManager":"...","props":{...},"initialReduxState":{...}}
                match = re.search(r'\{"dataManager"[^{]*"props".*\}', script_content)

                if match:
                    try:
                        full_json = json.loads(match.group(0))

                        # Navigate to propertyDetail.property
                        prop_detail = full_json.get('props', {}).get('initialReduxState', {}).get('propertyDetail', {}).get('property', {})

                        if prop_detail:
                            # Extract images from gallery
                            images_gallery = prop_detail.get('ImagesGallery', [])

                            image_urls = []
                            for img in images_gallery:
                                # Use large version (_l_gal.jpg) for best quality
                                img_url = img.get('ImageUrl_L') or img.get('ImageUrl_M') or img.get('ImageUrl_S')
                                if img_url:
                                    image_urls.append(img_url)

                            result['images'] = image_urls
                            logger.info(f"Extracted {len(image_urls)} images from Redux state")

                            # Description
                            desc = prop_detail.get('Description', '')
                            if desc:
                                result['description'] = desc

                            # Postcode
                            postcode = prop_detail.get('Postcode', '')
                            if postcode:
                                result['postcode'] = postcode

                            # Tenure
                            tenure = prop_detail.get('Tenure', '')
                            if tenure:
                                result['tenure'] = tenure.lower()

                            return result

                    except json.JSONDecodeError as e:
                        logger.warning(f"Could not parse Redux state JSON: {e}")

            # Fallback: look for images in img tags
            image_urls = []
            images = soup.find_all('img', src=lambda x: x and 'assets.savills.com/properties' in str(x))

            for img in images:
                src = img.get('src')
                if src and src not in image_urls:
                    image_urls.append(src)

            if image_urls:
                result['images'] = image_urls
                logger.info(f"Extracted {len(image_urls)} images from img tags")

            return result

        except Exception as e:
            logger.warning(f"Failed to fetch detail page {url}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {}

    def _extract_property_type(self, text: str) -> Optional[str]:
        """Extract property type from text"""
        text_lower = text.lower()

        if 'flat' in text_lower or 'apartment' in text_lower:
            return 'flat'
        elif 'terraced' in text_lower:
            return 'terraced'
        elif 'semi-detached' in text_lower or 'semi detached' in text_lower:
            return 'semi_detached'
        elif 'detached' in text_lower:
            return 'detached'
        elif 'bungalow' in text_lower:
            return 'bungalow'

        return None


def create_savills_scraper(agent_id: int = 3) -> SavillsScraper:
    """
    Create Savills scraper instance

    Args:
        agent_id: Database ID for Savills

    Returns:
        Configured scraper
    """
    config = ScraperConfig(
        agent_id=agent_id,
        agent_name="Savills",
        base_url="https://search.savills.com",
        listings_url_template="https://search.savills.com/list/property-for-sale/uk?Page={page}",
        max_pages=10,
        delay_seconds=2.5  # Be extra respectful with premium agents
    )

    return SavillsScraper(config)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("="*60)
    print("TESTING SAVILLS SCRAPER")
    print("="*60)

    scraper = create_savills_scraper()

    print("\nScraping first page...")
    listings = scraper.scrape_page(1)

    print(f"\nScraped {len(listings)} listings")
    print("="*60)

    for i, listing in enumerate(listings[:3], 1):
        print(f"\n{i}. {listing.title}")
        print(f"   Price: {listing.price_text}")
        print(f"   Address: {listing.raw_address}")
        print(f"   Postcode: {listing.postcode}")
        print(f"   Beds: {listing.bedrooms}, Baths: {listing.bathrooms}")
        print(f"   Type: {listing.property_type}")
        print(f"   Images: {len(listing.image_urls)}")
        if listing.description:
            print(f"   Description: {listing.description[:100]}...")

    scraper.close()
