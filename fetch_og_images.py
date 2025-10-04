import csv
import json
import re
from urllib.request import urlopen, Request
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_og_image(url):
    try:
        # Add a user-agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Simple regex to find og:image content
            match = re.search(r'<meta\s+(?:property="og:image"|name="og:image")\s+content="([^"]+)"', html)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def create_image_mapping():
    mapping = {}
    with open('posts.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            post_id = row['id']
            website_url = row.get('Website URL')
            if website_url and website_url.startswith('http'):
                print(f"Fetching OGP image for {post_id} from {website_url}...")
                og_image_url = fetch_og_image(website_url)
                if og_image_url:
                    mapping[post_id] = og_image_url
                    print(f"  > Found: {og_image_url}")
                else:
                    print(f"  > OGP image not found.")
            else:
                print(f"Skipping {post_id} as it has no valid Website URL.")
    
    with open('image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("\nimage_mapping.json created successfully.")

if __name__ == '__main__':
    create_image_mapping()
