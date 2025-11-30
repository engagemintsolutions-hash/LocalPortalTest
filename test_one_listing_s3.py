"""
Test: Scrape ONE Savills listing + Upload images to S3
"""
import logging
from ingestion.scrapers.savills_scraper import SavillsScraper, ScraperConfig
from ingestion.storage.s3_storage import get_storage_manager

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("="*70)
print("TEST: ONE SAVILLS LISTING + S3 UPLOAD")
print("="*70)

# Create scraper with max_pages=1
config = ScraperConfig(
    agent_id=3,
    agent_name="Savills",
    base_url="https://search.savills.com",
    listings_url_template="https://search.savills.com/list/property-for-sale/uk?Page={page}",
    max_pages=1,  # Just first page
    delay_seconds=2.5
)

scraper = SavillsScraper(config)
s3_storage = get_storage_manager()

print("\nScraping first page...")
listings = scraper.scrape_page(1)

if listings and len(listings) > 0:
    # Just take the FIRST listing
    listing = listings[0]

    print(f"\nLISTING DETAILS:")
    print(f"  Title: {listing.title}")
    print(f"  Price: {listing.price_text}")
    print(f"  Address: {listing.raw_address}")
    print(f"  Postcode: {listing.postcode}")
    print(f"  Beds: {listing.bedrooms}, Baths: {listing.bathrooms}")
    print(f"  Type: {listing.property_type}")

    if listing.description:
        print(f"\n  Description: {listing.description[:200]}...")

    print(f"\n  Images Found: {len(listing.image_urls)}")
    for i, url in enumerate(listing.image_urls[:5], 1):
        print(f"    {i}. {url}")
    if len(listing.image_urls) > 5:
        print(f"    ... and {len(listing.image_urls)-5} more")

    # Upload to S3
    if listing.image_urls:
        print(f"\nUPLOADING {min(3, len(listing.image_urls))} IMAGES TO S3...")

        s3_urls = s3_storage.upload_listing_images(
            listing_id=999,
            image_urls=listing.image_urls[:3],  # First 3 images
            agent_id=3
        )

        print(f"\nSUCCESS! Uploaded {len(s3_urls)} images:")
        for s3_url in s3_urls:
            print(f"  - {s3_url}")

        # Verify in S3
        print("\nVerifying in S3...")
        verify_urls = s3_storage.get_listing_image_urls(listing_id=999, agent_id=3)
        print(f"  S3 confirms {len(verify_urls)} images stored")

        print("\n" + "="*70)
        print("COMPLETE SUCCESS!")
        print("="*70)
        print("Scraped: Address, Price, Beds, Baths, Description")
        print(f"Images: Extracted {len(listing.image_urls)}, Uploaded {len(s3_urls)} to S3")
        print("="*70)

scraper.close()
