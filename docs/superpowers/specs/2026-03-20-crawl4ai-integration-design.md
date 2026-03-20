# Crawl4AI Integration for High-Precision News Extraction

## Overview
Upgrade the `ContentExtractor` from a basic `httpx` + `BeautifulSoup4` scraper to a high-precision asynchronous engine powered by **Crawl4AI**. This change will significantly improve the accuracy of article body extraction, metadata parsing (date/author), and overall robustness against JavaScript-heavy or anti-scraping news sites.

## Architecture: Browser-Based Asynchronous Extraction
The system will replace the current HTTP-only extraction logic with a browser-based strategy using **Playwright** via the `AsyncWebCrawler` interface.

### Core Enhancements
1.  **JavaScript Rendering**: Full support for dynamic content, allowing extraction of news from sites that load text via JS.
2.  **Magic Mode**: Enable Crawl4AI's "magic" mode to automatically bypass simple bot detection and optimize extraction parameters.
3.  **Markdown-First Logic**: Extract the article body as high-quality Markdown, which provides better semantic structure for the `DecomposerAgent`.
4.  **Enhanced Metadata**: Leverage Crawl4AI's internal schema to extract titles, publication dates, and authors more reliably.

## Components & Implementation

### 1. Updated Utility (`app/utils/content_extractor.py`)
*   **Engine**: `AsyncWebCrawler`.
*   **Strategy**: Use `DefaultMarkdownGenerationStrategy` with noise removal.
*   **Interface**: Maintain the existing `extract()` method signature for backward compatibility.

### 2. Dependency Management (`requirements.txt`)
*   Add `crawl4ai` and `playwright`.
*   Include a setup task to run `playwright install chromium`.

### 3. README Update
The "System Architecture" and "Modules" sections in `README.md` will be updated to reflect the upgrade to an "Intelligent Browser-based Scraper".

## Error Handling & Reliability
*   **Timeout Protection**: Explicit timeouts for browser initialization and page loading.
*   **Fallback**: If Crawl4AI fails due to environment issues, the system will provide a clear error message instructing the user to run the setup command.
*   **Language Preservation**: Ensure that Crawl4AI's extraction doesn't trigger any internal translation, preserving the original Traditional Chinese text.

## Success Criteria
*   Successfully extract content from JS-heavy sites (e.g., Yahoo News, certain Taiwanese news portals).
*   Correctly identify publication dates and authors across multiple site formats.
*   Maintain the 100% original language requirement.
