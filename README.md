# XenForo Forum Scraper

A Python scraper for extracting data from XenForo-based forums. This scraper works with **any forum** that uses the XenForo CMS platform, with full support for multiple domains.

## Features

- ✅ Scrape complete threads with **all pages by default**
- ✅ **Multi-domain cookie management** - manage cookies for multiple XenForo sites in one file
- ✅ **Auto-pattern detection** - analyzes each site's HTML structure for optimal scraping
- ✅ Extract user information (username, stats, profile links)
- ✅ Download attachment URLs (images, videos, documents)
- ✅ Separate content types (text, HTML, images, videos/embeds, links)
- ✅ Multi-page thread support with automatic pagination detection
- ✅ Forum thread list extraction
- ✅ Export to JSON format
- ✅ Rate limiting to respect server resources
- ✅ Automated cookie extraction with Chrome
- ✅ Built-in cookie testing for all domains
- ✅ Automatic Selenium fallback for Cloudflare protection

## Tested & Working Domains

- ✅ simpcity.cr
- ✅ nudostar.com
- ✅ celebforum.to
- ✅ leakedmodels.com

**Note:** Works with Cloudflare normal protection. Does NOT work when site enables Cloudflare "Under Attack Mode" (requires manual CAPTCHA solving).

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Easiest Way - Using quick_start.py

1. **Extract cookies for your forum(s):**
   ```bash
   python get_cookies.py
   ```
   - Choose option 1 (automated with Chrome)
   - Enter forum URL
   - Login in the Chrome window
   - Press Enter when done
   - **Provide a sample thread URL** to auto-detect site patterns (optional but recommended)
   - Repeat for multiple forums if needed

2. **Start scraping:**
   ```bash
   python quick_start.py
   ```
   - Enter any thread URL from any XenForo forum you have cookies for
   - Press Enter to scrape **ALL pages** (or specify a number)
   - Data is automatically exported to JSON

3. **Download media from JSON:**
   ```bash
   # Install downloader tools first
   pip install cyberdrop-dl yt-dlp gallery-dl aria2

   # Then download all media
   python download_media.py downloads/344155/thread_344155.json
   ```
   - Auto-detects domains and uses appropriate tool
   - Supports: cyberdrop, yt-dlp, gallery-dl, aria2c

### Basic Usage (Python Code)

```python
from scraper import XenforoScraper
import json

# Load cookies for your domain
with open('cookies.json', 'r') as f:
    data = json.load(f)

domain = 'celebforum.to'
cookie_string = data['domains'][domain]['string']

# Initialize scraper
scraper = XenforoScraper(
    base_url=f'https://{domain}',
    delay=1.5,
    headers={'Cookie': cookie_string}
)

# Scrape entire thread (all pages by default)
thread_url = 'https://celebforum.to/threads/blows.204932/'
thread = scraper.scrape_thread(thread_url)  # Scrapes all pages

# Or limit pages
thread = scraper.scrape_thread(thread_url, max_pages=5)

# Access thread data
print(f"Title: {thread.title}")
print(f"Total Posts: {len(thread.posts)}")
print(f"Tags: {thread.tags}")

# Access post data
for post in thread.posts:
    print(f"Author: {post.author.username}")
    print(f"Content: {post.content}")
    print(f"Images: {len(post.attachments)}")
    print(f"Videos/Embeds: {len(post.media_embeds)}")
    print(f"Links: {len(post.links)}")
```

### Export to JSON

```python
import json

# Export thread data to JSON
thread_dict = scraper.export_thread_to_dict(thread)

with open('thread_data.json', 'w', encoding='utf-8') as f:
    json.dump(thread_dict, f, indent=2, ensure_ascii=False)
```

### Scrape Multiple Threads

```python
# Get list of threads from a forum
forum_url = 'https://celebforum.to/forums/fan-sites.34/'
thread_urls = scraper.scrape_forum_threads(forum_url, max_threads=10)

# Scrape each thread
all_threads = []
for url in thread_urls:
    thread = scraper.scrape_thread(url, max_pages=1)
    if thread:
        all_threads.append(thread)
```

## Data Structure

### Thread Object

```python
Thread(
    thread_id='204932',
    title='Thread Title',
    url='https://forum.com/threads/example.204932/',
    start_date='2025-03-05',
    tags=['tag1', 'tag2'],
    prefixes=['USA', 'THICC'],
    social_links=[...],  # All social media links from posts
    posts=[...],
    total_pages=10,
    current_page=5
)
```

### Post Object

```python
Post(
    post_id='1213126',
    author=User(...),
    content='Post content text (plain text only)...',
    date='2025-03-05',
    reactions=54,
    attachments=[...],
    media_embeds=[...],
    links=[...]
)
```

### User Object

```python
User(
    username='JohnDoe',
    user_id='123456',
    profile_url='https://forum.com/members/johndoe.123456/',
    user_title='Senior Member',
    messages=1000,
    reaction_score=5000,
    points=250
)
```

### Attachment Object

```python
Attachment(
    attachment_id='7033662',
    filename='image.jpg',
    url='https://forum.com/attachments/image.7033662/',
    file_type='image'  # 'image', 'video', 'document', or 'unknown'
)
```

### MediaEmbed Object

```python
MediaEmbed(
    embed_url='https://youtube.com/embed/xyz',
    media_type='youtube',  # 'youtube', 'saint_video', 'redgifs', 'iframe'
    iframe_html='<iframe src="..."></iframe>'
)
```

### Link Object

```python
Link(
    url='https://example.com',
    text='Link text',
    link_type='external'  # 'external', 'internal', 'image_link'
)
```

## Usage

### Quick Start
```bash
python quick_start.py
```
- Paste any thread URL
- Press Enter to scrape ALL pages
- JSON saved to `downloads/{thread_id}/thread_{thread_id}.json`

### Cookie Management
```bash
python get_cookies.py
```
- Add cookies for multiple domains
- Test cookie validity
- View stored domains

### View Results
```bash
python view_json.py
```
- View scraped thread data
- See statistics and summaries

## Configuration

### Multiple Forums

```bash
python get_cookies.py
```
- **Option 1**: Add domain (Chrome login)
- **Option 3**: View stored domains
- **Option 4**: Test all cookies

### Rate Limiting & Pages

```python
scraper = XenforoScraper(base_url='https://forum.com', delay=2.5)

# Scrape all pages (default)
thread = scraper.scrape_thread(url)

# Limit pages
thread = scraper.scrape_thread(url, max_pages=5)
```

## Legal Notice

This tool is for educational purposes. Always:
- Respect the forum's Terms of Service
- Use appropriate rate limiting
- Only scrape publicly available content

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, questions, or suggestions, please open an issue on the repository.
