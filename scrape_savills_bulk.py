"""
Scrape 50-100 Savills properties for demo
Saves to JSON file (no database needed for quick demo)
"""
import json
import logging
from ingestion.scrapers.savills_scraper import create_savills_scraper

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("="*70)
print("SCRAPING 50-100 SAVILLS PROPERTIES")
print("="*70)
print("\nThis will:")
print("- Scrape multiple pages from Savills")
print("- Extract: price, beds, baths, address, postcode, description")
print("- Get image URLs (10-30 per property)")
print("- Save to savills_properties.json")
print("\nEstimated time: 10-15 minutes")
print("="*70)

input("\nPress ENTER to start scraping...")

scraper = create_savills_scraper(agent_id=3)

all_listings = []
target_count = 50

print(f"\nScraping pages until we have {target_count} properties...")

page = 1
while len(all_listings) < target_count and page <= 3:  # Max 3 pages
    print(f"\nPage {page}...")
    listings = scraper.scrape_page(page)

    print(f"  Found {len(listings)} listings on this page")

    all_listings.extend(listings)
    print(f"  Total so far: {len(all_listings)}")

    page += 1

# Trim to target
all_listings = all_listings[:target_count]

print(f"\n{'='*70}")
print(f"SCRAPED {len(all_listings)} PROPERTIES")
print(f"{'='*70}")

# Convert to JSON-serializable format
properties_data = []
for listing in all_listings:
    prop = {
        'external_id': listing.external_listing_id,
        'title': listing.title,
        'price': float(listing.price_numeric) if listing.price_numeric else None,
        'price_text': listing.price_text,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'property_type': listing.property_type,
        'address': listing.raw_address,
        'postcode': listing.postcode,
        'description': listing.description,
        'tenure': listing.tenure,
        'image_urls': listing.image_urls,
        'listing_url': listing.listing_url
    }
    properties_data.append(prop)

# Save to JSON
with open('savills_properties.json', 'w', encoding='utf-8') as f:
    json.dump(properties_data, f, indent=2, ensure_ascii=False)

print(f"\nSaved to: savills_properties.json")
print(f"Total properties: {len(properties_data)}")
print(f"Total images: {sum(len(p['image_urls']) for p in properties_data)}")

# Show sample
print(f"\nSample properties:")
for i, prop in enumerate(properties_data[:5], 1):
    print(f"\n{i}. {prop['title']}")
    print(f"   Price: {prop['price_text']}")
    print(f"   {prop['bedrooms']} beds, {prop['bathrooms']} baths")
    print(f"   {len(prop['image_urls'])} images")

print(f"\n{'='*70}")
print("SCRAPING COMPLETE!")
print(f"{'='*70}")

scraper.close()
