"""
Complete test: Scrape Savills listing + Upload images to S3
"""
import logging
from ingestion.scrapers.savills_scraper import create_savills_scraper
from ingestion.storage.s3_storage import get_storage_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("="*70)
print("COMPLETE TEST: SAVILLS SCRAPER + S3 IMAGE UPLOAD")
print("="*70)

# Create scraper
scraper = create_savills_scraper(agent_id=3)

# Create S3 storage
s3_storage = get_storage_manager()

print("\n1. Scraping first page from Savills...")
listings = scraper.scrape_page(1)

if listings and len(listings) > 0:
    # Take first listing
    listing = listings[0]

    print(f"\n2. Successfully scraped listing:")
    print(f"   ID: {listing.external_listing_id}")
    print(f"   Title: {listing.title}")
    print(f"   Price: {listing.price_text} ({listing.price_numeric})")
    print(f"   Address: {listing.raw_address}")
    print(f"   Postcode: {listing.postcode}")
    print(f"   Bedrooms: {listing.bedrooms}")
    print(f"   Bathrooms: {listing.bathrooms}")
    print(f"   Property Type: {listing.property_type}")
    print(f"   Tenure: {listing.tenure}")

    if listing.description:
        print(f"\n3. Description ({len(listing.description)} chars):")
        print(f"   {listing.description[:150]}...")

    print(f"\n4. Images ({len(listing.image_urls)} found):")
    for i, url in enumerate(listing.image_urls[:5], 1):
        print(f"   {i}. {url}")

    if len(listing.image_urls) > 5:
        print(f"   ... and {len(listing.image_urls) - 5} more")

    # Upload images to S3
    if listing.image_urls:
        print(f"\n5. Uploading {len(listing.image_urls)} images to S3...")
        print(f"   Bucket: uk-property-images")
        print(f"   Path: images/3/999/")

        s3_urls = s3_storage.upload_listing_images(
            listing_id=999,  # Test ID
            image_urls=listing.image_urls[:3],  # Upload first 3 for testing
            agent_id=3
        )

        print(f"\n6. Successfully uploaded {len(s3_urls)} images to S3:")
        for i, s3_url in enumerate(s3_urls, 1):
            print(f"   {i}. {s3_url}")

        print("\n" + "="*70)
        print("SUCCESS! Complete flow working:")
        print("  - Scraped listing from Savills")
        print(f"  - Extracted {len(listing.image_urls)} image URLs")
        print(f"  - Uploaded {len(s3_urls)} images to S3")
        print("="*70)

    else:
        print("\nNo images found to upload")

else:
    print("\nNo listings found")

scraper.close()
