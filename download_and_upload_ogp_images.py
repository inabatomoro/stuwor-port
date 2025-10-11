import json
import requests
import subprocess
import os
import tempfile

def download_and_upload_ogp_images():
    image_asset_mapping = {}
    
    # Ensure SANITY_API_TOKEN is set
    sanity_api_token = os.environ.get('SANITY_API_TOKEN')
    if not sanity_api_token:
        print("Error: SANITY_API_TOKEN environment variable is not set.")
        print("Please set it before running this script.")
        return

    try:
        with open('scraped_data.json', 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
    except FileNotFoundError:
        print("Error: scraped_data.json not found. Please run scrape_website_data.py first.")
        return

    for post_id, data in scraped_data.items():
        image_url = data.get('image_url')
        if image_url:
            print(f"Processing OGP image for {post_id} from {image_url}...")
            try:
                # Download image to a temporary file
                response = requests.get(image_url, stream=True, timeout=10)
                response.raise_for_status() # Raise an exception for HTTP errors

                with tempfile.NamedTemporaryFile(delete=False) as temp_image_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_image_file.write(chunk)
                    temp_file_path = temp_image_file.name
                
                # Upload image to Sanity using upload_image.js
                # Ensure upload_image.js is executable or called with node
                upload_command = ['node', 'upload_image.js', temp_file_path]
                upload_process = subprocess.run(upload_command, capture_output=True, text=True, env=os.environ)
                
                if upload_process.returncode == 0:
                    asset_info = json.loads(upload_process.stdout)
                    asset_id = asset_info['_id']
                    image_asset_mapping[post_id] = asset_id
                    print(f"  > Uploaded {image_url} to Sanity. Asset ID: {asset_id}")
                else:
                    print(f"  > Error uploading image for {post_id}: {upload_process.stderr}")

            except requests.exceptions.RequestException as e:
                print(f"  > Error downloading image for {post_id} from {image_url}: {e}")
            except json.JSONDecodeError as e:
                print(f"  > Error parsing upload_image.js output for {post_id}: {e}\nOutput: {upload_process.stdout}")
            except Exception as e:
                print(f"  > An unexpected error occurred for {post_id}: {e}")
            finally:
                # Clean up temporary file
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            print(f"Skipping {post_id}: No image_url found in scraped_data.json.")

    with open('image_asset_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(image_asset_mapping, f, indent=2, ensure_ascii=False)
    
    print("\nimage_asset_mapping.json created successfully.")

if __name__ == '__main__':
    download_and_upload_ogp_images()
