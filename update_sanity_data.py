
import os
import subprocess
import json

# Import functions from our existing scripts
from fetch_author_images import create_author_image_mapping
from scrape_website_data import create_scraped_data_file
from download_and_upload_ogp_images import download_and_upload_ogp_images
from convert_to_ndjson import convert_authors, convert_posts

def run_command(command, cwd='.'):
    """Runs a shell command and returns its stdout."""
    print(f"\n[RUNNING]: {command}")
    try:
        process = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        print(process.stdout)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        raise

def get_existing_ids(doc_type, sanity_dir):
    """Get all existing document IDs for a given type from Sanity."""
    print(f"Fetching existing IDs for type: {doc_type}...")
    query = f'"*[_type == \"{doc_type}\"]._id"'
    command = f"sanity documents query {query}"
    output = run_command(command, cwd=sanity_dir)
    try:
        # The output might have a warning line, so we find the JSON part
        json_output_start = output.find('[')
        if json_output_start == -1:
            print(f"Warning: Could not find JSON array in Sanity output for {doc_type}.")
            return []
        
        ids = json.loads(output[json_output_start:])
        print(f"Found {len(ids)} existing {doc_type} documents.")
        return ids
    except json.JSONDecodeError:
        print(f"Error parsing JSON for {doc_type} IDs.")
        return []

def update_sanity():
    """The main function to run the full differential update process."""
    
    # 1. Get Sanity API Token from environment
    # I will retrieve this from my memory when executing.
    sanity_api_token = os.environ.get('SANITY_API_TOKEN')
    if not sanity_api_token:
        print("Error: SANITY_API_TOKEN is not set. Please set the environment variable.")
        return

    sanity_project_dir = "sanity"

    # 2. Run all data gathering and file generation scripts
    print("--- Step 1: Fetching and Generating Data ---")
    create_author_image_mapping()
    create_scraped_data_file()
    download_and_upload_ogp_images(sanity_api_token)
    
    print("\n--- Step 2: Converting Data to NDJSON ---")
    new_author_ids = convert_authors()
    new_post_ids = convert_posts()
    print(f"Generated {len(new_author_ids)} author documents.")
    print(f"Generated {len(new_post_ids)} post documents.")

    # 3. Get IDs of documents currently in Sanity
    print("\n--- Step 3: Fetching Current Sanity Document IDs ---")
    old_author_ids = get_existing_ids('author', sanity_project_dir)
    old_post_ids = get_existing_ids('post', sanity_project_dir)

    # 4. Import the new data (creates new documents and updates existing ones)
    print("\n--- Step 4: Importing Data to Sanity (Create/Update) ---")
    run_command("sanity dataset import ../authors.ndjson production --missing", cwd=sanity_project_dir)
    run_command("sanity dataset import ../posts.ndjson production --missing", cwd=sanity_project_dir)

    # 5. Calculate which documents to delete
    print("\n--- Step 5: Calculating Documents to Delete ---")
    author_ids_to_delete = [id for id in old_author_ids if id not in new_author_ids]
    post_ids_to_delete = [id for id in old_post_ids if id not in new_post_ids]

    # 6. Delete orphaned documents
    print("\n--- Step 6: Deleting Orphaned Documents ---")
    if author_ids_to_delete:
        print(f"Found {len(author_ids_to_delete)} authors to delete.")
        ids_string = ' '.join(author_ids_to_delete)
        run_command(f"sanity documents delete {ids_string}", cwd=sanity_project_dir)
    else:
        print("No authors to delete.")

    if post_ids_to_delete:
        print(f"Found {len(post_ids_to_delete)} posts to delete.")
        ids_string = ' '.join(post_ids_to_delete)
        run_command(f"sanity documents delete {ids_string}", cwd=sanity_project_dir)
    else:
        print("No posts to delete.")
        
    print("\n\n✅ Sanity update process completed successfully!")

if __name__ == '__main__':
    update_sanity()
