"""
Enhanced Scraper Orchestrator with S3 Integration

Coordinates scraping, image downloading, and S3 storage.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from api.models.database import ListingRaw, Agent
from ingestion.storage.s3_storage import get_storage_manager
from .foxtons_scraper import create_foxtons_scraper
from .base_scraper import RawListing

logger = logging.getLogger(__name__)


class EnhancedScraperOrchestrator:
    """Orchestrates scraping with S3 image storage"""

    def __init__(self, db: Session):
        self.db = db
        self.s3_storage = get_storage_manager()

    def run_all_scrapers(self) -> Dict[str, Any]:
        """
        Run all configured scrapers and store results with S3 images.

        Returns:
            Dictionary with scraping statistics
        """
        stats = {
            'total_agents': 0,
            'successful_agents': 0,
            'failed_agents': 0,
            'total_listings_scraped': 0,
            'total_listings_new': 0,
            'total_listings_updated': 0,
            'total_images_uploaded': 0
        }

        # Get all active agents
        agents = self.db.query(Agent).filter(Agent.is_active == True).all()
        stats['total_agents'] = len(agents)

        for agent in agents:
            try:
                agent_stats = self.run_scraper_for_agent(agent)
                stats['successful_agents'] += 1
                stats['total_listings_scraped'] += agent_stats['scraped']
                stats['total_listings_new'] += agent_stats['new']
                stats['total_listings_updated'] += agent_stats['updated']
                stats['total_images_uploaded'] += agent_stats['images_uploaded']

            except Exception as e:
                logger.error(f"Failed to scrape {agent.name}: {e}", exc_info=True)
                stats['failed_agents'] += 1

        return stats

    def run_scraper_for_agent(self, agent: Agent) -> Dict[str, Any]:
        """
        Run scraper for a specific agent with S3 integration.

        Args:
            agent: Agent database object

        Returns:
            Statistics dictionary
        """
        logger.info(f"Starting scrape for agent_id={agent.agent_id} ({agent.name})")

        # Create appropriate scraper based on agent name
        scraper = self._create_scraper(agent)

        if not scraper:
            raise ValueError(f"No scraper available for agent: {agent.name}")

        try:
            # Scrape listings
            listings = scraper.scrape()

            # Store in database with S3 image uploads
            stats = self._store_listings_with_images(agent.agent_id, listings)

            # Update agent last_scraped_at
            agent.last_scraped_at = datetime.utcnow()
            self.db.commit()

            logger.info(
                f"Agent {agent.name}: scraped={len(listings)}, "
                f"new={stats['new']}, updated={stats['updated']}, "
                f"images={stats['images_uploaded']}"
            )

            return {
                'scraped': len(listings),
                'new': stats['new'],
                'updated': stats['updated'],
                'images_uploaded': stats['images_uploaded']
            }

        finally:
            scraper.close()

    def _create_scraper(self, agent: Agent):
        """
        Factory to create scraper based on agent name.

        Args:
            agent: Agent database object

        Returns:
            Scraper instance or None
        """
        agent_name_lower = agent.name.lower()

        if 'foxtons' in agent_name_lower:
            return create_foxtons_scraper(agent.agent_id)

        # Add more agent scrapers here
        # elif 'chestertons' in agent_name_lower:
        #     return create_chestertons_scraper(agent.agent_id)

        logger.warning(f"No scraper implementation for agent: {agent.name}")
        return None

    def _store_listings_with_images(
        self,
        agent_id: int,
        listings: List[RawListing]
    ) -> Dict[str, int]:
        """
        Store scraped listings in database and upload images to S3.

        Args:
            agent_id: Agent ID
            listings: List of RawListing objects

        Returns:
            Statistics dict with counts
        """
        new_count = 0
        updated_count = 0
        images_uploaded = 0

        for listing in listings:
            try:
                # Store listing in database
                listing_db = self._upsert_listing(agent_id, listing)

                # Upload images to S3
                if listing.image_urls:
                    s3_urls = self.s3_storage.upload_listing_images(
                        listing_id=listing_db.raw_listing_id,
                        image_urls=listing.image_urls,
                        agent_id=agent_id
                    )

                    # Update listing with S3 URLs
                    if s3_urls:
                        listing_db.image_urls = s3_urls
                        images_uploaded += len(s3_urls)

                self.db.commit()

                # Track new vs updated
                # (In reality, check if it was INSERT vs UPDATE)
                new_count += 1

            except Exception as e:
                logger.error(
                    f"Failed to store listing {listing.external_listing_id}: {e}",
                    exc_info=True
                )
                self.db.rollback()
                continue

        return {
            'new': new_count,
            'updated': updated_count,
            'images_uploaded': images_uploaded
        }

    def _upsert_listing(self, agent_id: int, listing: RawListing) -> ListingRaw:
        """
        Insert or update listing in database.

        Args:
            agent_id: Agent ID
            listing: RawListing object

        Returns:
            ListingRaw database object
        """
        data = listing.to_dict()
        data['agent_id'] = agent_id

        # Try to find existing
        existing = self.db.query(ListingRaw).filter(
            ListingRaw.agent_id == agent_id,
            ListingRaw.external_listing_id == listing.external_listing_id
        ).first()

        if existing:
            # Update existing
            for key, value in data.items():
                if key not in ['agent_id', 'external_listing_id']:
                    setattr(existing, key, value)

            existing.updated_at = datetime.utcnow()
            return existing

        else:
            # Create new
            new_listing = ListingRaw(**data)
            self.db.add(new_listing)
            self.db.flush()  # Get ID
            return new_listing


def run_scraping_job_with_s3(db: Session) -> Dict[str, Any]:
    """
    Entrypoint for scheduled scraping job with S3 storage.

    Args:
        db: Database session

    Returns:
        Statistics dictionary
    """
    orchestrator = EnhancedScraperOrchestrator(db)
    return orchestrator.run_all_scrapers()


# CLI command
if __name__ == "__main__":
    import logging
    from config.database import SessionLocal

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db = SessionLocal()
    try:
        stats = run_scraping_job_with_s3(db)
        print("\n" + "="*50)
        print("SCRAPING COMPLETED")
        print("="*50)
        print(f"Total agents: {stats['total_agents']}")
        print(f"Successful: {stats['successful_agents']}")
        print(f"Failed: {stats['failed_agents']}")
        print(f"Total listings: {stats['total_listings_scraped']}")
        print(f"New listings: {stats['total_listings_new']}")
        print(f"Updated listings: {stats['total_listings_updated']}")
        print(f"Images uploaded to S3: {stats['total_images_uploaded']}")
        print("="*50)

    finally:
        db.close()
