"""
Quick test of Foxtons scraper to see if it works
"""
import sys
import logging
from ingestion.scrapers.foxtons_scraper import create_foxtons_scraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("="*60)
print("TESTING FOXTONS SCRAPER")
print("="*60)

# Create scraper
scraper = create_foxtons_scraper(agent_id=999)  # Dummy ID for testing

print("\nFetching first page of listings from Foxtons...")
print("URL: https://www.foxtons.co.uk/properties-for-sale/london\n")

try:
    # Scrape just the first page for testing
    listings = scraper.scrape_page(1)

    print(f"\nSUCCESS! Found {len(listings)} listings\n")
    print("="*60)

    # Display first 3 listings
    for i, listing in enumerate(listings[:3], 1):
        print(f"\nLISTING {i}:")
        print(f"  Title: {listing.title}")
        print(f"  Price: {listing.price_text} ({listing.price_numeric})")
        print(f"  Address: {listing.raw_address}")
        print(f"  Postcode: {listing.postcode}")
        print(f"  Bedrooms: {listing.bedrooms}")
        print(f"  Bathrooms: {listing.bathrooms}")
        print(f"  Type: {listing.property_type}")
        print(f"  Images: {len(listing.image_urls)} images found")
        print(f"  URL: {listing.listing_url}")
        if listing.description:
            desc_preview = listing.description[:100] + "..." if len(listing.description) > 100 else listing.description
            print(f"  Description: {desc_preview}")

    print("\n" + "="*60)
    print("SCRAPER TEST SUCCESSFUL!")
    print("="*60)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    scraper.close()
