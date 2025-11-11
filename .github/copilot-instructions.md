# GitHub Copilot Instructions for XenForo Scraper

## Project Overview
This is a Python-based web scraper for XenForo forum platforms. It extracts threads, posts, user data, attachments, and social media links from any XenForo-based forum with multi-domain cookie support.

## Key Architecture

### Data Models (`models.py`)
- **Thread**: Contains thread metadata, posts array, and aggregated social_links
- **Post**: Contains post_id, author, plain text content (no HTML), date, reactions, attachments, media_embeds, links
- **User**: Forum user with username, profile data, stats
- **Attachment**: Files (images, videos, documents) with URLs
- **MediaEmbed**: Embedded media (YouTube, iframes, etc.)
- **Link**: Hyperlinks with type classification (external, internal, image_link)

**Important**: 
- Post content is PLAIN TEXT ONLY (no content_html field)
- No post_number field (use post_id for identification)
- Thread has social_links array aggregating all social media from posts

### Scraper (`scraper.py`)
- **XenforoScraper class**: Main scraping engine
- Uses BeautifulSoup4 + lxml for HTML parsing
- **Site-specific patterns**: Uses detected CSS selectors for each domain
- Implements rate limiting (configurable delay between requests)
- Multi-page support with automatic pagination detection
- Cookie-based authentication for accessing protected content

**Key Methods**:
- `scrape_thread()`: Main method, scrapes entire thread (all pages by default)
- `_extract_posts_from_page()`: Parses posts from HTML
- `_extract_social_links_from_posts()`: Aggregates social media links
- `_extract_attachments()`: Extracts images and files
- `_extract_media_embeds()`: Extracts iframes and embedded videos
- `_extract_links()`: Extracts all hyperlinks
- `export_thread_to_dict()`: Converts Thread object to JSON-serializable dict

### Cookie Manager (`get_cookies.py`)
- **Multi-domain support**: Stores cookies for unlimited forums in one cookies.json file
- Uses Selenium + Chrome WebDriver for automated cookie extraction
- **Auto-pattern detection**: Analyzes sample thread to detect site-specific HTML structure
- Cookie testing functionality for all or specific domains
- Format: `{"domains": {"domain.com": {"url": "...", "string": "...", "dict": {}, "list": [], "patterns": {...}}}}`

**Supported Social Platforms**:
TikTok, OnlyFans, Instagram, Twitter/X, Facebook, Fansly, Patreon, YouTube, Snapchat, Reddit, Twitch, Discord, Telegram, LinkedIn, Pinterest, Tumblr, Vimeo, Threads, Bluesky

### User Interface (`quick_start.py`)
- Auto-detects domain from thread URL
- Loads appropriate cookies and patterns automatically
- Defaults to scraping ALL pages (not just 1)
- Exports to JSON: `downloads/{thread_id}/thread_{thread_id}.json`
- Shows statistics only (no content preview)

### Pattern Detector (`pattern_detector.py`)
- **PatternDetector class**: Analyzes thread HTML structure
- Detects CSS selectors for posts, authors, dates, reactions, attachments
- Detects pagination patterns and post ID attributes
- Returns site-specific pattern dictionary
- Saved with cookies for automatic loading

## Coding Standards

### When Adding Features:
1. **Data Models**: Update dataclasses in models.py first
2. **Extraction Logic**: Add extraction methods to scraper.py
3. **Export Format**: Update export_thread_to_dict() to include new fields
4. **Backward Compatibility**: Ensure old cookies.json files still work

### When Fixing Bugs:
1. **Check HTML Structure**: XenForo CSS classes may vary across forums
2. **Test Multiple Domains**: Verify fixes work on different XenForo sites
3. **Handle Missing Data**: Use Optional types and default values
4. **Error Handling**: Wrap extraction code in try-except blocks

### Best Practices:
- Keep content as PLAIN TEXT (strip all HTML)
- Remove duplicate data (deduplicate URLs in social_links)
- Use absolute URLs (urljoin for relative paths)
- Respect rate limits (configurable delay parameter)
- Log progress for multi-page scrapes
- Export organized by post_id in downloads folder

## File Organization

### Core Files:
- `scraper.py` - Main scraping engine (760+ lines)
- `models.py` - Data models with dataclasses
- `quick_start.py` - User-friendly CLI interface
- `get_cookies.py` - Multi-domain cookie manager (510+ lines)
- `pattern_detector.py` - Site structure analyzer (230+ lines)
- `view_json.py` - JSON viewer and statistics

### Configuration:
- `requirements.txt` - Python dependencies
- `cookies.json` - Multi-domain cookie storage
- `.gitignore` - Exclude cookies, cache, JSON outputs

### Documentation:
- `README.md` - User documentation
- `PROJECT_STRUCTURE.md` - Project overview

## Common Tasks

### Adding New Social Platform:
1. Add domain mapping to `_extract_social_links_from_posts()` in scraper.py
2. Format: `'platform.com': 'platform_name'`

### Changing Output Location:
Update `quick_start.py` where JSON is saved (currently downloads/{post_id}/thread_{thread_id}.json)

### Adding New Data Field:
1. Add to dataclass in models.py
2. Add extraction logic in scraper.py
3. Add to export_thread_to_dict() method
4. Update __post_init__ if it needs default initialization

### Testing Cookie Validity:
Use `get_cookies.py` → Option 4 (Test all cookies)

## Dependencies
- requests: HTTP client
- beautifulsoup4: HTML parsing
- lxml: Fast XML/HTML parser
- selenium: Browser automation for cookies
- webdriver-manager: Auto ChromeDriver management

## Important Notes
- XenForo CSS classes: `message`, `bbWrapper`, `message-user`, `pageNav`
- Always use sessions (requests.Session) for cookie persistence
- Thread pagination: Detect via pageNav-page--last or page jump input
- URL formats: `/threads/name.ID/` or `/threads/name.ID/page-N`
- Social links are stored at thread level (not duplicated per post)

## Anti-Patterns to Avoid
- ❌ Don't store HTML in content field (use plain text)
- ❌ Don't add post_number field (removed for simplicity)
- ❌ Don't duplicate social links (deduplicate by URL)
- ❌ Don't hardcode domain-specific logic (make it generic)
- ❌ Don't scrape without rate limiting (respect servers)
- ❌ Don't store cookies in code (use cookies.json)

## When Suggesting Code:
- Follow existing code style (4 spaces, type hints, docstrings)
- Use dataclasses for new models
- Add error handling with try-except
- Log progress for user visibility
- Test with multiple XenForo forums
- Maintain backward compatibility with existing JSON files
