"""
Quick start scraper with multi-domain cookie support
Automatically loads cookies and scrapes all pages by default
"""
import json
import os
from urllib.parse import urlparse
from scraper import XenforoScraper


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc


def load_cookies_for_domain(domain: str, filename: str = 'cookies.json'):
    """Load cookies and patterns for a specific domain"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle old format (single domain)
        if 'domains' not in data:
            if 'string' in data:
                return {
                    'cookie_string': data.get('string', ''),
                    'patterns': data.get('patterns')
                }
            return None
        
        # New format (multiple domains)
        domain_data = data.get('domains', {}).get(domain)
        if domain_data:
            return {
                'cookie_string': domain_data.get('string', ''),
                'patterns': domain_data.get('patterns')
            }
        
        return None
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None


def main():
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "XenForo Scraper - Multi-Domain Support" + " "*16 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Check if cookies file exists
    if not os.path.exists('cookies.json'):
        print("❌ No cookies.json found!")
        print("\nPlease run: python get_cookies.py")
        print("Then choose option 1 to extract cookies automatically.")
        return
    
    # Load all available domains
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f:
            cookies_file = json.load(f)
        
        # Handle old format
        if 'domains' not in cookies_file:
            if 'string' in cookies_file:
                available_domains = [cookies_file.get('domain', 'unknown')]
            else:
                print("❌ Invalid cookies.json format!")
                return
        else:
            available_domains = list(cookies_file.get('domains', {}).keys())
        
        if not available_domains:
            print("❌ No domains found in cookies.json!")
            return
        
        print(f"Available domains with cookies ({len(available_domains)}):")
        for i, domain in enumerate(available_domains, 1):
            print(f"  {i}. {domain}")
        print()
        
    except Exception as e:
        print(f"❌ Error reading cookies.json: {e}")
        return
    
    # Get thread URL from user
    print("="*70)
    thread_url = input("Enter thread URL: ").strip()
    if not thread_url:
        print("❌ URL required!")
        return
    
    # Extract domain from URL
    domain = get_domain_from_url(thread_url)
    print(f"\nDetected domain: {domain}")
    
    # Load cookies and patterns for this domain
    domain_data = load_cookies_for_domain(domain)
    
    if not domain_data:
        print(f"❌ No cookies found for domain: {domain}")
        print(f"\nAvailable domains: {', '.join(available_domains)}")
        print(f"\nPlease run: python get_cookies.py")
        print(f"And add cookies for {domain}")
        return
    
    cookie_string = domain_data['cookie_string']
    patterns = domain_data['patterns']
    
    print(f"✓ Loaded cookies for {domain}")
    if patterns:
        print(f"✓ Loaded site-specific patterns (version {patterns.get('version', 'unknown')})")
    
    # Extract base URL
    parsed = urlparse(thread_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Initialize scraper with patterns
    scraper = XenforoScraper(
        base_url=base_url,
        delay=1.5,
        patterns=patterns
    )
    
    # Load cookies into session from cookies.json
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        domain_cookies = cookies_data.get('domains', {}).get(domain, {})
        cookie_dict = domain_cookies.get('dict', {})
        
        # Add cookies to session's cookie jar
        for name, value in cookie_dict.items():
            scraper.session.cookies.set(name, value, domain=domain)
        
    except Exception as e:
        print(f"⚠ Warning: Could not load cookies into session: {e}")
    
    # Ask how many pages (default = all)
    max_pages_input = input("\nHow many pages to scrape? (press Enter for ALL pages): ").strip()
    max_pages = int(max_pages_input) if max_pages_input.isdigit() else None
    
    if max_pages:
        print(f"Will scrape up to {max_pages} pages")
    else:
        print("Will scrape ALL pages")
    
    # Scrape the thread
    print(f"\n{'='*70}")
    print("SCRAPING THREAD")
    print(f"{'='*70}\n")
    
    thread = scraper.scrape_thread(thread_url, max_pages=max_pages)
    
    if thread and len(thread.posts) > 0:
        print(f"\n{'='*70}")
        print("✓ SUCCESS!")
        print(f"{'='*70}")
        print(f"\nThread: {thread.title}")
        print(f"Thread ID: {thread.thread_id}")
        print(f"Total Posts Scraped: {len(thread.posts)}")
        print(f"Total Pages: {thread.total_pages}")
        print(f"Tags: {', '.join(thread.tags) if thread.tags else 'None'}")
        print(f"Prefixes: {', '.join(thread.prefixes) if thread.prefixes else 'None'}")
        
        # Show post statistics
        total_attachments = sum(len(post.attachments) for post in thread.posts)
        total_media_embeds = sum(len(post.media_embeds) for post in thread.posts)
        total_links = sum(len(post.links) for post in thread.posts)
        total_reactions = sum(post.reactions for post in thread.posts if post.reactions)
        unique_authors = len(set(post.author.username for post in thread.posts))
        
        print(f"\nStatistics:")
        print(f"  Total Posts: {len(thread.posts)}")
        print(f"  Unique Authors: {unique_authors}")
        print(f"  Total Images: {total_attachments}")
        print(f"  Total Videos/Embeds: {total_media_embeds}")
        print(f"  Total Links: {total_links}")
        print(f"  Total Reactions: {total_reactions}")
        
        # Export to JSON in organized folder structure
        output_dir = os.path.join('downloads', thread.thread_id)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'thread_{thread.thread_id}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scraper.export_thread_to_dict(thread), f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✓ EXPORTED TO: {output_file}")
        print(f"{'='*70}")
        print(f"\nFile size: {os.path.getsize(output_file) / 1024:.2f} KB")
        
        # Ask if user wants to download media
        download = input("\nDownload media from this thread? (y/n): ").strip().lower()
        if download == 'y':
            print(f"\nRunning: python download_media.py {output_file}\n")
            os.system(f"python download_media.py {output_file}")
        
        # Ask if user wants to scrape another thread
        another = input("\nScrape another thread? (y/n): ").strip().lower()
        if another == 'y':
            main()
            
    else:
        print("\n❌ Failed to scrape thread!")
        print("\nPossible issues:")
        print("  1. Cookies may have expired - run: python get_cookies.py")
        print("  2. Invalid thread URL")
        print("  3. Network connection issue")
        print("  4. Forum may be blocking requests")
        print("\nYou can test your cookies with:")
        print("  python get_cookies.py → Choose option 4")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
