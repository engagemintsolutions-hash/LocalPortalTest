"""
Inspect Foxtons HTML structure to update scraper
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.foxtons.co.uk/properties-for-sale/london"

print("Fetching Foxtons page...")
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

soup = BeautifulSoup(response.content, 'html.parser')

# Try to find property listings
print("\n1. Looking for <article> tags:")
articles = soup.find_all('article')
print(f"   Found {len(articles)} <article> tags")

print("\n2. Looking for data-testid attributes:")
testids = soup.find_all(attrs={'data-testid': True})
print(f"   Found {len(testids)} elements with data-testid")
if testids:
    unique_testids = set([elem.get('data-testid') for elem in testids[:20]])
    print(f"   Sample testids: {list(unique_testids)[:10]}")

print("\n3. Looking for class names with 'property':")
property_divs = soup.find_all('div', class_=lambda x: x and 'property' in x.lower())
print(f"   Found {len(property_divs)} divs with 'property' in class")
if property_divs:
    print(f"   Sample classes: {[div.get('class') for div in property_divs[:3]]}")

print("\n4. Looking for links to property pages:")
property_links = soup.find_all('a', href=lambda x: x and '/property' in x)
print(f"   Found {len(property_links)} links containing '/property'")
if property_links:
    print(f"   Sample URLs: {[link['href'][:80] for link in property_links[:5]]}")

print("\n5. Looking for price elements:")
prices = soup.find_all(string=lambda x: x and '£' in x)
print(f"   Found {len(prices)} elements containing '£'")
if prices:
    print(f"   Sample prices: {[str(p).strip()[:50] for p in prices[:5]]}")

# Save HTML for manual inspection
with open('foxtons_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("\n6. Saved full HTML to 'foxtons_page.html' for inspection")

# Look for common property listing patterns
print("\n7. Looking for React/Next.js data:")
scripts = soup.find_all('script', type='application/json')
print(f"   Found {len(scripts)} JSON scripts (Next.js data)")

if scripts:
    import json
    for i, script in enumerate(scripts[:3]):
        try:
            data = json.loads(script.string)
            print(f"\n   Script {i+1} keys: {list(data.keys())[:10]}")
        except:
            pass
