"""
XenForo Forum Scraper
Scrapes threads, posts, and user data from XenForo-based forums
"""
import re
import time
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from models import Thread, Post, User, Attachment, MediaEmbed, Link
import os


class XenforoScraper:
    """
    A scraper for XenForo-based forums
    """
    
    def __init__(self, base_url: str, delay: float = 1.0, headers: Optional[Dict] = None, patterns: Optional[Dict] = None):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL of the forum (e.g., 'https://celebforum.to')
            delay: Delay between requests in seconds (default: 1.0)
            headers: Optional custom headers for requests
            patterns: Optional site-specific patterns (CSS selectors, classes, etc.)
        """
        self.base_url = base_url.rstrip('/')
        self.delay = delay
        self.session = requests.Session()
        self.patterns = patterns or self._get_default_patterns()
        self.selenium_driver = None  # Reuse same browser instance
        
        # More realistic browser headers to avoid 403 errors
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        if headers:
            self.headers.update(headers)
        
        self.session.headers.update(self.headers)
    
    def _get_default_patterns(self) -> Dict:
        """Return default XenForo patterns"""
        return {
            'version': '1.0',
            'selectors': {
                'post_container': ['.message', 'article.message'],
                'author': ['.username'],
                'date': ['time[datetime]', '.u-dt'],
                'reactions': ['.reactionsBar'],
                'attachments': ['.attachment'],
                'pagination': ['.pageNav']
            },
            'classes': {
                'content_wrapper': ['bbWrapper']
            },
            'attributes': {
                'post_id': 'data-content'
            }
        }
    
    def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a page
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            time.sleep(self.delay)  # Rate limiting
            
            # Add referrer header for better acceptance
            extra_headers = {}
            if hasattr(self, '_last_url') and self._last_url:
                extra_headers['Referer'] = self._last_url
            
            response = self.session.get(url, timeout=30, headers=extra_headers, allow_redirects=True)
            self._last_url = url
            
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # Check if we have cf_clearance cookie (Cloudflare protection)
                has_cf_clearance = any('cf_clearance' in str(cookie) for cookie in self.session.cookies)
                
                if has_cf_clearance:
                    print(f"⚠ 403 Forbidden with Cloudflare protection detected")
                    print(f"🔄 Switching to Selenium to bypass Cloudflare...")
                    return self._get_page_with_selenium(url)
                else:
                    print(f"Error fetching {url}: 403 Forbidden")
                    print("Tip: The forum may be blocking automated requests. Try:")
                    print("  1. Adding cookies from a browser session")
                    print("  2. Using a proxy or VPN")
                    print("  3. Checking if the forum requires login")
            else:
                print(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _get_page_with_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch page using Selenium when Cloudflare blocks requests
        Reuses same browser instance for efficiency
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service as ChromeService
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            # Initialize Chrome driver on first use
            if self.selenium_driver is None:
                print("  🌐 Starting Chrome browser (will reuse for all pages)...")
                
                # Setup Chrome options
                chrome_options = Options()
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
                
                # Use Chrome profile from project folder (has logged-in sessions)
                chrome_profile_dir = os.path.join(os.path.dirname(__file__), 'XenForo')
                if os.path.exists(chrome_profile_dir):
                    chrome_options.add_argument(f'--user-data-dir={chrome_profile_dir}')
                    print("  ✓ Using saved Chrome profile with cookies...")
                else:
                    print("  ⚠ Chrome profile not found - Cloudflare may block")
                
                # Initialize driver
                service = ChromeService(ChromeDriverManager().install())
                self.selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Remove webdriver flag to avoid detection
                self.selenium_driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })
            
            driver = self.selenium_driver
            
            # Navigate to page
            print(f"  📄 Loading: {url}")
            driver.get(url)
            
            # Wait for Cloudflare challenge to complete (if present)
            print("  ⏳ Waiting for page...")
            time.sleep(3)  # Initial wait
            
            # Check if we're still on Cloudflare page
            if 'Just a moment' in driver.page_source or 'Checking your browser' in driver.page_source:
                print("  🔄 Cloudflare challenge detected, waiting...")
                time.sleep(8)  # Wait longer for challenge to complete
            
            # Wait for page to load (wait for article.message or post content)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article.message, .message, .post"))
                )
                print("  ✓ Page loaded")
            except:
                print("  ⚠ Timeout waiting for posts, checking content...")
            
            # Get page source and parse
            page_source = driver.page_source
            
            # Check if we got actual content
            if len(page_source) < 1000 or 'Just a moment' in page_source:
                print("  ✗ Cloudflare still blocking")
                print("\n  💡 To fix this:")
                print("     1. Run: python get_cookies.py")
                print("     2. Choose option 1")
                print(f"     3. Enter: {self.base_url}")
                print("     4. Login and wait for Cloudflare challenge to complete")
                print("     5. Press ENTER to save fresh cookies\n")
                return None
            
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            print(f"  ✗ Selenium error: {e}")
            return None
    
    def close_selenium_driver(self):
        """Close the Selenium driver when done"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                self.selenium_driver = None
            except:
                pass
    
    def _extract_user_from_element(self, user_element) -> Optional[User]:
        """Extract user information from a user element"""
        try:
            username_elem = user_element.find('a', class_='username')
            if not username_elem:
                return None
            
            username = username_elem.get_text(strip=True)
            profile_url = username_elem.get('href', '')
            if profile_url:
                profile_url = urljoin(self.base_url, profile_url)
            
            # Extract user ID from URL
            user_id = None
            if profile_url:
                match = re.search(r'/members/[^/]+\.(\d+)/', profile_url)
                if match:
                    user_id = match.group(1)
            
            # Extract user title (try multiple selectors)
            user_title = None
            # Method 1: h5.userTitle or h5.message-userTitle
            user_title_elem = user_element.find('h5', class_=lambda x: x and 'userTitle' in x)
            if user_title_elem:
                user_title = user_title_elem.get_text(strip=True)
            else:
                # Method 2: span.userTitle (older XenForo versions)
                user_title_elem = user_element.find('span', class_='userTitle')
                if user_title_elem:
                    user_title = user_title_elem.get_text(strip=True)
            
            # Extract stats
            messages = None
            reaction_score = None
            points = None
            
            stats = user_element.find_all('dd')
            for stat in stats:
                text = stat.get_text(strip=True)
                if text.isdigit() or text.replace(',', '').isdigit():
                    value = int(text.replace(',', ''))
                    if messages is None:
                        messages = value
                    elif reaction_score is None:
                        reaction_score = value
                    elif points is None:
                        points = value
            
            return User(
                username=username,
                user_id=user_id,
                profile_url=profile_url,
                user_title=user_title,
                messages=messages,
                reaction_score=reaction_score,
                points=points
            )
        except Exception as e:
            print(f"Error extracting user: {e}")
            return None
    
    def _extract_media_embeds(self, post_content) -> List[MediaEmbed]:
        """Extract embedded media (iframes, videos) from post content"""
        media_embeds = []
        
        try:
            # Find all iframes
            iframes = post_content.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if not src:
                    continue
                
                # Determine media type and extract ID
                media_type = 'iframe'
                media_id = None
                
                if 'saint2.cr' in src or 'saint.to' in src:
                    media_type = 'saint_video'
                    match = re.search(r'/embed/([^/\?]+)', src)
                    media_id = match.group(1) if match else None
                elif 'youtube.com' in src or 'youtu.be' in src:
                    media_type = 'youtube'
                    match = re.search(r'(?:embed/|v=)([^&\?]+)', src)
                    media_id = match.group(1) if match else None
                elif 'redgifs.com' in src:
                    media_type = 'redgifs'
                    match = re.search(r'/watch/([^/\?]+)', src)
                    media_id = match.group(1) if match else None
                elif 'imgur.com' in src:
                    media_type = 'imgur'
                
                media_embeds.append(MediaEmbed(
                    media_type=media_type,
                    embed_url=src,
                    media_id=media_id
                ))
            
            # Find div placeholders for lazy-loaded media
            media_divs = post_content.find_all('div', class_=['generic2wide-iframe-div', 'iframe-wrapper-redgifs'])
            for div in media_divs:
                # Sometimes the iframe isn't loaded yet, but onclick attribute has the URL
                parent = div.find_parent()
                if parent and parent.get('onclick'):
                    onclick_code = parent.get('onclick', '')
                    # Extract URL from loadMedia function call
                    match = re.search(r'loadMedia\([^,]+,\s*["\']([^"\']+)["\']', onclick_code)
                    if match:
                        embed_url = match.group(1)
                        media_type = 'redgifs' if 'redgifs' in embed_url else 'video'
                        media_embeds.append(MediaEmbed(
                            media_type=media_type,
                            embed_url=embed_url,
                            media_id=None
                        ))
        
        except Exception as e:
            print(f"Error extracting media embeds: {e}")
        
        return media_embeds
    
    def _extract_links(self, post_content) -> List[Link]:
        """Extract all links from post content"""
        links = []
        
        try:
            # Find all links
            all_links = post_content.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                if not href or href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                # Get link text
                text = link.get_text(strip=True)
                
                # Determine link type
                link_type = 'external'
                
                # Check if it's an image link
                img_tag = link.find('img')
                if img_tag:
                    link_type = 'image_link'
                    # Use alt text or image filename as text
                    if not text:
                        text = img_tag.get('alt', '') or img_tag.get('title', '') or href
                
                # Check if internal link
                if href.startswith('/') or self.base_url in href:
                    link_type = 'internal'
                
                # Make URL absolute
                full_url = urljoin(self.base_url, href)
                
                links.append(Link(
                    url=full_url,
                    text=text or href,
                    link_type=link_type
                ))
        
        except Exception as e:
            print(f"Error extracting links: {e}")
        
        return links
    
    def _extract_attachments(self, post_content) -> List[Attachment]:
        """Extract attachments from post content"""
        attachments = []
        
        try:
            # Find all attachment links
            attach_links = post_content.find_all('a', class_='file-preview')
            if not attach_links:
                # Alternative: find all attachment images
                attach_links = post_content.find_all('a', href=re.compile(r'/attachments/'))
            
            for link in attach_links:
                href = link.get('href', '')
                if not href:
                    continue
                
                full_url = urljoin(self.base_url, href)
                
                # Extract attachment ID from URL
                match = re.search(r'/attachments/[^/]+\.(\d+)/', href)
                attachment_id = match.group(1) if match else ''
                
                # Determine filename
                filename = link.get_text(strip=True)
                if not filename:
                    filename_match = re.search(r'/attachments/([^/]+)/', href)
                    filename = filename_match.group(1) if filename_match else f"attachment_{attachment_id}"
                
                # Determine file type
                file_type = 'unknown'
                if any(ext in filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    file_type = 'image'
                elif any(ext in filename.lower() for ext in ['.mp4', '.webm', '.mov', '.avi']):
                    file_type = 'video'
                elif any(ext in filename.lower() for ext in ['.pdf', '.doc', '.docx', '.txt']):
                    file_type = 'document'
                
                attachments.append(Attachment(
                    attachment_id=attachment_id,
                    filename=filename,
                    url=full_url,
                    file_type=file_type
                ))
            
            # Also check for embedded images
            images = post_content.find_all('img', class_='bbImage')
            for img in images:
                src = img.get('src', '') or img.get('data-url', '')
                if not src:
                    continue
                
                # Skip data URIs and placeholder images
                if src.startswith('data:') or 'data:image/gif;base64' in src:
                    continue
                
                full_url = urljoin(self.base_url, src)
                
                # Try to extract ID from URL or src
                attachment_id = ''
                if '/attachments/' in src:
                    match = re.search(r'/attachments/[^/]+\.(\d+)/', src)
                    attachment_id = match.group(1) if match else ''
                else:
                    # Use filename from URL as ID
                    match = re.search(r'/([^/]+)\.(jpg|jpeg|png|gif|webp)', src, re.IGNORECASE)
                    attachment_id = match.group(1) if match else ''
                
                # Get filename from alt or src
                filename = img.get('alt', '') or img.get('title', '')
                if not filename:
                    # Extract filename from URL
                    filename_match = re.search(r'/([^/]+\.(jpg|jpeg|png|gif|webp))' , src, re.IGNORECASE)
                    filename = filename_match.group(1) if filename_match else f"image_{attachment_id}.jpg"
                
                # Check if already added
                if not any(a.url == full_url for a in attachments):
                    attachments.append(Attachment(
                        attachment_id=attachment_id,
                        filename=filename,
                        url=full_url,
                        file_type='image'
                    ))
        
        except Exception as e:
            print(f"Error extracting attachments: {e}")
        
        return attachments
    
    def _extract_posts_from_page(self, soup: BeautifulSoup) -> List[Post]:
        """Extract all posts from a page"""
        posts = []
        
        try:
            # Find all post articles using patterns
            post_elements = []
            for selector in self.patterns['selectors'].get('post_container', ['.message']):
                elements = soup.select(selector)
                if elements:
                    post_elements = elements
                    break
            
            if not post_elements:
                # Fallback to default
                post_elements = soup.find_all('article', class_='message')
            
            for post_elem in post_elements:
                try:
                    # Extract post ID using pattern
                    post_id_attr = self.patterns['attributes'].get('post_id', 'data-content')
                    post_id = post_elem.get(post_id_attr, '')
                    if not post_id:
                        post_id = post_elem.get('id', '').replace('post-', '')
                    
                    # Extract author
                    user_section = post_elem.find('section', class_='message-user')
                    author = None
                    if user_section:
                        author = self._extract_user_from_element(user_section)
                    
                    if not author:
                        author = User(username="Unknown")
                    
                    # Extract post content (text only) using patterns
                    content_elem = None
                    for content_class in self.patterns['classes'].get('content_wrapper', ['bbWrapper']):
                        content_elem = post_elem.find('div', class_=content_class)
                        if content_elem:
                            break
                    
                    content = content_elem.get_text(strip=True, separator=' ') if content_elem else ""
                    
                    # Extract all media and links
                    attachments = self._extract_attachments(content_elem) if content_elem else []
                    media_embeds = self._extract_media_embeds(content_elem) if content_elem else []
                    links = self._extract_links(content_elem) if content_elem else []
                    
                    # Deduplicate: remove image_link entries that match attachment filenames
                    attachment_filenames = {att.filename for att in attachments}
                    links = [link for link in links if not (
                        link.link_type == 'image_link' and 
                        any(att_name in link.text for att_name in attachment_filenames)
                    )]
                    
                    # Extract date using patterns
                    date_elem = None
                    for date_selector in self.patterns['selectors'].get('date', ['time[datetime]']):
                        date_elem = post_elem.select_one(date_selector)
                        if date_elem:
                            break
                    
                    date = date_elem.get('datetime', '') if date_elem else ""
                    if not date:
                        date = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Extract reactions count using patterns
                    reactions = 0
                    reactions_elem = None
                    for reaction_selector in self.patterns['selectors'].get('reactions', ['.reactionsBar']):
                        reactions_elem = post_elem.select_one(reaction_selector)
                        if reactions_elem:
                            break
                    
                    if not reactions_elem:
                        reactions_elem = post_elem.find('a', href=re.compile(r'/posts/\d+/reactions'))
                    
                    if reactions_elem:
                        reactions_text = reactions_elem.get_text(strip=True)
                        
                        # Check for "and X others" pattern (e.g., "User1, User2 and 11 others")
                        others_match = re.search(r'and\s+(\d+)\s+others?', reactions_text)
                        if others_match:
                            # Count visible usernames (in <bdi> tags) + "others" count
                            bdi_tags = reactions_elem.find_all('bdi')
                            visible_users = len(bdi_tags)
                            others_count = int(others_match.group(1))
                            reactions = visible_users + others_count
                        else:
                            # Count individual usernames in <bdi> tags
                            bdi_tags = reactions_elem.find_all('bdi')
                            if bdi_tags:
                                reactions = len(bdi_tags)
                            else:
                                # Fallback: try to extract first number found
                                match = re.search(r'(\d+)', reactions_text)
                                if match:
                                    reactions = int(match.group(1))
                    
                    # Create post object
                    post = Post(
                        post_id=post_id,
                        author=author,
                        content=content,
                        date=date,
                        reactions=reactions,
                        attachments=attachments,
                        media_embeds=media_embeds,
                        links=links
                    )
                    
                    posts.append(post)
                
                except Exception as e:
                    print(f"Error extracting post: {e}")
                    continue
        
        except Exception as e:
            print(f"Error extracting posts from page: {e}")
        
        return posts
    
    def _extract_thread_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract thread metadata (title, tags, etc.)"""
        metadata = {
            'title': '',
            'thread_id': '',
            'tags': [],
            'prefixes': [],
            'start_date': '',
            'total_pages': 1
        }
        
        try:
            # Extract title
            title_elem = soup.find('h1', class_='p-title-value')
            if title_elem:
                metadata['title'] = title_elem.get_text(strip=True)
            
            # Extract thread ID from URL
            match = re.search(r'/threads/[^/]+\.(\d+)/', url)
            if match:
                metadata['thread_id'] = match.group(1)
            
            # Extract tags
            tag_elements = soup.find_all('a', class_='tagItem')
            metadata['tags'] = [tag.get_text(strip=True) for tag in tag_elements]
            
            # Extract prefixes (labels)
            prefix_elements = soup.find_all('a', class_='labelLink')
            metadata['prefixes'] = [prefix.get_text(strip=True) for prefix in prefix_elements]
            
            # Extract start date
            date_elem = soup.find('time', class_='u-dt')
            if date_elem:
                metadata['start_date'] = date_elem.get('datetime', '') or date_elem.get_text(strip=True)
            
            # Extract total pages - try multiple methods
            pageNav = soup.find('nav', class_='pageNav')
            if pageNav:
                # Method 1: Look for last page link
                last_page_elem = pageNav.find('a', class_='pageNav-page--last')
                if last_page_elem:
                    last_page_text = last_page_elem.get_text(strip=True)
                    if last_page_text.isdigit():
                        metadata['total_pages'] = int(last_page_text)
                
                # Method 2: Look for all page links and get the highest number
                if metadata['total_pages'] == 1:
                    page_links = pageNav.find_all('a', class_='pageNav-page')
                    page_numbers = []
                    for link in page_links:
                        page_text = link.get_text(strip=True)
                        if page_text.isdigit():
                            page_numbers.append(int(page_text))
                    if page_numbers:
                        metadata['total_pages'] = max(page_numbers)
                
                # Method 3: Check current page indicator like "4 of 4"
                if metadata['total_pages'] == 1:
                    page_indicator = pageNav.find('a', class_='pageNavSimple-el--current')
                    if page_indicator:
                        indicator_text = page_indicator.get_text(strip=True)
                        # Look for pattern like "X of Y"
                        match = re.search(r'(\d+)\s+of\s+(\d+)', indicator_text)
                        if match:
                            metadata['total_pages'] = int(match.group(2))
            
            # Alternative: Check for page jump input with max value
            if metadata['total_pages'] == 1:
                page_jump = soup.find('input', class_='js-pageJumpPage')
                if page_jump:
                    max_val = page_jump.get('max', '')
                    if max_val.isdigit():
                        metadata['total_pages'] = int(max_val)
        
        except Exception as e:
            print(f"Error extracting thread metadata: {e}")
        
        return metadata
    
    def _extract_social_links_from_posts(self, posts: List[Post]) -> List[Link]:
        """
        Extract all social media links from all posts
        
        Args:
            posts: List of Post objects
            
        Returns:
            List of unique social media Link objects
        """
        social_domains = {
            'tiktok.com': 'tiktok',
            'twitter.com': 'twitter',
            'x.com': 'x',
            'instagram.com': 'instagram',
            'facebook.com': 'facebook',
            'onlyfans.com': 'onlyfans',
            'fansly.com': 'fansly',
            'patreon.com': 'patreon',
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'snapchat.com': 'snapchat',
            'reddit.com': 'reddit',
            'twitch.tv': 'twitch',
            'discord.gg': 'discord',
            'discord.com': 'discord',
            'telegram.org': 'telegram',
            't.me': 'telegram',
            'linkedin.com': 'linkedin',
            'pinterest.com': 'pinterest',
            'tumblr.com': 'tumblr',
            'vimeo.com': 'vimeo',
            'threads.net': 'threads',
            'bluesky.social': 'bluesky'
        }
        
        social_links = []
        seen_urls = set()
        
        for post in posts:
            for link in post.links:
                # Check if link is from a social media platform
                url_lower = link.url.lower()
                platform = None
                
                for domain, platform_name in social_domains.items():
                    if domain in url_lower:
                        platform = platform_name
                        break
                
                # If it's a social media link and not already added
                if platform and link.url not in seen_urls:
                    social_links.append(Link(
                        url=link.url,
                        text=link.text,
                        link_type=platform
                    ))
                    seen_urls.add(link.url)
        
        return social_links
    
    def scrape_thread(self, thread_url: str, max_pages: Optional[int] = None) -> Thread:
        """
        Scrape a complete thread
        
        Args:
            thread_url: URL of the thread
            max_pages: Maximum number of pages to scrape (None = all pages)
            
        Returns:
            Thread object with all posts
        """
        print(f"Scraping thread: {thread_url}")
        
        # Get first page
        soup = self._get_page(thread_url)
        if not soup:
            return None
        
        # Extract metadata
        metadata = self._extract_thread_metadata(soup, thread_url)
        
        # Create thread object
        thread = Thread(
            thread_id=metadata['thread_id'],
            title=metadata['title'],
            url=thread_url,
            start_date=metadata['start_date'],
            tags=metadata['tags'],
            prefixes=metadata['prefixes'],
            total_pages=metadata['total_pages']
        )
        
        # Determine how many pages to scrape
        pages_to_scrape = metadata['total_pages']
        if max_pages:
            pages_to_scrape = min(max_pages, pages_to_scrape)
        
        print(f"Thread: {thread.title}")
        print(f"Thread ID: {thread.thread_id}")
        print(f"Total pages detected: {thread.total_pages}, Scraping: {pages_to_scrape}")
        
        if thread.total_pages == 1 and pages_to_scrape == 1:
            print("⚠ Warning: Only 1 page detected. If thread has more pages, pagination detection may have failed.")
        
        # Scrape first page posts
        thread.posts = self._extract_posts_from_page(soup)
        thread.current_page = 1
        
        print(f"Page 1: Found {len(thread.posts)} posts")
        
        # Scrape remaining pages
        for page_num in range(2, pages_to_scrape + 1):
            # Try different pagination URL formats
            if 'page-' in thread_url:
                # URL already has page parameter, replace it
                page_url = re.sub(r'page-\d+', f'page-{page_num}', thread_url)
            else:
                # Append page parameter
                if thread_url.endswith('/'):
                    page_url = f"{thread_url}page-{page_num}"
                else:
                    page_url = f"{thread_url}/page-{page_num}"
            
            soup = self._get_page(page_url)
            if not soup:
                print(f"Failed to fetch page {page_num}")
                continue
            
            posts = self._extract_posts_from_page(soup)
            if not posts:
                print(f"Page {page_num}: No posts found (URL might be wrong: {page_url})")
                continue
            
            thread.posts.extend(posts)
            thread.current_page = page_num
            
            print(f"Page {page_num}: Found {len(posts)} posts (Total: {len(thread.posts)})")
        
        # Extract all social media links from posts
        thread.social_links = self._extract_social_links_from_posts(thread.posts)
        
        # Close Selenium driver if it was used
        self.close_selenium_driver()
        
        return thread
    
    def scrape_forum_threads(self, forum_url: str, max_threads: Optional[int] = None) -> List[str]:
        """
        Get list of thread URLs from a forum page
        
        Args:
            forum_url: URL of the forum
            max_threads: Maximum number of thread URLs to return
            
        Returns:
            List of thread URLs
        """
        print(f"Scraping forum: {forum_url}")
        
        soup = self._get_page(forum_url)
        if not soup:
            return []
        
        thread_urls = []
        
        try:
            # Find all thread links
            thread_elements = soup.find_all('div', class_='structItem-title')
            
            for elem in thread_elements:
                link = elem.find('a', href=re.compile(r'/threads/'))
                if link:
                    href = link.get('href', '')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        thread_urls.append(full_url)
                        
                        if max_threads and len(thread_urls) >= max_threads:
                            break
        
        except Exception as e:
            print(f"Error extracting thread URLs: {e}")
        
        print(f"Found {len(thread_urls)} threads")
        return thread_urls
    
    def export_thread_to_dict(self, thread: Thread) -> Dict:
        """
        Export thread to dictionary format
        
        Args:
            thread: Thread object
            
        Returns:
            Dictionary representation
        """
        return {
            'thread_id': thread.thread_id,
            'title': thread.title,
            'url': thread.url,
            'start_date': thread.start_date,
            'tags': thread.tags,
            'prefixes': thread.prefixes,
            'social_links': [
                {
                    'url': link.url,
                    'text': link.text,
                    'platform': link.link_type
                } for link in thread.social_links
            ],
            'total_pages': thread.total_pages,
            'total_posts': len(thread.posts),
            'posts': [
                {
                    'post_id': post.post_id,
                    'author': {
                        'username': post.author.username,
                        'user_id': post.author.user_id,
                        'profile_url': post.author.profile_url,
                        'user_title': post.author.user_title,
                        'messages': post.author.messages,
                        'reaction_score': post.author.reaction_score,
                        'points': post.author.points
                    },
                    'content': post.content,
                    'date': post.date,
                    'reactions': post.reactions,
                    'attachments': [
                        {
                            'attachment_id': att.attachment_id,
                            'filename': att.filename,
                            'url': att.url,
                            'file_type': att.file_type
                        } for att in post.attachments
                    ],
                    'media_embeds': [
                        {
                            'media_type': media.media_type,
                            'embed_url': media.embed_url,
                            'media_id': media.media_id
                        } for media in post.media_embeds
                    ],
                    'links': [
                        {
                            'url': link.url,
                            'text': link.text,
                            'link_type': link.link_type
                        } for link in post.links
                    ]
                } for post in thread.posts
            ]
        }
