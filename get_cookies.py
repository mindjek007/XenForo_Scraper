"""
Automated cookie extractor for XenForo scraper - Multi-domain support
Opens Chrome, waits for login, then extracts and saves cookies
"""
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc


def extract_cookies_selenium(forum_url: str, wait_time: int = 60):
    """
    Open Chrome, wait for user to login, then extract cookies
    
    Args:
        forum_url: URL of the forum to login to
        wait_time: How long to wait for user to login (seconds)
    
    Returns:
        Dictionary of cookies with domain info
    """
    print("=" * 70)
    print("Automated Cookie Extractor")
    print("=" * 70)
    print(f"\nOpening Chrome browser to: {forum_url}")
    print(f"You have {wait_time} seconds to login...")
    print()
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Use Chrome profile stored in project folder
    import os
    chrome_profile_dir = os.path.join(os.path.dirname(__file__), 'XenForo')
    chrome_options.add_argument(f'--user-data-dir={chrome_profile_dir}')
    
    # Create directory if it doesn't exist
    os.makedirs(chrome_profile_dir, exist_ok=True)
    
    print(f"ℹ Using Chrome profile: {chrome_profile_dir}")
    
    driver = None
    try:
        # Use webdriver-manager to automatically manage ChromeDriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service as ChromeService
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to forum
        driver.get(forum_url)
        print("✓ Chrome opened successfully!")
        print()
        print("=" * 70)
        print("INSTRUCTIONS:")
        print("=" * 70)
        print("1. Login to the forum in the Chrome window")
        print("2. Navigate around a bit (optional)")
        print("3. Return to this terminal and press ENTER when done")
        print("=" * 70)
        print()
        
        # Wait for user to login
        input("Press ENTER after you've logged in...")
        
        # Extract cookies
        print("\nExtracting cookies...")
        cookies = driver.get_cookies()
        
        # Convert to dictionary and string format
        cookie_dict = {}
        cookie_string_parts = []
        
        for cookie in cookies:
            name = cookie['name']
            value = cookie['value']
            cookie_dict[name] = value
            cookie_string_parts.append(f"{name}={value}")
        
        cookie_string = "; ".join(cookie_string_parts)
        
        # Get domain
        domain = get_domain_from_url(forum_url)
        
        print(f"✓ Extracted {len(cookies)} cookies for {domain}")
        
        return {
            'domain': domain,
            'url': forum_url,
            'dict': cookie_dict,
            'string': cookie_string,
            'list': cookies
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Chrome WebDriver is installed:")
        print("  pip install selenium")
        print("  pip install webdriver-manager")
        return None
        
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


def save_cookies_to_file(cookies_data: dict, filename: str = 'cookies.json'):
    """Save cookies to a JSON file (supports multiple domains)"""
    try:
        # Load existing cookies if file exists
        existing_data = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    # Convert old format to new format if needed
                    if 'domains' not in existing_data:
                        if 'string' in existing_data:
                            # Old single-domain format
                            old_domain = existing_data.get('domain', 'unknown')
                            existing_data = {'domains': {old_domain: existing_data}}
                        else:
                            existing_data = {'domains': {}}
            except:
                existing_data = {'domains': {}}
        else:
            existing_data = {'domains': {}}
        
        # Add or update domain cookies
        domain = cookies_data.get('domain', 'unknown')
        existing_data['domains'][domain] = cookies_data
        
        # Save back to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Cookies for '{domain}' saved to: {filename}")
        print(f"  Total domains in file: {len(existing_data['domains'])}")
        return True
    except Exception as e:
        print(f"❌ Error saving cookies: {e}")
        return False


def load_cookies_from_file(filename: str = 'cookies.json', domain: str = None):
    """Load cookies from a JSON file (supports multiple domains)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle old format (single domain)
        if 'domains' not in data:
            if 'string' in data:
                return data
            return None
        
        # New format (multiple domains)
        if domain:
            # Return specific domain
            return data['domains'].get(domain)
        else:
            # Return all domains
            return data
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None


def test_cookies(cookie_string: str, forum_url: str = None, domain: str = None):
    """
    Test if cookies work with the scraper
    """
    from urllib.parse import urlparse
    
    # Determine base URL and test URL
    if forum_url:
        parsed = urlparse(forum_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        test_url = forum_url
    else:
        base_url = 'https://celebforum.to'
        test_url = 'https://celebforum.to/threads/blows.204932/'
    
    display_domain = domain or get_domain_from_url(base_url)
    
    print("\n" + "="*70)
    print(f"TESTING COOKIES FOR: {display_domain}")
    print("="*70)
    
    try:
        from scraper import XenforoScraper
        
        scraper = XenforoScraper(
            base_url=base_url,
            delay=1.5,
            headers={'Cookie': cookie_string}
        )
        
        print(f"\nTesting connection to {base_url}...")
        print(f"Test URL: {test_url}")
        
        # Try to fetch first page
        soup = scraper._get_page(test_url)
        
        if soup:
            # Try to find any thread content
            posts_section = soup.find('div', class_='block-body')
            if posts_section:
                print(f"\n✓ SUCCESS! Cookies are working for {display_domain}!")
                print(f"  Status: Can access thread content")
                return True
            else:
                print(f"\n⚠ WARNING: Page loaded but content not found")
                print(f"  Cookies may be working, but page structure unexpected")
                return False
        else:
            print(f"\n✗ FAILED: Could not access {display_domain}")
            print(f"  Cookies may have expired or be invalid")
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing cookies: {e}")
        return False


def test_all_cookies(filename: str = 'cookies.json'):
    """
    Test all cookies stored in the file
    """
    print("\n" + "="*70)
    print("TESTING ALL STORED COOKIES")
    print("="*70)
    
    cookies_data = load_cookies_from_file(filename)
    if not cookies_data:
        print("\n❌ No cookies file found or invalid format")
        return
    
    # Handle old format
    if 'domains' not in cookies_data:
        if 'string' in cookies_data:
            domain = cookies_data.get('domain', 'unknown')
            print(f"\n[Old format detected - single domain: {domain}]")
            test_cookies(cookies_data['string'], cookies_data.get('url'), domain)
        return
    
    # Test each domain
    domains = cookies_data.get('domains', {})
    if not domains:
        print("\n❌ No domains found in cookies file")
        return
    
    print(f"\nFound {len(domains)} domain(s) to test:\n")
    results = {}
    
    for domain, data in domains.items():
        cookie_string = data.get('string', '')
        forum_url = data.get('url', '')
        
        if cookie_string:
            success = test_cookies(cookie_string, forum_url, domain)
            results[domain] = success
            time.sleep(2)  # Delay between tests
        else:
            print(f"\n⚠ No cookie string found for {domain}")
            results[domain] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for domain, success in results.items():
        status = "✓ WORKING" if success else "✗ FAILED"
        print(f"  {domain}: {status}")
    print()


def get_cookies_string():
    """Legacy manual instructions"""
    
    print("=" * 70)
    print("Manual Method - Get cookies from browser:")
    print("=" * 70)
    print()
    print("1. Open your XenForo forum in your browser")
    print("2. Press F12 to open Developer Tools")
    print("3. Go to the 'Network' tab")
    print("4. Refresh the page (F5)")
    print("5. Click on the first request in the list")
    print("6. Scroll down to 'Request Headers'")
    print("7. Find 'Cookie:' and copy the entire value")
    print()
    print("Then use it in your scraper like this:")
    print()
    print("=" * 70)
    print("CODE EXAMPLE:")
    print("=" * 70)
    print("""
from scraper import XenforoScraper
import json

# Load cookies for specific domain
with open('cookies.json', 'r') as f:
    data = json.load(f)

domain = 'celebforum.to'
cookie_string = data['domains'][domain]['string']

scraper = XenforoScraper(
    base_url=f'https://{domain}',
    delay=1.5,
    headers={'Cookie': cookie_string}
)

thread = scraper.scrape_thread('YOUR_THREAD_URL')
print(f"Posts: {len(thread.posts)}")
""")
    print("=" * 70)


def parse_cookie_dict(cookie_string: str) -> dict:
    """
    Convert cookie string to dictionary
    
    Args:
        cookie_string: Raw cookie string from browser
        
    Returns:
        Dictionary of cookies
    """
    cookies = {}
    for item in cookie_string.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key] = value
    return cookies


def main():
    """Main function with menu"""
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*15 + "Cookie Manager for Multiple XenForo Sites" + " "*12 + "║")
    print("╚" + "="*68 + "╝\n")
    
    print("Choose an option:")
    print("  1. Add cookies for a new domain (automated with Chrome)")
    print("  2. Manual instructions (copy cookies from browser)")
    print("  3. View saved cookies")
    print("  4. Test all stored cookies")
    print("  5. Test specific domain cookies")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == '1':
        # Automated extraction
        print("\n" + "=" * 70)
        print("ADD COOKIES FOR NEW DOMAIN")
        print("=" * 70)
        
        forum_url = input("\nEnter forum URL: ").strip()
        if not forum_url:
            print("❌ URL required")
            return
        
        # Add protocol if missing
        if not forum_url.startswith('http'):
            forum_url = 'https://' + forum_url
        
        domain = get_domain_from_url(forum_url)
        print(f"\nDomain: {domain}")
        
        print("\nStarting automated extraction...")
        print("Note: Make sure you have 'selenium' installed:")
        print("  pip install selenium webdriver-manager")
        print()
        
        try:
            cookies_data = extract_cookies_selenium(forum_url)
            
            if cookies_data:
                print("\n" + "=" * 70)
                print("COOKIES EXTRACTED SUCCESSFULLY!")
                print("=" * 70)
                print(f"\nDomain: {cookies_data['domain']}")
                print(f"Cookie string length: {len(cookies_data['string'])} characters")
                print(f"Number of cookies: {len(cookies_data['list'])}")
                
                # Ask for sample thread URL to detect patterns
                print("\n" + "=" * 70)
                print("DETECT SITE PATTERNS (OPTIONAL)")
                print("=" * 70)
                print("\nProvide a sample thread URL to auto-detect site structure.")
                print("This helps the scraper work better with site-specific HTML.")
                print()
                thread_url = input("Sample thread URL (or press ENTER to skip): ").strip()
                
                if thread_url:
                    try:
                        from pattern_detector import detect_and_save_patterns
                        print("\n🔍 Analyzing site structure...")
                        patterns = detect_and_save_patterns(thread_url, cookies_data['dict'])
                        cookies_data['patterns'] = patterns
                        print("✓ Site patterns detected and saved")
                    except Exception as e:
                        print(f"⚠ Could not detect patterns: {e}")
                        print("  Scraper will use default XenForo patterns")
                
                # Save to file
                save_cookies_to_file(cookies_data, 'cookies.json')
                
                # Ask if user wants to test
                test_now = input("\nTest cookies now? (y/n): ").strip().lower()
                if test_now == 'y':
                    test_cookies(cookies_data['string'], forum_url, domain)
                
                # Ask if user wants to add more
                add_more = input("\nAdd cookies for another domain? (y/n): ").strip().lower()
                if add_more == 'y':
                    main()
                
        except ImportError:
            print("\n❌ Selenium not installed!")
            print("\nInstall with:")
            print("  pip install selenium webdriver-manager")
            
    elif choice == '2':
        # Manual instructions
        get_cookies_string()
        
    elif choice == '3':
        # View saved cookies
        print("\n" + "=" * 70)
        print("SAVED COOKIES")
        print("=" * 70)
        
        cookies_data = load_cookies_from_file('cookies.json')
        if not cookies_data:
            print("\n❌ No cookies.json found")
            return
        
        # Handle old format
        if 'domains' not in cookies_data:
            if 'string' in cookies_data:
                domain = cookies_data.get('domain', 'unknown')
                print(f"\n[Old format - single domain: {domain}]")
                print(f"  URL: {cookies_data.get('url', 'N/A')}")
                print(f"  Cookies: {len(cookies_data.get('list', []))}")
            return
        
        # Display all domains
        domains = cookies_data.get('domains', {})
        if not domains:
            print("\n❌ No domains found")
            return
        
        print(f"\nTotal domains: {len(domains)}\n")
        for i, (domain, data) in enumerate(domains.items(), 1):
            print(f"{i}. {domain}")
            print(f"   URL: {data.get('url', 'N/A')}")
            print(f"   Cookies: {len(data.get('list', []))}")
            print()
            
    elif choice == '4':
        # Test all cookies
        test_all_cookies('cookies.json')
        
    elif choice == '5':
        # Test specific domain
        print("\n" + "=" * 70)
        print("TEST SPECIFIC DOMAIN")
        print("=" * 70)
        
        cookies_data = load_cookies_from_file('cookies.json')
        if not cookies_data:
            print("\n❌ No cookies.json found")
            return
        
        # Handle old format
        if 'domains' not in cookies_data:
            if 'string' in cookies_data:
                domain = cookies_data.get('domain', 'unknown')
                print(f"\n[Old format - testing {domain}]")
                test_cookies(cookies_data['string'], cookies_data.get('url'), domain)
            return
        
        # Show available domains
        domains = cookies_data.get('domains', {})
        if not domains:
            print("\n❌ No domains found")
            return
        
        print("\nAvailable domains:")
        domain_list = list(domains.keys())
        for i, domain in enumerate(domain_list, 1):
            print(f"  {i}. {domain}")
        
        choice = input("\nEnter domain number or name: ").strip()
        
        # Check if it's a number or domain name
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(domain_list):
                domain = domain_list[idx]
            else:
                print("❌ Invalid choice")
                return
        else:
            domain = choice
        
        if domain in domains:
            data = domains[domain]
            test_cookies(data.get('string', ''), data.get('url'), domain)
        else:
            print(f"❌ Domain '{domain}' not found")
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    main()
