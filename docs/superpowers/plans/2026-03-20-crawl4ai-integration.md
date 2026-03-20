# Crawl4AI Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the News Fact-Checking Service to use Crawl4AI for high-precision browser-based extraction of news content and metadata.

**Architecture:** Replace the `httpx` and `BeautifulSoup4` scraper in `ContentExtractor` with `Crawl4AI`'s `AsyncWebCrawler`.

**Tech Stack:** Python, Crawl4AI, Playwright, Pydantic.

---

### Task 1: Update Dependencies and Installation

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add new dependencies.**
  Add `crawl4ai` and `playwright`.

- [ ] **Step 2: Install dependencies.**
  Run `pip install -r requirements.txt`.

- [ ] **Step 3: Setup Playwright.**
  Run `playwright install chromium`.

- [ ] **Step 4: Commit dependencies.**
  ```bash
  git add requirements.txt
  git commit -m "chore: add crawl4ai and playwright dependencies"
  ```

### Task 2: Implement Crawl4AI-based ContentExtractor

**Files:**
- Modify: `app/utils/content_extractor.py`
- Test: `tests/test_content_extractor.py`

- [ ] **Step 1: Update `app/utils/content_extractor.py`**
  Implement the new `AsyncWebCrawler` logic within the `extract` method.
  Ensure extraction logic for title, author, and date is updated to use Crawl4AI's metadata results.

- [ ] **Step 2: Verify original language preservation.**
  Confirm the extraction doesn't trigger any translation of Traditional Chinese content.

- [ ] **Step 3: Update existing tests.**
  Update `tests/test_content_extractor.py` to handle the new asynchronous extraction results.

- [ ] **Step 4: Commit implementation.**
  ```bash
  git add app/utils/content_extractor.py tests/test_content_extractor.py
  git commit -m "feat: upgrade ContentExtractor to Crawl4AI"
  ```

### Task 3: Integration Testing and README Update

**Files:**
- Modify: `README.md`
- Test: `tests/test_factcheck_integration.py`

- [ ] **Step 1: Run integration tests.**
  Verify that the full fact-checking pipeline works with the new scraper.
  Test with Yahoo News and other Taiwanese news sites.

- [ ] **Step 2: Update README.md (English & 中文)**
  - Update "System Architecture" diagram (replace BeautifulSoup with Crawl4AI).
  - Update "Modules" section to highlight the browser-based extraction engine.
  - Update "Installation" steps to include `playwright install`.

- [ ] **Step 3: Final commit.**
  ```bash
  git add README.md tests/test_factcheck_integration.py
  git commit -m "docs: update README with Crawl4AI architecture and extraction details"
  ```
