"""
Foxtons Estate Agent Scraper

Scrapes property listings from Foxtons.co.uk
- Extracts: address, price, bedrooms, bathrooms, description, images
- Uploads images to S3
- Stores in database

URL: https://www.foxtons.co.uk
"""
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from bs4 import BeautifulSoup
import time

from .base_scraper import BaseScraper, RawListing, ScraperConfig
from ingestion.storage.s3_storage import get_storage_manager

logger = logging.getLogger(__name__)


class FoxtonsScr(BaseScraper):
    """Scraper for Foxtons estate agent"""

    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self.s3_storage = get_storage_manager()

    def parse_listing_page(self, soup: BeautifulSoup, page_num: int) -> List[RawListing]:
        """
        Parse Foxtons search results page.

        URL example: https://www.foxtons.co.uk/properties-for-sale/london
        """
        listings = []

        # Foxtons uses <article> tags for property cards
        property_cards = soup.find_all('article', class_=re.compile(r'property'))

        if not property_cards:
            # Try alternative selector
            property_cards = soup.find_all('div', attrs={'data-testid': 'property-card'})

        logger.info(f"Found {len(property_cards)} property cards on page {page_num}")

        for card in property_cards:
            try:
                listing = self._parse_property_card(card)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.warning(f"Failed to parse property card: {e}")
                continue

        return listings

    def _parse_property_card(self, card: BeautifulSoup) -> Optional[RawListing]:
        """Parse a single Foxtons property card"""

        # Extract listing URL
        link = card.find('a', href=re.compile(r'/property'))
        if not link:
            return None

        listing_url = link['href']
        if not listing_url.startswith('http'):
            listing_url = f"https://www.foxtons.co.uk{listing_url}"

        # Extract external listing ID from URL
        # URL format: /property-for-sale/chelsea/abc123/
        external_id = listing_url.rstrip('/').split('/')[-1]

        # Get detailed data from detail page
        logger.info(f"Fetching detail page: {listing_url}")
        time.sleep(2)  # Be polite

        detail_soup = BeautifulSoup(self.session.get(listing_url).content, 'html.parser')
        return self._parse_detail_page(detail_soup, listing_url, external_id)

    def _parse_detail_page(
        self,
        soup: BeautifulSoup,
        listing_url: str,
        external_id: str
    ) -> Optional[RawListing]:
        """
        Parse Foxtons property detail page.

        Extract all required fields including images.
        """

        # Title (e.g. "2 bedroom flat for sale")
        title_elem = soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "Property for sale"

        # Price
        price_elem = soup.find(class_=re.compile(r'price'))
        if not price_elem:
            price_elem = soup.find('span', string=re.compile(r'£'))

        price_text = price_elem.get_text(strip=True) if price_elem else "Price on application"
        price_numeric = self.extract_price(price_text)

        # Address
        address_elem = soup.find(class_=re.compile(r'address')) or soup.find('address')
        if not address_elem:
            # Try meta tag
            address_elem = soup.find('meta', property='og:title')
            raw_address = address_elem['content'] if address_elem else ""
        else:
            raw_address = address_elem.get_text(strip=True)

        postcode = self.extract_postcode(raw_address)

        # Bedrooms & Bathrooms
        bedrooms = None
        bathrooms = None

        # Look for property features list
        features = soup.find_all(class_=re.compile(r'feature|icon'))
        for feature in features:
            text = feature.get_text(strip=True).lower()

            if 'bedroom' in text or 'bed' in text:
                bedrooms = self.extract_bedrooms(text)
            if 'bathroom' in text or 'bath' in text:
                match = re.search(r'(\d+)', text)
                if match:
                    bathrooms = int(match.group(1))

        # Alternative: look in title
        if not bedrooms:
            bedrooms = self.extract_bedrooms(title)

        # Property type
        property_type = self._extract_property_type(title, raw_address)

        # Description
        description_elem = soup.find(class_=re.compile(r'description'))
        if not description_elem:
            description_elem = soup.find('div', attrs={'itemprop': 'description'})

        description = description_elem.get_text(strip=True) if description_elem else None

        # Tenure (freehold/leasehold)
        tenure = None
        if description:
            if 'freehold' in description.lower():
                tenure = 'freehold'
            elif 'leasehold' in description.lower():
                tenure = 'leasehold'

        # Extract images
        image_urls = self._extract_images(soup)

        # Square footage (if available)
        sqft_elem = soup.find(string=re.compile(r'sq ft|sqft'))
        square_feet = None
        if sqft_elem:
            match = re.search(r'([\d,]+)\s*sq', sqft_elem)
            if match:
                square_feet = int(match.group(1).replace(',', ''))

        # Listed date (if available)
        listed_date = None
        date_elem = soup.find(class_=re.compile(r'date|added'))
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            listed_date = self._parse_date(date_text)

        # Create RawListing object
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
            listed_date=listed_date
        )

        return listing

    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract all property image URLs from detail page"""
        image_urls = []

        # Look for gallery/carousel images
        gallery = soup.find(class_=re.compile(r'gallery|carousel|photos'))

        if gallery:
            images = gallery.find_all('img')
        else:
            # Fallback: all images on page
            images = soup.find_all('img', src=re.compile(r'property|listing'))

        for img in images:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

            if not src:
                continue

            # Skip small thumbnails, icons, logos
            if any(skip in src for skip in ['logo', 'icon', 'thumb', 'avatar']):
                continue

            # Make absolute URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://www.foxtons.co.uk' + src

            # Get high-res version if available
            # Foxtons often has image size params: ?width=800&height=600
            src = re.sub(r'(width|height)=\d+', r'\1=1200', src)

            if src not in image_urls:
                image_urls.append(src)

        logger.info(f"Extracted {len(image_urls)} images")
        return image_urls

    def _extract_property_type(self, title: str, address: str) -> Optional[str]:
        """Determine property type from title/address"""
        text = (title + ' ' + address).lower()

        if 'flat' in text or 'apartment' in text or 'maisonette' in text:
            return 'flat'
        elif 'terraced' in text or 'terrace' in text:
            return 'terraced'
        elif 'semi-detached' in text or 'semi detached' in text:
            return 'semi_detached'
        elif 'detached' in text:
            return 'detached'
        elif 'bungalow' in text:
            return 'bungalow'
        elif 'house' in text:
            return 'terraced'  # Default house type

        return None

    def _parse_date(self, date_text: str) -> Optional[date]:
        """Parse date from various formats"""
        # Try common formats
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d %B %Y', '%d %b %Y']:
            try:
                return datetime.strptime(date_text, fmt).date()
            except ValueError:
                continue

        # Handle "2 days ago", "1 week ago" etc.
        if 'ago' in date_text.lower():
            from datetime import timedelta
            match = re.search(r'(\d+)\s*(day|week|month)', date_text.lower())
            if match:
                num = int(match.group(1))
                unit = match.group(2)

                if unit == 'day':
                    return date.today() - timedelta(days=num)
                elif unit == 'week':
                    return date.today() - timedelta(weeks=num)
                elif unit == 'month':
                    return date.today() - timedelta(days=num*30)

        return None


def create_foxtons_scraper(agent_id: int = 2) -> FoxtonsScr:
    """
    Factory function to create Foxtons scraper.

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
        max_pages=20,
        delay_seconds=2.0  # Be respectful
    )

    return FoxtonsScr(config)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = create_foxtons_scraper()

    # Scrape first page
    listings = scraper.scrape_page(1)

    print(f"Scraped {len(listings)} listings")

    for listing in listings[:3]:
        print(f"\n{listing.title}")
        print(f"Price: {listing.price_text}")
        print(f"Address: {listing.raw_address}")
        print(f"Bedrooms: {listing.bedrooms}")
        print(f"Images: {len(listing.image_urls)}")
