"""
Test fetching a single Foxtons listing with images
"""
import logging
from ingestion.scrapers.foxtons_scraper_v2 import create_foxtons_scraper

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("="*60)
print("TESTING SINGLE FOXTONS LISTING (with images)")
print("="*60)

scraper = create_foxtons_scraper()

# Get first page to get a listing URL
print("\n1. Fetching search results page...")
listings = scraper.scrape_page(1)

if listings and len(listings) > 0:
    # Take just the first listing to test
    first_listing = listings[0]

    print(f"\n2. Successfully scraped first listing:")
    print(f"   ID: {first_listing.external_listing_id}")
    print(f"   Title: {first_listing.title}")
    print(f"   Price: {first_listing.price_text}")
    print(f"   Address: {first_listing.raw_address}")
    print(f"   Postcode: {first_listing.postcode}")
    print(f"   Bedrooms: {first_listing.bedrooms}")
    print(f"   Bathrooms: {first_listing.bathrooms}")
    print(f"   Property Type: {first_listing.property_type}")
    print(f"   Tenure: {first_listing.tenure}")

    print(f"\n3. Description:")
    if first_listing.description:
        desc_preview = first_listing.description[:200] + "..." if len(first_listing.description) > 200 else first_listing.description
        print(f"   {desc_preview}")
    else:
        print("   (No description)")

    print(f"\n4. Images:")
    print(f"   Found {len(first_listing.image_urls)} images")
    if first_listing.image_urls:
        for i, url in enumerate(first_listing.image_urls[:5], 1):
            print(f"   {i}. {url}")
        if len(first_listing.image_urls) > 5:
            print(f"   ... and {len(first_listing.image_urls) - 5} more")
    else:
        print("   (No images found - may need to adjust selectors)")

    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60)

else:
    print("\nNo listings found on search page")

scraper.close()
