import csv
import json
import re
from urllib.request import urlopen, Request
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def scrape_website(url):
    scraped_data = {}
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')
            print(f"--- HTML for {url} (first 500 chars): {html[:500]} ---") # Debug print

            # Scrape title
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            print(f"  > Title match: {title_match}") # Debug print
            if title_match:
                scraped_data['title'] = title_match.group(1).strip()

            # Scrape meta description
            desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE)
            print(f"  > Description match: {desc_match}") # Debug print
            if desc_match:
                scraped_data['description'] = desc_match.group(1).strip()

            # Scrape og:image
            image_match = re.search(r'<meta\s+(?:property="og:image"|name="og:image")\s+content="([^"]+)"', html, re.IGNORECASE)
            print(f"  > Image match: {image_match}") # Debug print
            if image_match:
                scraped_data['image_url'] = image_match.group(1)

    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return scraped_data

def create_scraped_data_file():
    all_data = {}
    with open('posts.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            post_id = row['id']
            website_url = row.get('Website URL')
            if website_url and website_url.startswith('http'):
                print(f"Scraping data for {post_id} from {website_url}...")
                data = scrape_website(website_url)
                if data:
                    all_data[post_id] = data
                    print(f"  > Found: { ', '.join(data.keys())}")
                else:
                    print(f"  > No data found.")
            else:
                print(f"Skipping {post_id} as it has no valid Website URL.")
    
    with open('scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print("\nscraped_data.json created successfully.")

if __name__ == '__main__':
    create_scraped_data_file()
