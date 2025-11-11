"""
JSON Viewer - Check scraped thread data
"""
import json
import os


def view_thread_json(filename):
    """Display summary of scraped thread data"""
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n" + "="*70)
    print("THREAD DATA SUMMARY")
    print("="*70)
    
    print(f"\nThread: {data['title']}")
    print(f"Thread ID: {data['thread_id']}")
    print(f"URL: {data['url']}")
    print(f"Start Date: {data['start_date']}")
    print(f"Tags: {', '.join(data['tags']) if data['tags'] else 'None'}")
    print(f"Prefixes: {', '.join(data['prefixes']) if data['prefixes'] else 'None'}")
    print(f"\nTotal Pages in Thread: {data['total_pages']}")
    print(f"Total Posts Scraped: {data['total_posts']}")
    
    # Post statistics
    posts = data['posts']
    total_attachments = sum(len(p.get('attachments', [])) for p in posts)
    total_media_embeds = sum(len(p.get('media_embeds', [])) for p in posts)
    total_links = sum(len(p.get('links', [])) for p in posts)
    total_reactions = sum(p['reactions'] for p in posts if p['reactions'])
    unique_authors = len(set(p['author']['username'] for p in posts))
    
    print(f"\nStatistics:")
    print(f"  Posts: {len(posts)}")
    print(f"  Unique Authors: {unique_authors}")
    print(f"  Total Attachments (Images): {total_attachments}")
    print(f"  Total Media Embeds (Videos/iframes): {total_media_embeds}")
    print(f"  Total Links: {total_links}")
    print(f"  Total Reactions: {total_reactions}")
    
    # File info
    file_size = os.path.getsize(filename)
    print(f"\nFile Info:")
    print(f"  Filename: {filename}")
    print(f"  Size: {file_size / 1024:.2f} KB")
    
    # Top authors by post count
    author_counts = {}
    for post in posts:
        author = post['author']['username']
        author_counts[author] = author_counts.get(author, 0) + 1
    
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\nTop 5 Authors:")
    for i, (author, count) in enumerate(top_authors, 1):
        print(f"  {i}. {author}: {count} posts")
    
    # Attachment types
    attachment_types = {}
    for post in posts:
        for att in post['attachments']:
            file_type = att['file_type']
            attachment_types[file_type] = attachment_types.get(file_type, 0) + 1
    
    if attachment_types:
        print(f"\nAttachment Types:")
        for file_type, count in attachment_types.items():
            print(f"  {file_type}: {count}")
    
    # Show sample posts
    print(f"\n{'='*70}")
    print("SAMPLE POSTS (First 5)")
    print(f"{'='*70}")
    
    for i, post in enumerate(posts[:5], 1):
        print(f"\n--- Post {i} (ID: {post['post_id']}) ---")
        print(f"Author: {post['author']['username']}")
        print(f"Date: {post['date']}")
        print(f"Reactions: {post['reactions']}")
        print(f"Attachments: {len(post.get('attachments', []))}")
        print(f"Media Embeds: {len(post.get('media_embeds', []))}")
        print(f"Links: {len(post.get('links', []))}")
        
        content = post['content'][:150]
        if len(post['content']) > 150:
            content += "..."
        print(f"Content: {content}")
        
        # Show media embeds
        if post.get('media_embeds'):
            print(f"  Media:")
            for media in post['media_embeds'][:3]:
                print(f"    - {media['media_type']}: {media['embed_url'][:60]}...")
    
    if len(posts) > 5:
        print(f"\n... and {len(posts) - 5} more posts in JSON file")


def main():
    print("\n╔" + "="*68 + "╗")
    print("║" + " "*20 + "JSON Thread Data Viewer" + " "*25 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Find all thread JSON files in downloads directory
    json_files = []
    downloads_dir = 'downloads'
    
    if os.path.exists(downloads_dir):
        for root, dirs, files in os.walk(downloads_dir):
            for filename in files:
                if filename.startswith('thread_') and filename.endswith('.json'):
                    json_files.append(os.path.join(root, filename))
    
    json_files.sort()
    
    if not json_files:
        print("❌ No thread JSON files found in downloads directory")
        print("\nRun 'python quick_start.py' first to scrape threads.")
        return
    
    print("Found thread JSON files:")
    for i, filename in enumerate(json_files, 1):
        size = os.path.getsize(filename) / 1024
        print(f"  {i}. {filename} ({size:.2f} KB)")
    
    if len(json_files) == 1:
        choice = 1
        print(f"\nViewing: {json_files[0]}")
    else:
        print()
        choice_input = input(f"Select file (1-{len(json_files)}): ").strip()
        if not choice_input.isdigit() or int(choice_input) < 1 or int(choice_input) > len(json_files):
            print("❌ Invalid choice")
            return
        choice = int(choice_input)
    
    selected_file = json_files[choice - 1]
    view_thread_json(selected_file)
    
    # Options
    print(f"\n{'='*70}")
    print("Options:")
    print("  1. View another file")
    print("  2. Export post list to TXT")
    print("  3. Exit")
    
    option = input("\nSelect option (1-3): ").strip()
    
    if option == '1':
        main()
    elif option == '2':
        export_to_txt(selected_file)
    else:
        print("\nGoodbye!")


def export_to_txt(json_filename):
    """Export posts to readable TXT file"""
    
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    txt_filename = json_filename.replace('.json', '.txt')
    
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"Thread: {data['title']}\n")
        f.write(f"URL: {data['url']}\n")
        f.write(f"Posts: {data['total_posts']}\n")
        f.write("="*70 + "\n\n")
        
        for i, post in enumerate(data['posts'], 1):
            f.write(f"\n{'='*70}\n")
            f.write(f"Post {i} (ID: {post['post_id']}) by {post['author']['username']}\n")
            f.write(f"Date: {post['date']}\n")
            f.write(f"Reactions: {post['reactions']}\n")
            f.write(f"{'='*70}\n\n")
            f.write(post['content'])
            f.write("\n\n")
            
            if post['attachments']:
                f.write(f"Attachments ({len(post['attachments'])}):\n")
                for att in post['attachments']:
                    f.write(f"  - {att['filename']} ({att['file_type']})\n")
                    f.write(f"    {att['url']}\n")
                f.write("\n")
    
    print(f"\n✓ Exported to: {txt_filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
