#!/usr/bin/env python3
"""Download media from JSON thread file using appropriate tools."""

import json
import os
import subprocess
import hashlib
from pathlib import Path
from urllib.parse import urlparse

# Domain to tool mapping
TOOLS = {
    "cyberdrop": ["gofile", "cyberdrop", "pixeldrain","jpg6.su", "jpg7.cr"],
    "yt_dlp": ["gofile", "redgifs", "vk.com", "pornhub.com", "pornhub.org", "sendvid"],
    "gallery_dl": ["pixhost", "bunkr", "imgbox", "erome", "reddit.com", "redd.it", "saint"],
    "aria2c": ["streamtape", "phncdn.com", "fap.onl"],
}

def get_domain(url):
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.replace("www.", "")
    except:
        return ""

def url_to_md5(url):
    """Generate MD5 hash of URL."""
    return hashlib.md5(url.encode()).hexdigest()

def file_to_md5(filepath):
    """Generate MD5 hash of file contents."""
    try:
        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except:
        return None

def load_download_history(history_file=".download_history.json"):
    """Load download history from file."""
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"file_md5s": {}, "downloaded_urls": []}
    return {"file_md5s": {}, "downloaded_urls": []}

def save_download_history(history, history_file=".download_history.json"):
    """Save download history to file."""
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"⚠ Warning: Could not save history: {e}")

def clean_url(url):
    """Clean URL: replace .md. with . (for attachment links) and optimize image hosting URLs."""
    url = url.replace(".md.", ".")
    
    domain = get_domain(url).lower()
    
    # Vipr domain optimization: replace /th/ with /i/ for full quality
    if "vipr" in domain:
        url = url.replace("/th/", "/i/")
    
    # Imagetwist domain optimization: replace /th/ with /i/ for full quality
    if "imagetwist" in domain:
        url = url.replace("/th/", "/i/")
    
    return url

def get_tool_for_url(url):
    """Determine which tool to use for URL."""
    domain = get_domain(url).lower()
    
    for tool, domains in TOOLS.items():
        for d in domains:
            if d in domain:
                return tool
    
    # Default to aria2c for direct image links
    if any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"]):
        return "aria2c"
    
    return None

