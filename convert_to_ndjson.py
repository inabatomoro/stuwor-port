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
    ndjson_authors = []
    with open('authors.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            author_id = f"author-{row['id']}"
            author = {
                '_type': 'author',
                '_id': author_id,
                'name': row['name'],
                'bio': [{
                    '_type': 'block',
                    'style': 'normal',
                    'children': [{
                        '_type': 'span',
                        'text': row['bio']
                    }]
                }]
            }
            ndjson_authors.append(json.dumps(author, ensure_ascii=False))
    
    with open('authors.ndjson', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ndjson_authors))
    print("authors.ndjson created successfully.")


def convert_posts():
    # Load the image asset mapping
    image_mapping = {}
    try:
        with open('image_asset_mapping.json', 'r', encoding='utf-8') as f:
            image_mapping = json.load(f)
        print("Loaded image asset mapping.")
    except FileNotFoundError:
        print("image_asset_mapping.json not found, proceeding without image data.")

    ndjson_posts = []
    with open('posts.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['title']
            post_id = row['id']
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
                        'text': row['body']
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

if __name__ == '__main__':
    convert_authors()
    convert_posts()