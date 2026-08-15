import requests
import os
import time
import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError, Field, field_validator
from typing import Optional
import traceback

# Configuration
BASE_URL = "https://books.toscrape.com"
CATALOGUE_URL = urljoin(BASE_URL, "/catalogue/page-1.html")
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/syedriyyan9-cloud/FlyRank)"
TIMEOUT = 10
DELAY = 0.5
MAX_RETRIES = 1

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== Pydantic Schema ==========

class BookRecord(BaseModel):
    """Schema for validated book records"""
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: Optional[str] = None
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: str
    fetched_at: str
    
    @field_validator('price_gbp')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @field_validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

# ========== Helper Functions ==========

def fetch_page(url, cache_key, retry_count=0):
    """Fetch a page with caching and retry logic"""
    cache_path = os.path.join(CACHE_DIR, cache_key)
    
    # Check cache first
    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_key}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html, True, None
    
    print(f"FETCH: {url}")
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.encoding = 'utf-8'
        
        # Check status code
        if response.status_code == 404:
            return None, False, f"404 Not Found (page doesn't exist)"
        elif response.status_code == 403:
            return None, False, f"403 Forbidden (site said no)"
        elif response.status_code >= 500:
            # Server error - retry once
            if retry_count < MAX_RETRIES:
                print(f"  Server error {response.status_code}, retrying...")
                time.sleep(DELAY * 2)
                return fetch_page(url, cache_key, retry_count + 1)
            return None, False, f"Server error {response.status_code} after {MAX_RETRIES} retries"
        elif response.status_code != 200:
            return None, False, f"Status code {response.status_code}"
        
        # Save to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"  Status: {response.status_code}, Size: {len(response.text)} bytes")
        return response.text, False, None
    except requests.Timeout:
        if retry_count < MAX_RETRIES:
            print(f"  Timeout, retrying...")
            time.sleep(DELAY * 2)
            return fetch_page(url, cache_key, retry_count + 1)
        return None, False, f"Timeout after {MAX_RETRIES} retries"
    except requests.RequestException as e:
        return None, False, str(e)

