# Pattern Detection Feature

## Overview
The scraper now automatically detects site-specific HTML structure when you add cookies for a new domain. This ensures optimal scraping for different XenForo forum variations.

## How It Works

### 1. When Adding Cookies
Run `python get_cookies.py` and choose option 1. After extracting cookies, you'll be asked:

```
═══════════════════════════════════════════════════════════════
DETECT SITE PATTERNS (OPTIONAL)
═══════════════════════════════════════════════════════════════

Provide a sample thread URL to auto-detect site structure.
This helps the scraper work better with site-specific HTML.

Sample thread URL (or press ENTER to skip):
```

### 2. Pattern Detection Process
The pattern detector analyzes the thread HTML and detects:

- **Post containers** - CSS selectors for post elements
- **Content wrappers** - Classes for post content
- **Author selectors** - How to find usernames
- **Date selectors** - Time/datetime elements
- **Reaction selectors** - Like/reaction counters
- **Attachment selectors** - Image/file containers
- **Pagination selectors** - Page navigation elements
- **Post ID attributes** - How posts are identified

### 3. Saved Patterns
Patterns are saved in `cookies.json` alongside cookies:

```json
{
  "domains": {
    "celebforum.to": {
      "url": "https://celebforum.to",
      "string": "cookie_data...",
      "dict": {...},
      "list": [...],
      "patterns": {
        "version": "1.0",
        "thread_url_sample": "https://celebforum.to/threads/example.123/",
        "selectors": {
          "post_container": [".message", "article.message"],
          "author": [".username"],
          "date": ["time[datetime]"],
          "reactions": [".reactionsBar"],
          "attachments": [".attachment"],
          "pagination": [".pageNav"]
        },
        "classes": {
          "content_wrapper": ["bbWrapper"]
        },
        "attributes": {
          "post_id": "data-content"
        }
      }
    }
  }
}
```

### 4. Automatic Loading
When you use `quick_start.py`, patterns are automatically loaded and applied:

```
✓ Loaded cookies for celebforum.to
✓ Loaded site-specific patterns (version 1.0)
```

## Benefits

1. **Works with Different XenForo Versions** - Some forums use different CSS classes
2. **Better Accuracy** - Uses site-specific selectors instead of generic fallbacks
3. **Future-Proof** - If a forum changes structure, just re-run cookie extraction
4. **Automatic** - No manual configuration needed

## Fallback Behavior

If patterns aren't detected or available, the scraper uses default XenForo patterns that work with most forums.

## Manual Pattern Updates

You can manually edit patterns in `cookies.json` if needed:

```json
{
  "domains": {
    "example.com": {
      "patterns": {
        "selectors": {
          "post_container": [".custom-post-class"]
        }
      }
    }
  }
}
```

## Example: Different XenForo Sites

**Site A** (default XenForo):
- Post container: `.message`
- Content wrapper: `.bbWrapper`
- Date: `time[datetime]`

**Site B** (custom theme):
- Post container: `.post`
- Content wrapper: `.message-body`
- Date: `.DateTime`

The pattern detector automatically adapts to both!