def load_json(filepath):
    """Load thread JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_urls(thread_data, history):
    """Extract all media URLs from thread, excluding already downloaded ones."""
    urls = {
        "cyberdrop": [],
        "yt_dlp": [],
        "gallery_dl": [],
        "aria2c": [],
        "unknown": []
    }
    
    # Domains to grab as external links
    external_link_domains = ["bunkr", "jpg6.su", "jpg7.cr", "gofile", "redgifs"]
    
    # URLs that were already downloaded
    downloaded_urls = set(history.get("downloaded_urls", []))
    
    # Get attachments
    for post in thread_data.get("posts", []):
        for att in post.get("attachments", []):
            url = att.get("url")
            if url:
                url = clean_url(url)
                
                # Skip if already downloaded from this URL
                if url in downloaded_urls:
                    continue
                
                tool = get_tool_for_url(url)
                if tool:
                    urls[tool].append(url)
                else:
                    urls["unknown"].append(url)
        
        # Get media embeds
        for media in post.get("media_embeds", []):
            url = media.get("embed_url")
            if url:
                url = clean_url(url)
                
                # Skip if already downloaded from this URL
                if url in downloaded_urls:
                    continue
                
                tool = get_tool_for_url(url)
                if tool:
                    urls[tool].append(url)
                else:
                    urls["unknown"].append(url)
        
        # Get links (both image_link and external links from supported domains)
        for link in post.get("links", []):
            url = link.get("url")
            link_type = link.get("link_type")
            
            if not url:
                continue
            
            # Include image_link entries
            if link_type == "image_link":
                url = clean_url(url)
                
                # Skip if already downloaded from this URL
                if url in downloaded_urls:
                    continue
                
                tool = get_tool_for_url(url)
                if tool:
                    urls[tool].append(url)
                else:
                    urls["unknown"].append(url)
            
            # Include external links from supported domains
            elif link_type == "external":
                domain = get_domain(url).lower()
                if any(d in domain for d in external_link_domains):
                    # Skip if already downloaded from this URL
                    if url in downloaded_urls:
                        continue
                    
                    tool = get_tool_for_url(url)
                    if tool:
                        urls[tool].append(url)
                    else:
                        urls["unknown"].append(url)
    
    return urls

def download_with_tool(urls, tool, output_dir, history):
    """Download URLs using specified tool and record in history."""
    if not urls:
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📥 Downloading {len(urls)} items with {tool}...")
    
    if tool == "cyberdrop":
        cmd = [
            "cyberdrop-dl",
            "--download",
            "--block-download-sub-folders",
            "--ignore-history",
            "-d", output_dir
        ] + urls
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded with cyberdrop-dl")
            # Record URLs in history
            if "downloaded_urls" not in history:
                history["downloaded_urls"] = []
            for url in urls:
                history["downloaded_urls"].append(url)
        except FileNotFoundError:
            print(f"❌ cyberdrop-dl not installed: pip install cyberdrop-dl")
        except subprocess.CalledProcessError as e:
            print(f"⚠ cyberdrop-dl error: {e}")
            print(f"⚠ cyberdrop-dl error: {e}")
    
    elif tool == "yt_dlp":
        cmd = [
            "yt-dlp",
            "-P", output_dir,
            "-f", "best",
            "--no-warnings"
        ] + urls
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded with yt-dlp")
            if "downloaded_urls" not in history:
                history["downloaded_urls"] = []
            for url in urls:
                history["downloaded_urls"].append(url)
        except FileNotFoundError:
            print(f"❌ yt-dlp not installed: pip install yt-dlp")
        except subprocess.CalledProcessError as e:
            print(f"⚠ yt-dlp error: {e}")
    
    elif tool == "gallery_dl":
        cmd = ["gallery-dl", "-d", output_dir] + urls
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded with gallery-dl")
            if "downloaded_urls" not in history:
                history["downloaded_urls"] = []
            for url in urls:
                history["downloaded_urls"].append(url)
        except FileNotFoundError:
            print(f"❌ gallery-dl not installed: pip install gallery-dl")
        except subprocess.CalledProcessError as e:
            print(f"⚠ gallery-dl error: {e}")
    
    elif tool == "aria2c":
        # Write URLs to file for aria2c (better for many URLs)
        url_file = os.path.join(output_dir, "urls.txt")
        with open(url_file, 'w') as f:
            for url in urls:
                f.write(url + "\n")
        cmd = [
            "aria2c",
            "--quiet",
            "--summary-interval=0",
            "-x", "16",
            "-s", "16",
            "--min-split-size=1M",
            "--max-concurrent-downloads=1",
            "--max-overall-download-limit=0",
            "--max-download-limit=0",
            "-d", output_dir,
            "-i", url_file
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Downloaded with aria2c")
            if "downloaded_urls" not in history:
                history["downloaded_urls"] = []
            for url in urls:
                history["downloaded_urls"].append(url)
        except FileNotFoundError:
            print(f"❌ aria2c not installed: pip install aria2")
        except subprocess.CalledProcessError as e:
            print(f"⚠ aria2c error: {e}")

def main():
    """Main entry point."""
    import sys
    import shutil
    
    if len(sys.argv) < 2:
        print("Usage: python download_media.py <thread.json>")
        print("Example: python download_media.py downloads/344155/thread_344155.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        sys.exit(1)
    
    # Extract thread_id from path
    thread_dir = os.path.dirname(json_file)
    
    # Load download history
    history = load_download_history()
    
    print(f"📂 Loading: {json_file}")
    thread = load_json(json_file)
    
    print(f"📊 Extracting URLs...")
    urls = extract_urls(thread, history)
    
    # Show summary
    total = sum(len(v) for k, v in urls.items() if k != "unknown")
    print(f"✅ Found {total} media URLs")
    
    for tool, items in urls.items():
        if items and tool != "unknown":
            print(f"  • {tool}: {len(items)} URLs")
    
    if urls["unknown"]:
        print(f"  ⚠ Unknown: {len(urls['unknown'])} URLs (will try aria2c)")
    
    # Download to temp subdirs first
    temp_dir = f"{thread_dir}/temp_downloads"
    download_with_tool(urls["cyberdrop"], "cyberdrop", f"{temp_dir}/cyberdrop", history)
    download_with_tool(urls["yt_dlp"], "yt_dlp", f"{temp_dir}/yt_dlp", history)
    download_with_tool(urls["gallery_dl"], "gallery_dl", f"{temp_dir}/gallery_dl", history)
    download_with_tool(urls["aria2c"] + urls["unknown"], "aria2c", f"{temp_dir}/aria2c", history)
    
    # Move all files to thread_dir
    if os.path.exists(temp_dir):
        print(f"\n📋 Moving files to: {thread_dir}")
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "urls.txt":  # Skip url list files
                    continue
                src = os.path.join(root, file)
                dst = os.path.join(thread_dir, file)
                shutil.move(src, dst)
                print(f"  ✓ {file}")
        
        # Remove temp directory and empty folders
        shutil.rmtree(temp_dir)
        print(f"✓ Cleaned up temp folders")
    
    # Scan downloaded files and compute MD5s
    print(f"\n📊 Computing file MD5s...")
    if "file_md5s" not in history:
        history["file_md5s"] = {}
    for file in os.listdir(thread_dir):
        filepath = os.path.join(thread_dir, file)
        if os.path.isfile(filepath) and file not in ["thread_" + thread_dir.split('/')[-1] + ".json", "urls.txt"]:
            file_md5 = file_to_md5(filepath)
            if file_md5:
                history["file_md5s"][file_md5] = file
    
    # Save download history
    save_download_history(history)
    
    print(f"\n✨ Done! All media saved to: {thread_dir}")

if __name__ == "__main__":
    main()
