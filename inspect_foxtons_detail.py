"""
Inspect a Foxtons detail page to find images
"""
import requests
from bs4 import BeautifulSoup
import json

# Use a real Foxtons listing URL
url = "https://www.foxtons.co.uk/property-for-sale/chpk6210326"

print(f"Fetching: {url}\n")

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}, timeout=30)

soup = BeautifulSoup(response.content, 'html.parser')

# Find Next.js data
script = soup.find('script', id='__NEXT_DATA__', type='application/json')

if script:
    data = json.loads(script.string)

    # Navigate to page data
    page_data = data.get('props', {}).get('pageProps', {}).get('pageData', {})

    print("Keys in pageData:")
    print(list(page_data.keys()))
    print()

    # Look for main data
    if 'data' in page_data:
        prop_data = page_data['data']
        print("Keys in pageData.data:")
        print(list(prop_data.keys())[:30])
        print()

        # Description
        if 'description' in prop_data:
            desc = prop_data['description']
            print(f"Description (first 200 chars): {desc[:200]}")
            print()

        # Images
        for possible_key in ['images', 'photos', 'gallery', 'media', 'pictures']:
            if possible_key in prop_data:
                images = prop_data[possible_key]
                print(f"\nFound '{possible_key}' with {len(images) if isinstance(images, list) else 'non-list'} items")

                if isinstance(images, list) and len(images) > 0:
                    print(f"First image structure: {json.dumps(images[0], indent=2)[:300]}")
                    break

        # Save full data
        with open('foxtons_detail_data.json', 'w', encoding='utf-8') as f:
            json.dump(prop_data, f, indent=2)
        print("\nSaved full detail data to 'foxtons_detail_data.json'")

else:
    print("No __NEXT_DATA__ found")
