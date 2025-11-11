# XenForo Scraper - Final Project Structure

## Core Files (Production Ready)

### Main Application Files
- **`scraper.py`** - Core scraping engine for XenForo forums (760+ lines)
- **`models.py`** - Data models (Thread, Post, User, Attachment, MediaEmbed, Link)
- **`pattern_detector.py`** - Auto-detects site-specific HTML patterns (230+ lines)
- **`quick_start.py`** - Easy-to-use multi-domain scraper with auto cookie/pattern loading
- **`get_cookies.py`** - Cookie manager with pattern detection (510+ lines)

### Utility Files
- **`view_json.py`** - JSON data viewer and statistics

### Configuration Files
- **`requirements.txt`** - Python dependencies
- **`cookies.json`** - Stored cookies & patterns for multiple domains
- **`.gitignore`** - Git ignore rules

### Documentation Files
- **`README.md`** - Complete user documentation
- **`PROJECT_STRUCTURE.md`** - This file (project overview)
- **`PATTERN_DETECTION.md`** - Pattern detection feature guide
- **`.github/copilot-instructions.md`** - AI assistant guidance

### Output
- **`downloads/{thread_id}/thread_{thread_id}.json`** - Scraped thread data organized by thread ID

---

## Current JSON Structure

```json
{
  "thread_id": "123456",
  "title": "Thread Title",
  "url": "https://forum.com/threads/example.123456/",
  "start_date": "2024-01-01",
  "tags": ["tag1", "tag2"],
  "prefixes": ["Prefix1"],
  "social_links": [
    {
      "url": "https://onlyfans.com/username",
      "text": "OnlyFans",
      "platform": "onlyfans"
    }
  ],
  "total_pages": 5,
  "total_posts": 147,
  "posts": [
    {
      "post_id": "789",
      "author": {
        "username": "User123",
        "user_id": "456",
        "profile_url": "...",
        "user_title": "Member",
        "messages": 1000,
        "reaction_score": 5000,
        "points": 250
      },
      "content": "Plain text content only",
      "date": "2024-01-01T12:00:00+00:00",
      "reactions": 54,
      "attachments": [...],
      "media_embeds": [...],
      "links": [...]
    }
  ]
}
```

---

## Features

### ✅ Multi-Domain Support
- Store cookies for unlimited XenForo forums in one file
- Automatic domain detection from URLs
- Easy cookie management and testing

### ✅ Auto-Pattern Detection (NEW)
- Analyzes each site's HTML structure
- Detects CSS selectors for posts, authors, dates, reactions, etc.
- Saves patterns with cookies for automatic loading
- Works with different XenForo versions and custom themes

### ✅ Smart Scraping
- Scrapes ALL pages by default
- Automatic pagination detection
- Rate limiting to respect servers
- Robust error handling

### ✅ Rich Data Extraction
- **Content:** Plain text only (no HTML clutter)
- **Attachments:** Images, videos, documents
- **Media Embeds:** YouTube, iframes, etc.
- **Links:** External, internal, image links
- **Social Links:** Aggregated TikTok, OnlyFans, Instagram, X, etc.
- **User Data:** Profile info, stats, titles

### ✅ Clean Structure
- No redundant fields (removed post_number, content_html)
- Organized data models
- Easy JSON parsing

---

## Quick Usage

### 1. Setup Cookies
```bash
python get_cookies.py
```
Choose option 1, add cookies for your forums

### 2. Start Scraping
```bash
python quick_start.py
```
Paste any thread URL, press Enter to scrape all pages

### 3. View Results
```bash
python view_json.py
```
View and analyze scraped data

---

## Project Cleanup History

### Removed Files (Cleanup Nov 2025)
- ❌ `example.py` - Old basic examples
- ❌ `example_with_auth.py` - Replaced by get_cookies.py
- ❌ `exmple_source.txt` - Sample HTML (no longer needed)
- ❌ `test_structure.py` - Development test file
- ❌ `test_pagination.py` - Development test file
- ❌ `setup.bat` - Redundant setup script
- ❌ `CHANGES.md` - Outdated documentation
- ❌ `IMPLEMENTATION_COMPLETE.md` - Outdated documentation
- ❌ `JSON_STRUCTURE_UPDATE.md` - Outdated documentation
- ❌ `QUICKGUIDE.md` - Merged into README
- ❌ `QUICKSTART.md` - Merged into README

### Removed Features
- ❌ Image/video count per post (inaccurate detection)
- ❌ `content_html` field (unnecessary duplication)
- ❌ `post_number` field (redundant with post_id)

---

## Dependencies

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.0.0
webdriver-manager>=4.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## File Size Reference

- **Code Files:** ~3 files, ~50KB total
- **Config Files:** ~4 files, ~5KB total
- **Output:** Variable (typical thread: 20-500KB per JSON)

---

## Support Multiple Forums

Works with ANY XenForo forum:
- celebforum.to
- nudostar.com
- simpcity.cr
- And any other XenForo-based forum!

Just add cookies and start scraping!

---

**Last Updated:** November 11, 2025
**Status:** Production Ready ✅
