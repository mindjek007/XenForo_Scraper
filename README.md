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

### Using Multiple Domains

The scraper automatically handles multiple XenForo forums:

1. **Add cookies for each domain:**
   ```bash
   python get_cookies.py
   ```
   Choose option 1 and add cookies for each forum

2. **View all stored domains:**
   ```bash
   python get_cookies.py
   ```
   Choose option 3

3. **Test all cookies:**
   ```bash
   python get_cookies.py
   ```
   Choose option 4

4. **Use quick_start.py:**
   It will automatically detect the domain from any thread URL and load the correct cookies!

### Custom Headers

```python
scraper = XenforoScraper(
    base_url='https://forum.com',
    delay=2.0,
    headers={
        'User-Agent': 'Custom User Agent',
        'Cookie': 'your_session_cookie'  # If authentication needed
    }
)
```

### Scraping All Pages by Default

```python
# Scrape ALL pages (default behavior)
thread = scraper.scrape_thread(thread_url)

# Or limit to specific number
thread = scraper.scrape_thread(thread_url, max_pages=5)
```

### Rate Limiting

Adjust the `delay` parameter to control request frequency:

```python
scraper = XenforoScraper(
    base_url='https://forum.com',
    delay=2.5  # 2.5 seconds between requests
)
```

## Limitations & Best Practices

1. **Rate Limiting**: Always use appropriate delays to avoid overloading servers
2. **Authentication**: Some forums require login to view content. You may need to add session cookies
3. **Robots.txt**: Check the forum's robots.txt file and respect crawling rules
4. **Terms of Service**: Ensure your use complies with the forum's terms of service
5. **Private Content**: This scraper only works with publicly accessible content

## Supported Forums

This scraper works with any forum using XenForo CMS, including:
- Community forums
- Gaming forums
- Tech forums
- Fan forums
- And many more!

Simply change the `base_url` parameter to the target forum.

## Troubleshooting

### Issue: 403 Forbidden Error

**This is the most common issue!** The forum is blocking automated requests.

**Solution - Automated Cookie Extraction (Easiest):**

1. Run the cookie manager:
   ```bash
   python get_cookies.py
   ```

2. Choose option 1 (automated):
   - Enter the forum URL
   - Chrome will open automatically
   - Login to the forum
   - Press Enter in terminal when done
   - Cookies are automatically saved!

3. Test your cookies:
   ```bash
   python get_cookies.py
   ```
   Choose option 4 to test all stored cookies

4. Use quick_start.py:
   ```bash
   python quick_start.py
   ```
   It will automatically load the correct cookies for any domain!

**Multiple Domains:**
The cookie manager supports multiple XenForo forums in a single cookies.json file. Just repeat step 2 for each forum you want to scrape.

### Issue: No posts found

**Solution**: The forum might have a different HTML structure. Check the page source and adjust the CSS selectors in `scraper.py`.

### Issue: Authentication required

**Solution**: Some forums require login. Add session cookies to the headers (see 403 error solution above).

### Issue: Rate limited by server

**Solution**: Increase the delay between requests:

```python
scraper = XenforoScraper(base_url='https://forum.com', delay=5.0)
```

## Advanced Usage

### Custom Post Processing

```python
def process_post(post):
    """Custom processing for each post"""
    # Extract specific data
    if len(post.attachments) > 0:
        print(f"Post has {len(post.attachments)} attachments")
    
    # Filter content
    if 'keyword' in post.content.lower():
        print(f"Found keyword in post by {post.author.username}")

# Apply to all posts
for post in thread.posts:
    process_post(post)
```

### Download Attachments

```python
import requests
import os

def download_attachments(thread, output_dir='downloads'):
    """Download all attachments from a thread"""
    os.makedirs(output_dir, exist_ok=True)
    
    for post in thread.posts:
        for att in post.attachments:
            if att.file_type == 'image':
                filename = f"{output_dir}/{att.filename}"
                response = requests.get(att.url)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {filename}")
```

### Filter Posts by Date

```python
from datetime import datetime

def filter_posts_by_date(thread, start_date):
    """Filter posts after a specific date"""
    filtered_posts = []
    for post in thread.posts:
        try:
            post_date = datetime.fromisoformat(post.date.replace('Z', '+00:00'))
            if post_date >= start_date:
                filtered_posts.append(post)
        except:
            pass
    return filtered_posts

# Usage
start = datetime(2025, 7, 1)
recent_posts = filter_posts_by_date(thread, start)
```

## API Reference

### XenforoScraper Class

#### `__init__(base_url, delay=1.0, headers=None)`
Initialize the scraper with forum URL and settings.

#### `scrape_thread(thread_url, max_pages=None)`
Scrape a complete thread. Returns a `Thread` object.

#### `scrape_forum_threads(forum_url, max_threads=None)`
Get list of thread URLs from a forum page. Returns list of URLs.

#### `export_thread_to_dict(thread)`
Convert a Thread object to a dictionary for JSON export.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Legal Notice

This tool is for educational purposes. Always:
- Respect the forum's Terms of Service
- Follow robots.txt guidelines
- Use appropriate rate limiting
- Only scrape publicly available content
- Respect copyright and intellectual property

## License

MIT License - feel free to use and modify as needed.

## Support

For issues, questions, or suggestions, please open an issue on the repository.
