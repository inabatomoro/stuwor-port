import subprocess
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html

BASE_URL = "https://www.studio-works.jp/stuwor-port/"
SANITY_PROJECT_DIR = "./sanity"

def run_sanity_query(query):
    """Executes a Sanity CLI query and returns the JSON result."""
    try:
        result = subprocess.run(
            ['sanity', 'documents', 'query', query],
            cwd=SANITY_PROJECT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        # The query result might have a warning line at the end, so we need to find the JSON part.
        json_output = result.stdout
        # Find the start of the JSON array/object
        json_start = json_output.find('[')
        if json_start == -1:
            json_start = json_output.find('{')
        
        if json_start != -1:
            json_output = json_output[json_start:]

        return json.loads(json_output)
    except subprocess.CalledProcessError as e:
        print(f"Error executing Sanity query: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Sanity CLI output: {e}")
        print(f"Raw output that failed to parse:\n---\n{result.stdout}\n---")
        return None
    except FileNotFoundError:
        print("Error: 'sanity' command not found. Make sure Sanity CLI is installed and in your PATH.")
        return None


def generate_sitemap():
    """Generates the sitemap.xml file."""
    print("Starting sitemap generation...")

    # 1. Fetch slugs from Sanity
    print("Fetching slugs for posts and authors from Sanity...")
    posts = run_sanity_query('*[_type == "post" && defined(slug.current)]{"slug": slug.current}')
    authors = run_sanity_query('*[_type == "author" && defined(slug.current)]{"slug": slug.current}')

    if posts is None or authors is None:
        print("Could not fetch data from Sanity. Aborting sitemap generation.")
        return

    # 2. Build URL list
    urls = set()  # Use a set to avoid duplicates

    # Add static pages
    static_pages = ["index.html"]
    for page in static_pages:
        urls.add(BASE_URL + page)

    # Add post detail pages
    for post in posts:
        if post.get("slug"):
            # URL encode the slug to be safe, though it should be clean now
            urls.add(f"{BASE_URL}detail.html?slug={post['slug']}")

    # Add author pages
    for author in authors:
        if author.get("slug"):
            urls.add(f"{BASE_URL}creator.html?slug={author['slug']}")
            urls.add(f"{BASE_URL}creator-profile.html?slug={author['slug']}")
    
    print(f"Found {len(urls)} unique URLs to include in the sitemap.")

    # 3. Build XML structure
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in sorted(list(urls)):
        url_element = ET.SubElement(urlset, "url")
        loc_element = ET.SubElement(url_element, "loc")
        # We must escape special characters like '&'
        loc_element.text = html.escape(url)

    # 4. Write to file with pretty printing
    xml_string = ET.tostring(urlset, 'utf-8')
    dom = minidom.parseString(xml_string)
    pretty_xml_string = dom.toprettyxml(indent="  ")

    try:
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(pretty_xml_string)
        print("✅ Successfully generated and updated sitemap.xml!")
    except IOError as e:
        print(f"Error writing to sitemap.xml: {e}")


if __name__ == "__main__":
    generate_sitemap()
