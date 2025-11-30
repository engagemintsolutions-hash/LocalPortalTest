"""
Demo: Load real Savills listings with images into database

This script:
1. Scrapes 15 real properties from Savills
2. Downloads and uploads images to S3
3. Stores listings in database
4. Creates mock enriched data for demo
"""
import logging
import json
from decimal import Decimal
from config.database import SessionLocal
from api.models.database import Agent, ListingRaw, ListingEnriched, Property
from ingestion.scrapers.savills_scraper import create_savills_scraper
from ingestion.storage.s3_storage import get_storage_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_demo_database():
    """Load real Savills listings for demo"""

    db = SessionLocal()
    s3_storage = get_storage_manager()

    try:
        # 1. Ensure Savills agent exists
        agent = db.query(Agent).filter(Agent.name == 'Savills').first()
        if not agent:
            logger.info("Creating Savills agent...")
            agent = Agent(
                name='Savills',
                branch_name='UK Wide',
                website_url='www.savills.com',
                is_active=True,
                scraper_config={
                    'base_url': 'https://search.savills.com',
                    'max_pages': 1
                }
            )
            db.add(agent)
            db.commit()
            db.refresh(agent)

        logger.info(f"Using agent: {agent.name} (ID: {agent.agent_id})")

        # 2. Scrape listings
        logger.info("Scraping Savills listings...")
        scraper = create_savills_scraper(agent_id=agent.agent_id)

        # Get first 15 listings only (for demo)
        all_listings = scraper.scrape_page(1)
        listings_to_load = all_listings[:15]

        logger.info(f"Scraped {len(listings_to_load)} listings")

        # 3. Load into database with S3 images
        for idx, listing in enumerate(listings_to_load, 1):
            logger.info(f"\nProcessing listing {idx}/{len(listings_to_load)}: {listing.title}")

            # Check if already exists
            existing = db.query(ListingRaw).filter(
                ListingRaw.agent_id == agent.agent_id,
                ListingRaw.external_listing_id == listing.external_listing_id
            ).first()

            if existing:
                logger.info(f"  Listing {listing.external_listing_id} already exists, skipping")
                continue

            # Upload images to S3 (limit to 5 per listing for demo)
            s3_image_urls = []
            if listing.image_urls:
                logger.info(f"  Uploading {min(5, len(listing.image_urls))} images to S3...")

                s3_image_urls = s3_storage.upload_listing_images(
                    listing_id=idx,  # Use index as temp ID
                    image_urls=listing.image_urls[:5],  # First 5 images
                    agent_id=agent.agent_id
                )

                logger.info(f"  Uploaded {len(s3_image_urls)} images to S3")

            # Create listing in database
            listing_data = listing.to_dict()
            listing_data['agent_id'] = agent.agent_id
            listing_data['image_urls'] = s3_image_urls  # Store S3 URLs

            db_listing = ListingRaw(**listing_data)
            db.add(db_listing)
            db.flush()  # Get ID

            # Update S3 images with real listing ID
            if s3_image_urls:
                # Re-upload with correct ID
                logger.info(f"  Re-uploading with listing ID {db_listing.raw_listing_id}...")
                final_s3_urls = s3_storage.upload_listing_images(
                    listing_id=db_listing.raw_listing_id,
                    image_urls=listing.image_urls[:5],
                    agent_id=agent.agent_id
                )
                db_listing.image_urls = final_s3_urls

            # Create mock enriched version for demo
            create_mock_enriched_listing(db, db_listing, agent.agent_id)

            db.commit()
            logger.info(f"  Saved listing {db_listing.raw_listing_id} to database")

        logger.info(f"\n{'='*70}")
        logger.info(f"DEMO DATABASE LOADED SUCCESSFULLY!")
        logger.info(f"{'='*70}")
        logger.info(f"Loaded {len(listings_to_load)} real Savills listings")
        logger.info(f"Images uploaded to S3: s3://uk-property-images/images/{agent.agent_id}/")
        logger.info(f"{'='*70}")

        scraper.close()

    finally:
        db.close()


