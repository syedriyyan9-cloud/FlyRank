import requests
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://books.toscrape.com"
CATALOGUE_URL = urljoin(BASE_URL, "/catalogue/page-1.html")
CACHE_DIR = "cache"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/syedriyyan9-cloud/FlyRank)"
TIMEOUT = 10
DELAY = 0.5

os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_page(url, cache_key):
    """Fetch a page with caching"""
    cache_path = os.path.join(CACHE_DIR, cache_key)
    
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_key}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html, True
    
    print(f"FETCH: {url}")
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  Status: {response.status_code}, Size: {len(response.text)} bytes")
        return response.text, False
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch {url} - {e}")
        return None, False

def get_page_links(html, base_url):
    """Extract all book links from a catalogue page"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    # Find all book links (they're inside <h3> tags with <a>)
    for h3 in soup.find_all('h3'):
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href'):
            href = a_tag['href']
            # Convert relative to absolute URL
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
    
    return links

def get_next_page_url(html, base_url):
    """Find the 'next' page link"""
    soup = BeautifulSoup(html, 'html.parser')
    next_li = soup.find('li', class_='next')
    if next_li:
        a_tag = next_li.find('a')
        if a_tag and a_tag.get('href'):
            return urljoin(base_url, a_tag['href'])
    return None

def main():
    print("=== Scraper Started ===")
    start_time = time.time()
    
    all_book_urls = []
    page_urls = []
    current_url = CATALOGUE_URL
    page_num = 1
    
    # Fetch first 3 pages
    while current_url and page_num <= 3:
        print(f"\n--- Catalogue Page {page_num} ---")
        cache_key = f"catalogue-page-{page_num}.html"
        html, from_cache = fetch_page(current_url, cache_key)
        
        if not html:
            print(f"Failed to fetch page {page_num}")
            break
        
        # Get book links from this page
        book_links = get_page_links(html, current_url)
        print(f"  Found {len(book_links)} books on page {page_num}")
        
        all_book_urls.extend(book_links)
        page_urls.append(current_url)
        
        # Find next page
        if page_num < 3:
            next_url = get_next_page_url(html, current_url)
            if next_url:
                current_url = next_url
                page_num += 1
                # Wait between real requests
                if not from_cache:
                    time.sleep(DELAY)
            else:
                print("No next page found, stopping")
                break
        else:
            break
    
    # Remove duplicates
    unique_urls = list(dict.fromkeys(all_book_urls))
    
    print(f"\n=== Summary ===")
    print(f"  Catalogue pages: {page_num}")
    print(f"  Discovered book links: {len(all_book_urls)}")
    print(f"  Unique book URLs: {len(unique_urls)}")
    print(f"  Expected: 60 (20 per page × 3 pages)")
    
    # Save URLs for next stage
    with open(os.path.join(CACHE_DIR, "book_urls.txt"), 'w') as f:
        for url in unique_urls:
            f.write(url + '\n')

if __name__ == "__main__":
    main()