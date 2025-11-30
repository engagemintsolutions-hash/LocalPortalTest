"""
Test extracting images from Savills detail page
"""
import requests
from bs4 import BeautifulSoup
import json
import re

url = 'https://search.savills.com/property-detail/gbwmrstes250098'

print("Fetching Savills detail page...\n")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the script tag with Redux state
script = soup.find('script', string=lambda x: x and 'PropertyCardImagesGallery' in str(x))

if script:
    script_content = script.string

    # Find the propertyDetail object
    # It's in: {"props":{"...":"..."},"initialReduxState":{"propertyDetail":{"property":{...}}}}

    # Extract the full JSON
    match = re.search(r'{"dataManager"[^{]*"props".*}', script_content)

    if match:
        try:
            full_json = json.loads(match.group(0))

            # Navigate to property detail
            prop_detail = full_json.get('props', {}).get('initialReduxState', {}).get('propertyDetail', {}).get('property', {})

            if prop_detail:
                print("Property ID:", prop_detail.get('ExternalPropertyID'))
                print("Address:", prop_detail.get('FullAddress'))
                print("Price:", prop_detail.get('PriceString'))
                print("Bedrooms:", prop_detail.get('BedroomsInt'))
                print("Bathrooms:", prop_detail.get('BathroomsInt'))
                print("Description:", prop_detail.get('Description', '')[:100], '...')
                print()

                # Images!
                images = prop_detail.get('ImagesGallery', [])
                print(f"Found {len(images)} images:")
                for i, img in enumerate(images[:10], 1):
                    img_url = img.get('ImageUrl_L')  # Large version
                    caption = img.get('Caption', '')
                    print(f"  {i}. {img_url}")
                    if caption:
                        print(f"      Caption: {caption}")

                if len(images) > 10:
                    print(f"  ... and {len(images) - 10} more")

                print("\nSUCCESS! Images extracted!")

        except Exception as e:
            print(f"Error parsing JSON: {e}")
            import traceback
            traceback.print_exc()

else:
    print("Could not find Redux state script")
