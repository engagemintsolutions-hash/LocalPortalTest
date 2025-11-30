"""
Test scraping from a simpler independent estate agent
Let's try a few to find one with accessible data
"""
import requests
from bs4 import BeautifulSoup

agents_to_test = [
    {
        'name': 'Hamptons',
        'url': 'https://www.hamptons.co.uk/properties-for-sale',
    },
    {
        'name': 'Savills',
        'url': 'https://search.savills.com/list/property-for-sale/uk',
    },
    {
        'name': 'KFH',
        'url': 'https://www.kfh.co.uk/property-for-sale',
    }
]

for agent in agents_to_test:
    print(f"\nTesting {agent['name']}...")
    print(f"URL: {agent['url']}")

    try:
        response = requests.get(agent['url'], headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)

        print(f"  Status: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for property cards
        property_cards = soup.find_all(class_=lambda x: x and ('property' in x.lower() or 'listing' in x.lower()))[:5]
        print(f"  Found {len(property_cards)} potential property elements")

        # Look for prices
        prices = soup.find_all(string=lambda x: x and '£' in str(x))[:5]
        print(f"  Found {len(prices)} price elements")
        if prices:
            print(f"  Sample prices: {[str(p).strip()[:30] for p in prices[:3]]}")

        # Look for images
        images = soup.find_all('img', src=lambda x: x and ('property' in x.lower() or 'listing' in x.lower() or 'image' in x.lower()))
        print(f"  Found {len(images)} property images")

        print(f"  Result: {'GOOD CANDIDATE' if len(property_cards) > 0 or len(prices) > 3 else 'Might need more work'}")

    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "="*60)
print("Test complete - choose the best candidate above")
