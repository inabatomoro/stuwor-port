import csv
import json
from datetime import datetime
import re

def slugify(text):
    # A simple slugify function
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', '-', text, flags=re.UNICODE)
    text = re.sub(r'[^\w\-\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]+', '', text, flags=re.UNICODE)
    text = re.sub(r'\-\-+', '-', text, flags=re.UNICODE)
    text = re.sub(r'^-+|-+$', '', text, flags=re.UNICODE)
    return text

def convert_authors():
    # Load the author image asset mapping
    author_image_mapping = {}
    try:
        with open('author_image_asset_mapping.json', 'r', encoding='utf-8') as f:
            author_image_mapping = json.load(f)
        print("Loaded author image asset mapping.")
    except FileNotFoundError:
        print("author_image_asset_mapping.json not found, proceeding without author image data.")

    ndjson_authors = []
    author_ids = []
    with open('authors.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            author_id = f"author-{row['id']}"
            author_ids.append(author_id)
            author_name = row['name']
            author = {
                '_type': 'author',
                '_id': author_id,
                'name': author_name,
                'slug': {
                    '_type': 'slug',
                    'current': slugify(author_name)
                },
                'bio': [{
                    '_type': 'block',
                    'style': 'normal',
                    'children': [{
                        '_type': 'span',
                        'text': row['bio']
                    }]
                }]
            }

            # Add author image if it exists in the mapping
            if author_id in author_image_mapping:
                author['image'] = author_image_mapping[author_id]
                print(f"Added image for {author_id}")

            ndjson_authors.append(json.dumps(author, ensure_ascii=False))
    
    with open('authors.ndjson', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ndjson_authors))
    print("authors.ndjson created successfully.")
    return author_ids

def convert_posts():
    # Load scraped data
    scraped_data = {}
    try:
        with open('scraped_data.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        print("Loaded scraped_data.json.")
    except FileNotFoundError:
        print("scraped_data.json not found, proceeding with CSV data only.")

    # Load the image asset mapping
    image_mapping = {}
    try:
        with open('image_asset_mapping.json', 'r', encoding='utf-8') as f:
            image_mapping = json.load(f)
        print("Loaded image asset mapping.")
    except FileNotFoundError:
        print("image_asset_mapping.json not found, proceeding without image data.")

    ndjson_posts = []
    post_ids = []
    with open('posts.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            post_id = row['id']
            post_ids.append(post_id)
            
            # Start with data from CSV
            title = row['title']
            body_text = row['body']

            # Override with scraped data if available
            if post_id in scraped_data:
                scraped_post_data = scraped_data[post_id]
                if 'title' in scraped_post_data:
                    title = scraped_post_data['title']
                    print(f"Overriding title for {post_id} with scraped data.")
                if 'description' in scraped_post_data:
                    body_text = scraped_post_data['description']
                    print(f"Overriding body for {post_id} with scraped data.")

            post = {
                '_type': 'post',
                '_id': post_id,
                'title': title,
                'slug': {
                    '_type': 'slug',
                    'current': slugify(title)
                },
                'author': {
                    '_type': 'reference',
                    '_ref': f"author-{row['author_id']}"
                },
                'body': [{
                    '_type': 'block',
                    'style': 'normal',
                    'children': [{
                        '_type': 'span',
                        'text': body_text
                    }]
                }],
                'websiteUrl': row['Website URL'],
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            }

            # Add mainImage if it exists in the mapping
            if post_id in image_mapping:
                post['mainImage'] = image_mapping[post_id]
                print(f"Added mainImage for {post_id}")

            ndjson_posts.append(json.dumps(post, ensure_ascii=False))

    with open('posts.ndjson', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ndjson_posts))
    print("posts.ndjson created successfully.")
    return post_ids

if __name__ == '__main__':
    convert_authors()
    convert_posts()
