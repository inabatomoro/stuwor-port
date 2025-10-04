import csv
import json
import re
from urllib.request import urlopen, Request
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_author_image_url(url):
    # For author images, we assume the URL directly points to the image.
    # No scraping of HTML needed, just return the URL.
    return url

def create_author_image_mapping():
    mapping = {}
    with open('authors.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            author_id = f"author-{row['id']}"
            image_url = row.get('Image URL') # Assuming the column is named 'Image URL'
            if image_url and image_url.startswith('http'):
                print(f"Found image URL for {author_id}: {image_url}")
                mapping[author_id] = image_url
            else:
                print(f"Skipping {author_id} as it has no valid Image URL.")
    
    with open('author_image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("\nauthor_image_mapping.json created successfully.")

if __name__ == '__main__':
    create_author_image_mapping()