def create_mock_enriched_listing(db, raw_listing: ListingRaw, agent_id: int):
    """
    Create a mock enriched listing for demo purposes
    (Normally this would come from feature store + AVM)
    """
    import random
    from geoalchemy2.elements import WKTElement

    # Create a dummy property record if needed
    property_id = raw_listing.raw_listing_id  # Use listing ID as property ID for demo

    # Mock location (London center for demo)
    mock_location = WKTElement(f'POINT(-0.1278 51.5074)', srid=4326)

    # Create enriched listing
    enriched = ListingEnriched(
        raw_listing_id=raw_listing.raw_listing_id,
        property_id=property_id,  # Mock
        agent_id=agent_id,

        # Core data from raw
        title=raw_listing.title or "Property for sale",
        description=raw_listing.description,
        price=raw_listing.price_numeric or Decimal('500000'),
        bedrooms=raw_listing.bedrooms or 2,
        bathrooms=raw_listing.bathrooms or 1,
        property_type=raw_listing.property_type,
        tenure=raw_listing.tenure,
        address=raw_listing.raw_address or "London",
        postcode=raw_listing.postcode or "SW1A 1AA",
        location=mock_location,
        status='active',
        listed_date=raw_listing.listed_date,

        # Mock enrichment data for demo
        epc_rating=random.choice(['A', 'B', 'C', 'D']),
        epc_score=random.randint(60, 95),
        in_conservation_area=random.choice([True, False]),
        school_quality_score=Decimal(str(random.uniform(0.6, 0.95))),
        distance_to_nearest_primary_m=random.randint(200, 1500),
        distance_to_nearest_secondary_m=random.randint(500, 2000),
        distance_to_nearest_station_m=random.randint(300, 1200),
        distance_to_nearest_airport_m=random.randint(5000, 25000),
        nearest_airport_code=random.choice(['LHR', 'LGW', 'STN', 'LCY']),
        imd_decile=random.randint(5, 10),
        crime_rate_percentile=random.randint(10, 50),
        flood_risk=random.choice(['very_low', 'low', 'medium']),
        max_download_speed_mbps=random.randint(50, 500),

        # Mock AVM
        avm_estimate=raw_listing.price_numeric * Decimal(str(random.uniform(0.95, 1.05))) if raw_listing.price_numeric else None,
        avm_confidence_score=Decimal(str(random.uniform(0.75, 0.95))),
    )

    # Calculate AVM delta
    if enriched.avm_estimate and enriched.price:
        enriched.avm_confidence_interval_lower = enriched.avm_estimate * Decimal('0.95')
        enriched.avm_confidence_interval_upper = enriched.avm_estimate * Decimal('1.05')
        enriched.avm_value_delta_pct = ((enriched.price - enriched.avm_estimate) / enriched.avm_estimate) * 100

    db.add(enriched)
    logger.info(f"  Created enriched listing (ID: {enriched.listing_id})")


if __name__ == "__main__":
    print("="*70)
    print("LOADING DEMO DATA: REAL SAVILLS LISTINGS")
    print("="*70)
    print("\nThis will:")
    print("1. Scrape 15 real properties from Savills")
    print("2. Download and upload images to S3 (5 per property)")
    print("3. Store in database with mock enrichment data")
    print("4. Ready for questionnaire demo")
    print("\nEstimated time: 5-10 minutes")
    print("="*70)

    input("\nPress ENTER to continue...")

    setup_demo_database()

    print("\n✅ Demo data loaded successfully!")
    print("\nNext steps:")
    print("1. Visit: http://localhost:8080/questionnaire-wizard.html")
    print("2. Fill in the wizard")
    print("3. See real Savills properties with images")
    print("4. Click any property → professional report")
