"""
Extract listing data from Foxtons Next.js JSON
"""
import requests
from bs4 import BeautifulSoup
import json

url = "https://www.foxtons.co.uk/properties-for-sale/london"

response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'html.parser')

# Find Next.js data script
script = soup.find('script', id='__NEXT_DATA__', type='application/json')

if script:
    data = json.loads(script.string)

    # Navigate to properties
    try:
        props = data['props']['pageProps']

        # Look for properties in the data
        print("Keys in pageProps:")
        print(list(props.keys()))
        print()

        # Common keys where listings might be
        possible_keys = ['properties', 'listings', 'results', 'items', 'data', 'initialData', 'searchResults']

        for key in possible_keys:
            if key in props:
                print(f"\nFound '{key}' in pageProps!")
                listings = props[key]

                if isinstance(listings, list) and len(listings) > 0:
                    print(f"Contains {len(listings)} items")

                    # Show first listing structure
                    first = listings[0]
                    print(f"\nFirst listing keys: {list(first.keys()) if isinstance(first, dict) else type(first)}")

                    if isinstance(first, dict):
                        # Print sample listing
                        print("\nSample listing data:")
                        for k, v in list(first.items())[:15]:
                            print(f"  {k}: {v}")

                    break
        else:
            # Save full props for manual inspection
            with open('foxtons_props.json', 'w', encoding='utf-8') as f:
                json.dump(props, f, indent=2)
            print("\nSaved full pageProps to 'foxtons_props.json' for inspection")
            print(f"Top-level keys: {list(props.keys())}")

    except Exception as e:
        print(f"Error navigating data: {e}")
        # Save full data
        with open('foxtons_full_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Saved full data to 'foxtons_full_data.json'")
