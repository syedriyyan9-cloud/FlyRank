import requests
import os
import time
import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError, HttpUrl, Field, field_validator
from typing import Optional

# Configuration
BASE_URL = "https://books.toscrape.com"
CATALOGUE_URL = urljoin(BASE_URL, "/catalogue/page-1.html")
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/syedriyyan9-cloud/FlyRank)"
TIMEOUT = 10
DELAY = 0.5

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== Pydantic Schema ==========

class BookRecord(BaseModel):
    """Schema for validated book records"""
    title: str
    product_url: str  # Changed from HttpUrl to str for easier validation
    price_text: str
    price_gbp: float
    availability_text: Optional[str] = None
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: str  # Changed from HttpUrl to str
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
        # Force UTF-8 encoding
        response.encoding = 'utf-8'
        
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
    # Remove currency symbol and any spaces
    # Handle both £ and Â£
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
    
    product_url = url
    source_page_url = source_page
    fetched_at = datetime.now(timezone.utc).isoformat()
    
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page_url,
        "fetched_at": fetched_at
    }

def validate_record(record):
    """Validate record against schema, return (is_valid, validated_record, error)"""
    try:
        # Debug: Print what we're validating
        print(f"  Validating: {record.get('title')}")
        print(f"  Price text: {record.get('price_text')}")
        
        # Normalize price
        price_gbp = normalize_price(record.get('price_text'))
        if price_gbp is None:
            raise ValueError(f"Invalid price: {record.get('price_text')}")
        
        # Add normalized price to record
        record['price_gbp'] = price_gbp
        
        # Validate with Pydantic
        validated = BookRecord(**record)
        return True, validated.model_dump(), None
    except ValidationError as e:
        print(f"  Validation Error: {e}")
        return False, None, str(e)
    except ValueError as e:
        print(f"  Value Error: {e}")
        return False, None, str(e)
    except Exception as e:
        print(f"  Unexpected Error: {e}")
        return False, None, str(e)

def main():
    print("=== Scraper Started ===")
    start_time = time.time()
    
    # Stage 1: Get book URLs
    urls_file = os.path.join(CACHE_DIR, "book_urls.txt")
    if not os.path.exists(urls_file):
        print("ERROR: Run Stage 2 first to discover book URLs")
        return
    
    with open(urls_file, 'r') as f:
        book_urls = [line.strip() for line in f if line.strip()]
    
    print(f"\nProcessing {len(book_urls)} books...")
    
    valid_records = []
    error_records = []
    seen_urls = set()
    
    for idx, book_url in enumerate(book_urls, 1):
        print(f"\n[{idx}/{len(book_urls)}] {book_url}")
        
        # Skip duplicates
        if book_url in seen_urls:
            print(f"  SKIPPED: Duplicate URL")
            continue
        seen_urls.add(book_url)
        
        # Fetch page
        cache_key = book_url.replace(BASE_URL, '').replace('/', '_').strip('_') + '.html'
        if not cache_key:
            cache_key = f"book_{idx}.html"
        
        html, from_cache = fetch_page(book_url, cache_key)
        
        if not html:
            print(f"  SKIPPED: Failed to fetch")
            error_records.append({
                "url": book_url,
                "error": "Failed to fetch page"
            })
            continue
        
        # Extract details
        raw = extract_book_details(html, book_url, CATALOGUE_URL)
        
        # Validate against schema
        is_valid, validated, error = validate_record(raw)
        
        if is_valid:
            valid_records.append(validated)
            print(f"  ✓ VALID: {validated['title']} - £{validated['price_gbp']}")
        else:
            error_records.append({
                "url": book_url,
                "error": error,
                "raw_data": raw
            })
            print(f"  ✗ INVALID: {error}")
        
        # Wait between real requests
        if not from_cache:
            time.sleep(DELAY)
    
    # Save output files
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_file, 'w', encoding='utf-8') as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
    
    errors_file = os.path.join(OUTPUT_DIR, "errors.json")
    with open(errors_file, 'w', encoding='utf-8') as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Summary ===")
    print(f"  Total books processed: {len(book_urls)}")
    print(f"  Valid records: {len(valid_records)}")
    print(f"  Invalid records: {len(error_records)}")
    print(f"  Records saved to: {books_file}")
    print(f"  Errors saved to: {errors_file}")

if __name__ == "__main__":
    main()