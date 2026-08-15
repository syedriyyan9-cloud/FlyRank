# Polite Scraper - Books to Scrape

A polite web scraper that extracts book data from the first 3 catalogue pages of Books to Scrape (60 books total). Built with **Python**, **Requests**, **BeautifulSoup**, and **Pydantic**.

---

## 🎯 Target Classification

- **Target Site**: Books to Scrape ([https://books.toscrape.com](https://books.toscrape.com))
- **Why**: A public sandbox built specifically for practicing web scraping.
- **Scope**: First 3 catalogue pages only (~60 books).
- **Data Collected**: Title, URL, price (raw + normalized), availability, rating, description, source page, timestamp.
- **robots.txt**: [https://books.toscrape.com/robots.txt](https://books.toscrape.com/robots.txt) — Checked and confirmed.
- **Ethics**: I will not reuse this code on another site without checking its rules and terms first.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **HTTP Requests**: Requests
- **HTML Parsing**: BeautifulSoup4
- **Schema Validation**: Pydantic
- **Output**: JSON

---

## 📦 Installation & Running

### Prerequisites

- Python 3.10+ installed

### Steps

1. **Navigate to scraper folder**
   ```bash
   cd scraper
   ```

2. **Create and activate virtual environment**
   - **On Mac/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **On Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the scraper**
   ```bash
   python main.py
   ```

5. **Check output**
   - `output/books.json` — Valid book records
   - `output/errors.json` — Invalid records (if any)
   - `output/run-report.json` — Run statistics

---

## 📡 Output Schema

### `books.json` — Valid Record
```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "It's hard to imagine a world without A Light in the Attic...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-08-15T20:50:58.491822+00:00"
}
```

### `run-report.json` — Run Statistics
```json
{
  "start_time": "2026-08-15T20:50:58.491822+00:00",
  "end_time": "2026-08-15T20:51:07.061040+00:00",
  "duration_seconds": 8.57,
  "total_urls": 61,
  "pages_fetched": 60,
  "cache_hits": 60,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "successful_urls_count": 60
}
```

---

## 🤝 Politeness Rules

| Rule | Implementation |
| :--- | :--- |
| **User-Agent** | `FlyRankInternshipA9/1.0 (+https://github.com/syedriyyan9-cloud/FlyRank)` |
| **Delay** | 500ms delay between real HTTP requests |
| **Timeout** | 10 seconds request timeout |
| **Cache** | Saves HTML locally; cache is used on subsequent runs |
| **Status Check** | Only `200 OK` responses are processed |
| **Retry** | One retry for server errors (`5xx`) |
| **No Retry** | `404` (not found) and `403` (forbidden) are not retried |

---

## 🧪 Testing & Failure Handling

- **Fake URL Test**:
  - A non-existent URL was added to test failure handling.
  - **Result**: Failed gracefully with a `404` error.
  - **Run continued**: 60 valid records were still saved cleanly.
  - **Reported**: Failure was logged properly in `run-report.json`.
- **Idempotency Test**:
  - Running the scraper twice produces the exact same 60 records without creating duplicates.

---

## 📁 Project Structure

```text
scraper/
├── main.py              # Main scraper script
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
├── .gitignore          # Git ignore rules (gitignored)
├── cache/              # Cached HTML files (gitignored)
├── output/             # Output JSON files
│   ├── books.json      # Valid book records
│   ├── errors.json     # Invalid records (if any)
│   └── run-report.json # Run statistics
└── venv/               # Virtual environment (gitignored)
```

---

## 🚀 Why No Browser?

This scraper uses **Requests + BeautifulSoup** (no headless browser) because:
- **Data is in HTML**: Books to Scrape sends all data in the initial HTML response.
- **No JavaScript rendering**: No dynamic content requiring browser execution.
- **Faster & Lighter**: Direct HTTP requests execute significantly faster than browser automation.
- **Lower Resource Usage**: Avoids browser CPU and memory overhead.
- **Simpler Architecture**: No WebDriver setup or browser version management complexity.

---

## ⚠️ Ethics Note

- Use official APIs when they exist.
- Never bypass login, paywalls, or rate blocks.
- Collect only what you need.
- Check `robots.txt` before scraping.
- Be a polite guest (apply rate limiting and descriptive custom User-Agents).
- Do not reuse this code on another site without checking its rules and terms first.

---

## 📊 Sample Run Report

```text
=== RUN COMPLETE ===
  Total URLs: 61
  Valid records: 60
  Invalid records: 0
  Failed pages: 1
  Cache hits: 60
  Duration: 8.57 seconds
```

---

## 🔗 GitHub Repository

https://github.com/syedriyyan9-cloud/FlyRank/tree/main/scraper