def get_page_links(html, base_url):
    """Extract all book links from a catalogue page"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for h3 in soup.find_all('h3'):
        a_tag = h3.find('a')
        if a_tag and a_tag.get('href'):
            href = a_tag['href']
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

def normalize_price(price_text):
    """Convert £51.77 to 51.77"""
    if not price_text:
        return None
    cleaned = re.sub(r'[£€$Â]', '', price_text).strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract_book_details(html, url, source_page):
    """Extract all 8 fields from a book detail page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Title
    title_tag = soup.find('h1')
    title = title_tag.text.strip() if title_tag else None
    
    # Price
    price_tag = soup.find('p', class_='price_color')
    price_text = price_tag.text.strip() if price_tag else None
    
    # Availability
    avail_tag = soup.find('p', class_='instock availability')
    availability_text = avail_tag.text.strip() if avail_tag else None
    
    # Rating
    rating_map = {
        'star-rating One': 'One',
        'star-rating Two': 'Two',
        'star-rating Three': 'Three',
        'star-rating Four': 'Four',
        'star-rating Five': 'Five'
    }
    rating_tag = soup.find('p', class_='star-rating')
    rating_text = None
    if rating_tag:
        for class_name in rating_tag.get('class', []):
            if class_name in rating_map:
                rating_text = rating_map[class_name]
                break
    
    # Description
    desc_tag = soup.find('div', id='product_description')
    if desc_tag:
        desc_p = desc_tag.find_next('p')
        description = desc_p.text.strip() if desc_p else None
    else:
        description = None
    
    return {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def validate_record(record):
    """Validate record against schema"""
    try:
        price_gbp = normalize_price(record.get('price_text'))
        if price_gbp is None:
            raise ValueError(f"Invalid price: {record.get('price_text')}")
        
        record['price_gbp'] = price_gbp
        validated = BookRecord(**record)
        return True, validated.model_dump(), None
    except (ValidationError, ValueError) as e:
        return False, None, str(e)

def discover_book_urls():
    """Discover all 60 book URLs from first 3 pages"""
    all_book_urls = []
    current_url = CATALOGUE_URL
    page_num = 1
    
    while current_url and page_num <= 3:
        cache_key = f"catalogue-page-{page_num}.html"
        html, from_cache, error = fetch_page(current_url, cache_key)
        
        if not html:
            print(f"Failed to fetch catalogue page {page_num}")
            break
        
        book_links = get_page_links(html, current_url)
        all_book_urls.extend(book_links)
        
        # Find next page
        if page_num < 3:
            next_url = get_next_page_url(html, current_url)
            if next_url:
                current_url = next_url
                page_num += 1
                if not from_cache:
                    time.sleep(DELAY)
            else:
                break
        else:
            break
    
    # Remove duplicates
    return list(dict.fromkeys(all_book_urls))

def main():
    print("=== Scraper Started ===")
    start_time = time.time()
    
    # Track stats for report
    stats = {
        "start_time": datetime.now(timezone.utc).isoformat(),
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0,
        "failed_urls": [],
        "successful_urls": []
    }
    
    # Discover book URLs
    print("\n--- Discovering book URLs ---")
    book_urls = discover_book_urls()
    print(f"Found {len(book_urls)} unique book URLs")
    
    # Add a fake URL to test failure handling
    test_urls = book_urls + ["https://books.toscrape.com/catalogue/nonexistent-book_99999/index.html"]
    print(f"Testing with {len(test_urls)} URLs (including 1 fake)")
    
    valid_records = []
    error_records = []
    seen_urls = set()
    
    for idx, book_url in enumerate(test_urls, 1):
        print(f"\n[{idx}/{len(test_urls)}] {book_url}")
        
        # Skip duplicates
        if book_url in seen_urls:
            print(f"  SKIPPED: Duplicate URL")
            continue
        seen_urls.add(book_url)
        
        # Fetch page
        cache_key = book_url.replace(BASE_URL, '').replace('/', '_').strip('_') + '.html'
        if not cache_key:
            cache_key = f"book_{idx}.html"
        
        html, from_cache, error = fetch_page(book_url, cache_key)
        
        if from_cache:
            stats["cache_hits"] += 1
        
        if not html:
            print(f"  ✗ FAILED: {error}")
            stats["failed_pages"] += 1
            stats["failed_urls"].append({
                "url": book_url,
                "error": error
            })
            error_records.append({
                "url": book_url,
                "error": error
            })
            continue
        
        stats["pages_fetched"] += 1
        
        # Extract details
        raw = extract_book_details(html, book_url, CATALOGUE_URL)
        
        # Validate
        is_valid, validated, error = validate_record(raw)
        
        if is_valid:
            valid_records.append(validated)
            stats["valid_records"] += 1
            stats["successful_urls"].append(book_url)
            print(f"  ✓ VALID: {validated['title']} - £{validated['price_gbp']}")
        else:
            stats["invalid_records"] += 1
            stats["failed_pages"] += 1
            stats["failed_urls"].append({
                "url": book_url,
                "error": error
            })
            error_records.append({
                "url": book_url,
                "error": error,
                "raw_data": raw
            })
            print(f"  ✗ INVALID: {error}")
        
        # Wait between real requests
        if not from_cache:
            time.sleep(DELAY)
    
    # Calculate duration
    end_time = time.time()
    duration = end_time - start_time
    
    # Build run report
    report = {
        "start_time": stats["start_time"],
        "end_time": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration, 2),
        "total_urls": len(test_urls),
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": stats["valid_records"],
        "invalid_records": stats["invalid_records"],
        "failed_pages": stats["failed_pages"],
        "failed_urls": stats["failed_urls"][:10],  # Limit for readability
        "successful_urls_count": len(stats["successful_urls"])
    }
    
    # Save output files
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_file, 'w', encoding='utf-8') as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
    
    errors_file = os.path.join(OUTPUT_DIR, "errors.json")
    with open(errors_file, 'w', encoding='utf-8') as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)
    
    report_file = os.path.join(OUTPUT_DIR, "run-report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"=== RUN COMPLETE ===")
    print(f"{'='*50}")
    print(f"  Total URLs: {len(test_urls)}")
    print(f"  Valid records: {stats['valid_records']}")
    print(f"  Invalid records: {stats['invalid_records']}")
    print(f"  Failed pages: {stats['failed_pages']}")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Duration: {report['duration_seconds']} seconds")
    print(f"\n  Output saved to:")
    print(f"    - {books_file}")
    print(f"    - {errors_file}")
    print(f"    - {report_file}")

if __name__ == "__main__":
    main()