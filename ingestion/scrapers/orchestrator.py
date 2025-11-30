"""
Scraper orchestrator - runs scrapers and stores results in database.
"""
import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from api.models.database import ListingRaw, Agent
from .example_agent_scraper import get_scraper_configs, create_scraper
from .base_scraper import RawListing

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """Coordinates scraping across multiple agents"""

    def __init__(self, db: Session):
        self.db = db

    def run_all_scrapers(self) -> dict:
        """
        Run all configured scrapers and store results.

        Returns:
            Dictionary with scraping statistics
        """
        configs = get_scraper_configs()
        stats = {
            'total_agents': len(configs),
            'successful_agents': 0,
            'failed_agents': 0,
            'total_listings_scraped': 0,
            'total_listings_new': 0,
            'total_listings_updated': 0
        }

        for config in configs:
            try:
                agent_stats = self.run_scraper_for_agent(config)
                stats['successful_agents'] += 1
                stats['total_listings_scraped'] += agent_stats['scraped']
                stats['total_listings_new'] += agent_stats['new']
                stats['total_listings_updated'] += agent_stats['updated']

            except Exception as e:
                logger.error(f"Failed to scrape {config.agent_name}: {e}", exc_info=True)
                stats['failed_agents'] += 1

        return stats

    def run_scraper_for_agent(self, config) -> dict:
        """
        Run scraper for a single agent.

        Args:
            config: ScraperConfig instance

        Returns:
            Dictionary with agent-specific statistics
        """
        logger.info(f"Starting scrape for agent_id={config.agent_id} ({config.agent_name})")

        # Create scraper
        scraper = create_scraper(config)

        try:
            # Scrape listings
            listings = scraper.scrape()

            # Store in database
            stats = self._store_listings(config.agent_id, listings)

            # Update agent last_scraped_at
            self.db.query(Agent).filter(Agent.agent_id == config.agent_id).update({
                'last_scraped_at': datetime.utcnow()
            })
            self.db.commit()

            logger.info(
                f"Agent {config.agent_name}: scraped={len(listings)}, "
                f"new={stats['new']}, updated={stats['updated']}"
            )

            return {
                'scraped': len(listings),
                'new': stats['new'],
                'updated': stats['updated']
            }

        finally:
            scraper.close()

    def _store_listings(self, agent_id: int, listings: List[RawListing]) -> dict:
        """
        Store scraped listings in database using upsert.

        Args:
            agent_id: Agent ID
            listings: List of RawListing objects

        Returns:
            Statistics dict with 'new' and 'updated' counts
        """
        new_count = 0
        updated_count = 0

        for listing in listings:
            data = listing.to_dict()
            data['agent_id'] = agent_id

            # Upsert using PostgreSQL INSERT ... ON CONFLICT
            stmt = insert(ListingRaw).values(**data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['agent_id', 'external_listing_id'],
                set_={
                    'title': stmt.excluded.title,
                    'description': stmt.excluded.description,
                    'price_text': stmt.excluded.price_text,
                    'price_numeric': stmt.excluded.price_numeric,
                    'bedrooms': stmt.excluded.bedrooms,
                    'bathrooms': stmt.excluded.bathrooms,
                    'property_type': stmt.excluded.property_type,
                    'raw_address': stmt.excluded.raw_address,
                    'postcode': stmt.excluded.postcode,
                    'tenure': stmt.excluded.tenure,
                    'image_urls': stmt.excluded.image_urls,
                    'status': stmt.excluded.status,
                    'last_updated_date': stmt.excluded.scraped_at,
                    'updated_at': datetime.utcnow()
                }
            )

            result = self.db.execute(stmt)

            # Check if insert or update (PostgreSQL doesn't return this directly,
            # so we approximate based on whether matched_property_id existed)
            # For simplicity, count all as 'updated' for now
            updated_count += 1

        self.db.commit()

        # Rough heuristic: assume listings not seen before are new
        # In production, track this more accurately
        return {'new': len(listings), 'updated': updated_count}


def run_scraping_job(db: Session) -> dict:
    """
    Entrypoint for scheduled scraping job (e.g. Lambda, Celery task).

    Args:
        db: Database session

    Returns:
        Statistics dictionary
    """
    orchestrator = ScraperOrchestrator(db)
    return orchestrator.run_all_scrapers()
