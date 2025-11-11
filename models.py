"""
Data models for XenForo forum scraper
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class User:
    """Represents a forum user"""
    username: str
    user_id: Optional[str] = None
    profile_url: Optional[str] = None
    user_title: Optional[str] = None
    messages: Optional[int] = None
    reaction_score: Optional[int] = None
    points: Optional[int] = None


@dataclass
class Attachment:
    """Represents a file attachment"""
    attachment_id: str
    filename: str
    url: str
    file_type: str  # 'image', 'video', 'document', etc.


@dataclass
class MediaEmbed:
    """Represents an embedded media (iframe, video)"""
    media_type: str  # 'iframe', 'video', 'redgifs', etc.
    embed_url: str
    media_id: Optional[str] = None


@dataclass
class Link:
    """Represents a hyperlink"""
    url: str
    text: str
    link_type: str  # 'external', 'internal', 'image'


@dataclass
class Post:
    """Represents a forum post"""
    post_id: str
    author: User
    content: str  # Plain text content only
    date: str
    reactions: Optional[int] = None
    attachments: List[Attachment] = None
    media_embeds: List[MediaEmbed] = None
    links: List[Link] = None
    quoted_posts: List[str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.media_embeds is None:
            self.media_embeds = []
        if self.links is None:
            self.links = []
        if self.quoted_posts is None:
            self.quoted_posts = []


@dataclass
class Thread:
    """Represents a forum thread"""
    thread_id: str
    title: str
    url: str
    start_date: Optional[str] = None
    tags: List[str] = None
    prefixes: List[str] = None
    posts: List[Post] = None
    social_links: List[Link] = None  # All social media links from posts
    total_pages: int = 1
    current_page: int = 1

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.prefixes is None:
            self.prefixes = []
        if self.posts is None:
            self.posts = []
        if self.social_links is None:
            self.social_links = []
