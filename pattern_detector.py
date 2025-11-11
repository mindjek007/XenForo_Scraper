"""
XenForo Pattern Detector - Automatically detect site-specific HTML structure
Analyzes a sample thread to extract CSS selectors and patterns
"""
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class PatternDetector:
    """Detects XenForo site-specific patterns from sample thread"""
    
    def __init__(self, session: Optional[requests.Session] = None):
        """
        Initialize pattern detector
        
        Args:
            session: Optional requests session with cookies
        """
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def detect_patterns(self, thread_url: str) -> Dict:
        """
        Analyze thread HTML and detect site-specific patterns
        
        Args:
            thread_url: URL of a sample thread to analyze
            
        Returns:
            Dictionary of detected patterns
        """
        print(f"\n🔍 Analyzing thread structure from: {thread_url}")
        
        try:
            response = self.session.get(thread_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            patterns = {
                'version': '1.0',
                'thread_url_sample': thread_url,
                'selectors': {},
                'classes': {},
                'attributes': {}
            }
            
            # Detect post container
            post_containers = self._detect_post_container(soup)
            if post_containers:
                patterns['selectors']['post_container'] = post_containers
            
            # Detect content wrapper
            content_classes = self._detect_content_wrapper(soup)
            if content_classes:
                patterns['classes']['content_wrapper'] = content_classes
            
            # Detect username/author
            author_selectors = self._detect_author_selector(soup)
            if author_selectors:
                patterns['selectors']['author'] = author_selectors
            
            # Detect date/time
            date_selectors = self._detect_date_selector(soup)
            if date_selectors:
                patterns['selectors']['date'] = date_selectors
            
            # Detect reactions
            reaction_selectors = self._detect_reaction_selector(soup)
            if reaction_selectors:
                patterns['selectors']['reactions'] = reaction_selectors
            
            # Detect attachments
            attachment_selectors = self._detect_attachment_selector(soup)
            if attachment_selectors:
                patterns['selectors']['attachments'] = attachment_selectors
            
            # Detect pagination
            pagination_selectors = self._detect_pagination_selector(soup)
            if pagination_selectors:
                patterns['selectors']['pagination'] = pagination_selectors
            
            # Detect post ID attribute
            post_id_attr = self._detect_post_id_attribute(soup)
            if post_id_attr:
                patterns['attributes']['post_id'] = post_id_attr
            
            print(f"✓ Detected {len(patterns['selectors'])} selector patterns")
            return patterns
            
        except Exception as e:
            print(f"❌ Error detecting patterns: {e}")
            return self._get_default_patterns()
    
    def _detect_post_container(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect post container selectors"""
        candidates = []
        
        # Common XenForo post classes
        for class_name in ['message', 'post', 'message--post']:
            elements = soup.find_all(class_=class_name)
            if len(elements) >= 1:  # Should find multiple posts
                candidates.append(f'.{class_name}')
        
        # Check for article tags with specific classes
        articles = soup.find_all('article')
        if articles:
            for article in articles[:3]:
                classes = article.get('class', [])
                if any('message' in c or 'post' in c for c in classes):
                    candidates.append('article.' + '.'.join(classes[:2]))
                    break
        
        return candidates if candidates else None
    
    def _detect_content_wrapper(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect content wrapper classes"""
        candidates = []
        
        for class_name in ['bbWrapper', 'messageText', 'message-body', 'post-content']:
            if soup.find(class_=class_name):
                candidates.append(class_name)
        
        return candidates if candidates else None
    
    def _detect_author_selector(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect author/username selectors"""
        candidates = []
        
        # Look for username classes
        for class_name in ['username', 'author', 'message-name']:
            elem = soup.find(class_=class_name)
            if elem:
                candidates.append(f'.{class_name}')
        
        # Look for data-attributes
        elem = soup.find(attrs={'data-user-id': True})
        if elem and elem.find('a'):
            candidates.append('[data-user-id] a')
        
        return candidates if candidates else None
    
    def _detect_date_selector(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect date/time selectors"""
        candidates = []
        
        # Look for time tags
        time_tags = soup.find_all('time')
        if time_tags:
            candidates.append('time')
            # Check for datetime attribute
            if any(t.get('datetime') for t in time_tags):
                candidates.append('time[datetime]')
        
        # Look for date classes
        for class_name in ['u-dt', 'DateTime', 'message-date']:
            if soup.find(class_=class_name):
                candidates.append(f'.{class_name}')
        
        return candidates if candidates else None
    
    def _detect_reaction_selector(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect reaction/like count selectors"""
        candidates = []
        
        for class_name in ['reactionsBar', 'reactions', 'likes', 'message-reactions']:
            if soup.find(class_=class_name):
                candidates.append(f'.{class_name}')
        
        return candidates if candidates else None
    
    def _detect_attachment_selector(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect attachment selectors"""
        candidates = []
        
        for class_name in ['attachment', 'attachmentList', 'message-attachments']:
            if soup.find(class_=class_name):
                candidates.append(f'.{class_name}')
        
        return candidates if candidates else None
    
    def _detect_pagination_selector(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Detect pagination selectors"""
        candidates = []
        
        for class_name in ['pageNav', 'pagination', 'page-nav']:
            if soup.find(class_=class_name):
                candidates.append(f'.{class_name}')
        
        return candidates if candidates else None
    
    def _detect_post_id_attribute(self, soup: BeautifulSoup) -> Optional[str]:
        """Detect attribute used for post IDs"""
        # Check common attributes
        for attr in ['data-content', 'id', 'data-post-id']:
            elem = soup.find(attrs={attr: True})
            if elem:
                return attr
        
        return None
    
    def _get_default_patterns(self) -> Dict:
        """Return default XenForo patterns as fallback"""
        return {
            'version': '1.0',
            'selectors': {
                'post_container': ['.message'],
                'author': ['.username'],
                'date': ['time[datetime]'],
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


def detect_and_save_patterns(thread_url: str, cookies_dict: Optional[Dict] = None) -> Dict:
    """
    Convenience function to detect patterns with optional cookies
    
    Args:
        thread_url: Sample thread URL to analyze
        cookies_dict: Optional cookie dictionary for authentication
        
    Returns:
        Detected pattern dictionary
    """
    session = requests.Session()
    
    if cookies_dict:
        session.cookies.update(cookies_dict)
    
    detector = PatternDetector(session)
    return detector.detect_patterns(thread_url)
