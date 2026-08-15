import requests
import os
import time
from datetime import datetime
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://books.toscrape.com"
CATALOGUE_URL = urljoin(BASE_URL, "/catalogue/page-1.html")
CACHE_DIR = "cache"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/syedriyyan9-cloud/FlyRank)"
TIMEOUT = 10
DELAY = 0.5

# Create cache directory
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_page(url, cache_key):
    """Fetch a page with caching"""
    cache_path = os.path.join(CACHE_DIR, cache_key)
    
    # Check cache first
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_key}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html, True
    
    # Fetch from network
    print(f"FETCH: {url}")
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        
        # Save to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  Status: {response.status_code}, Size: {len(response.text)} bytes")
        return response.text, False
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch {url} - {e}")
        return None, False

def main():
    print("=== Scraper Started ===")
    print(f"Target: {CATALOGUE_URL}")
    
    # Fetch first catalogue page
    html, from_cache = fetch_page(CATALOGUE_URL, "catalogue-page-1.html")
    
    if html:
        print(f"Page fetched successfully (from cache: {from_cache})")
    else:
        print("Failed to fetch page")

if __name__ == "__main__":
    main()