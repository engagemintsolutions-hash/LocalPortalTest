"""
Base scraper class and utilities for estate agent listing scrapers.

PROTOTYPE ONLY: This scraper framework is for demonstration purposes.
In production, replace with official agent feeds/APIs.
"""
import re
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ScraperConfig:
    """Configuration for a scraper"""
    def __init__(
        self,
        agent_id: int,
        agent_name: str,
        base_url: str,
        listings_url_template: str,
        max_pages: int = 50,
        delay_seconds: float = 1.0,
        **kwargs
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.base_url = base_url
        self.listings_url_template = listings_url_template
        self.max_pages = max_pages
        self.delay_seconds = delay_seconds
        self.extra = kwargs


class RawListing:
    """Container for scraped listing data"""
    def __init__(
        self,
        external_listing_id: str,
        listing_url: str,
        title: str,
        description: Optional[str],
        price_text: str,
        price_numeric: Optional[Decimal],
        bedrooms: Optional[int],
        bathrooms: Optional[int],
        property_type: Optional[str],
        raw_address: str,
        postcode: Optional[str],
        tenure: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        listed_date: Optional[date] = None,
    ):
        self.external_listing_id = external_listing_id
        self.listing_url = listing_url
        self.title = title
        self.description = description
        self.price_text = price_text
        self.price_numeric = price_numeric
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.property_type = property_type
        self.raw_address = raw_address
        self.postcode = postcode
        self.tenure = tenure
        self.image_urls = image_urls or []
        self.listed_date = listed_date

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        return {
            'external_listing_id': self.external_listing_id,
            'listing_url': self.listing_url,
            'title': self.title,
            'description': self.description,
            'price_text': self.price_text,
            'price_numeric': self.price_numeric,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'property_type': self.property_type,
            'raw_address': self.raw_address,
            'postcode': self.postcode,
            'tenure': self.tenure,
            'image_urls': self.image_urls,
            'listed_date': self.listed_date,
            'status': 'active',
            'scraped_at': datetime.utcnow()
        }


class BaseScraper(ABC):
    """
    Abstract base class for estate agent scrapers.

    Each agent gets their own scraper subclass implementing:
    - parse_listing_page()
    - parse_detail_page()
    """

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()

        # Retry strategy
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # User agent
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        return session

    def scrape(self) -> List[RawListing]:
        """
        Main scraping entrypoint.

        Returns:
            List of RawListing objects
        """
        logger.info(f"Starting scrape for {self.config.agent_name}")
        all_listings = []

        for page_num in range(1, self.config.max_pages + 1):
            try:
                logger.info(f"Scraping page {page_num}")
                listings = self.scrape_page(page_num)

                if not listings:
                    logger.info(f"No listings on page {page_num}, stopping")
                    break

                all_listings.extend(listings)

                # Respect rate limiting
                time.sleep(self.config.delay_seconds)

            except Exception as e:
                logger.error(f"Error scraping page {page_num}: {e}", exc_info=True)
                # Continue to next page
                continue

        logger.info(f"Scraped {len(all_listings)} total listings for {self.config.agent_name}")
        return all_listings

    def scrape_page(self, page_num: int) -> List[RawListing]:
        """
        Scrape a single listings page.

        Args:
            page_num: Page number (1-indexed)

        Returns:
            List of RawListing objects
        """
        url = self.config.listings_url_template.format(page=page_num)
        logger.debug(f"Fetching {url}")

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        return self.parse_listing_page(soup, page_num)

    @abstractmethod
    def parse_listing_page(self, soup: BeautifulSoup, page_num: int) -> List[RawListing]:
        """
        Parse the listing page HTML to extract basic listing info.

        Args:
            soup: BeautifulSoup object
            page_num: Page number being parsed

        Returns:
            List of RawListing objects
        """
        pass

    def parse_detail_page(self, listing_url: str) -> Dict[str, Any]:
        """
        Optionally fetch and parse a detail page for additional data.

        Args:
            listing_url: URL of the listing detail page

        Returns:
            Dictionary of additional fields
        """
        # Default: no detail page parsing
        return {}

    @staticmethod
    def extract_price(price_text: str) -> Optional[Decimal]:
        """
        Extract numeric price from text like "£450,000" or "Offers Over £500k"

        Args:
            price_text: Raw price string

        Returns:
            Decimal price or None
        """
        if not price_text:
            return None

        # Remove £ and commas
        cleaned = re.sub(r'[£,]', '', price_text)

        # Handle "k" suffix (e.g. "450k")
        if 'k' in cleaned.lower():
            try:
                num = float(re.search(r'(\d+\.?\d*)', cleaned).group(1))
                return Decimal(str(int(num * 1000)))
            except (AttributeError, ValueError):
                return None

        # Extract first number
        match = re.search(r'(\d+)', cleaned)
        if match:
            try:
                return Decimal(match.group(1))
            except:
                return None

        return None

    @staticmethod
    def extract_bedrooms(text: str) -> Optional[int]:
        """Extract bedroom count from text"""
        match = re.search(r'(\d+)\s*bed', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def extract_postcode(address: str) -> Optional[str]:
        """
        Extract UK postcode from address text.

        UK postcode regex: AA9A 9AA format (with variations)
        """
        # UK postcode pattern
        pattern = r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b'
        match = re.search(pattern, address.upper())
        if match:
            return match.group(1).strip()
        return None

    def close(self):
        """Clean up session"""
        self.session.close()
